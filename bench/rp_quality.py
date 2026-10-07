#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Харнесс оценки КАЧЕСТВА генерации (не скорости) для llama-server.

Задача: сравнить параметры семплирования на русских RP-промптах и измерить,
насколько часто модель «сыпется» — чужие алфавиты (CJK/хангыль/тайский/арабский),
BPE-каша, служебные токены, зацикливание.

Как работает:
  1) один раз поднимает llama-server с base_args (как в launch\\...bat);
  2) форматирует промпты шаблоном модели через POST /apply-template;
  3) гоняет сетку sampling-конфигов через нативный POST /completion (он принимает
     ВСЕ сэмплеры: temp/min-p/top-k/top-p/DRY/XTC/typical/top-nsigma/dynatemp);
  4) сохраняет тексты ответов и метрики, печатает сводку по конфигам.

Только стандартная библиотека. Запуск:
  .venv\\Scripts\\python.exe bench\\rp_quality.py bench\\quality\\suites\\suite_sampling1.json
  ... bench\\rp_quality.py <suite.json> --only base_ --seeds 11,22 --limit 4
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_LOCAL = os.path.join(ROOT, "env.local.json")
SANITIZE_KEYS = ("LLAMA_SERVER", "LLAMA_DIR", "MODELS_DIR", "PROJECT_DIR")

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)


# ----------------------------------------------------------------------------
# Пути / санитизация (как в bench.py)
# ----------------------------------------------------------------------------
def _load_env():
    env_map = dict(os.environ)
    local = {}
    try:
        with open(ENV_LOCAL, encoding="utf-8") as f:
            local = json.load(f)
    except Exception:
        local = {}
    env_map.update(local)
    pairs = [(local[k], f"<{k}>") for k in SANITIZE_KEYS if local.get(k)]
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    return env_map, pairs


ENV_MAP, SANITIZE_PAIRS = _load_env()


def expand_str(text):
    return re.sub(
        r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}",
        lambda m: str(ENV_MAP.get(m.group(1), m.group(0))),
        text,
    )


def expand_obj(obj):
    if isinstance(obj, str):
        return expand_str(obj)
    if isinstance(obj, list):
        return [expand_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: expand_obj(v) for k, v in obj.items()}
    return obj


def sanitize(text):
    for src, dst in SANITIZE_PAIRS:
        text = text.replace(src, dst)
    return text


# ----------------------------------------------------------------------------
# Анализ текста: чужие алфавиты, служебные токены, BPE-мусор, зацикливание
# ----------------------------------------------------------------------------
def char_script(ch):
    o = ord(ch)
    if (
        0x0400 <= o <= 0x052F
        or 0x2DE0 <= o <= 0x2DFF
        or 0xA640 <= o <= 0xA69F
        or 0x1C80 <= o <= 0x1C8F
    ):
        return "cyr"
    if (
        0x0041 <= o <= 0x005A
        or 0x0061 <= o <= 0x007A
        or 0x00C0 <= o <= 0x024F
        or 0x1E00 <= o <= 0x1EFF
        or 0x2C60 <= o <= 0x2C7F
        or 0xA720 <= o <= 0xA7FF
    ):
        return "lat"
    if (
        0x4E00 <= o <= 0x9FFF
        or 0x3400 <= o <= 0x4DBF
        or 0xF900 <= o <= 0xFAFF
        or 0x20000 <= o <= 0x2FA1F
    ):
        return "han"
    if 0x3040 <= o <= 0x30FF or 0x31F0 <= o <= 0x31FF:
        return "kana"
    if (
        0xAC00 <= o <= 0xD7AF
        or 0x1100 <= o <= 0x11FF
        or 0x3130 <= o <= 0x318F
        or 0xA960 <= o <= 0xA97F
        or 0xD7B0 <= o <= 0xD7FF
    ):
        return "hangul"
    if 0x0E00 <= o <= 0x0E7F:
        return "thai"
    if (
        0x0600 <= o <= 0x06FF
        or 0x0750 <= o <= 0x077F
        or 0xFB50 <= o <= 0xFDFF
        or 0xFE70 <= o <= 0xFEFF
    ):
        return "arab"
    if 0x0590 <= o <= 0x05FF:
        return "hebr"
    if 0x0900 <= o <= 0x097F:
        return "deva"
    if 0x0530 <= o <= 0x058F:
        return "armn"
    if 0x10A0 <= o <= 0x10FF:
        return "geor"
    if 0x0370 <= o <= 0x03FF:
        return "grek"
    if unicodedata.category(ch).startswith("L"):
        return "other"
    return None


SPECIAL_RE = re.compile(
    r"<\|[^>\n]{1,40}\|>"
    r"|</?(?:start_of_turn|end_of_turn|turn|channel|image|audio|unused\d*|bos|eos|pad|mask)\b[^>]*>"
    r"|\b(?:\[/?INST\]|<<SYS>>|<</SYS>>)"
)
ESCAPE_RE = re.compile(r"\\u[0-9a-fA-F]{4}|\\x[0-9a-fA-F]{2}|<0x[0-9A-Fa-f]{2}>")
LATIN_WORD_RE = re.compile(r"[A-Za-z]+")
# Служебные англ. слова посреди русского текста — верный признак BPE-сбоя
# (например «пальцы и That и онемели»).
EN_STOP = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "that",
    "this",
    "these",
    "those",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "of",
    "to",
    "in",
    "on",
    "at",
    "by",
    "for",
    "with",
    "from",
    "as",
    "it",
    "its",
    "i",
    "you",
    "he",
    "she",
    "they",
    "we",
    "not",
    "no",
    "yes",
    "do",
    "does",
    "did",
    "have",
    "has",
    "had",
    "will",
    "would",
    "can",
    "could",
    "should",
    "if",
    "then",
    "than",
    "so",
    "because",
    "while",
    "when",
    "where",
    "what",
    "who",
    "how",
    "why",
}
# Буквы, которых нет в русском алфавите, но есть в украинском (і/ї/є/ґ).
UKR_LETTERS = set("іїєґІЇЄҐ")


def piece_is_foreign(piece):
    """True, если токен словаря — чужой алфавит или англ. служебное слово."""
    text = piece.replace("\u2581", " ")
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    scripts = {char_script(c) for c in letters}
    if scripts - {"cyr", "lat"}:
        return True
    if "lat" in scripts and "cyr" in scripts:
        return True  # BPE-склейка: буквы двух алфавитов в одном токене
    core = "".join(letters).lower()
    return core in EN_STOP and all(char_script(c) == "lat" for c in letters)


def strip_channels(text):
    """Убирает блоки размышлений, оставляет только видимый ответ.

    Поддерживает два формата: Gemma `<|channel>...<channel|>` и Qwen ` thinking...</think>`.
    Если открывающий маркер остался в промпте (шаблон уже открыл канал/мысль), вывод
    начинается сразу с размышлений и закрывается закрывающим маркером — тогда берём всё
    после него. Так thinking не попадает в «ответ» и не портит метрики.
    """
    text = re.sub(r"<\|channel>.*?<channel\|>", "", text, flags=re.S)
    text = re.sub(r" thinking.*?</think>", "", text, flags=re.S)
    if "<channel|>" in text:
        text = text.rsplit("<channel|>", 1)[-1]
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[-1]
    text = re.sub(r"<\|channel>.*$", "", text, flags=re.S)
    text = re.sub(r" thinking.*$", "", text, flags=re.S)
    return text.strip()


def max_dup_ngram(words, n=8):
    if len(words) < n:
        return 0, 0.0
    grams = {}
    for i in range(len(words) - n + 1):
        g = tuple(words[i : i + n])
        grams[g] = grams.get(g, 0) + 1
    mx = max(grams.values())
    dup = sum(c - 1 for c in grams.values() if c > 1)
    tot = len(words) - n + 1
    return mx, dup / tot


def analyze(text):
    stats = {
        "chars": len(text),
        "cyr": 0,
        "lat": 0,
        "cjk": 0,
        "foreign": 0,
        "fffd": 0,
        "ctrl": 0,
        "marker": 0,
        "special": 0,
        "escape": 0,
        "emoji": 0,
        "latin_words": 0,
        "latin_stop": 0,
        "mixed_words": 0,
        "ukr_letters": 0,
    }
    foreign_by_script = {}
    for ch in text:
        if ch in UKR_LETTERS:
            stats["ukr_letters"] += 1
        s = char_script(ch)
        if s == "cyr":
            stats["cyr"] += 1
        elif s == "lat":
            stats["lat"] += 1
        elif s in ("han", "kana", "hangul"):
            stats["cjk"] += 1
            stats["foreign"] += 1
            foreign_by_script[s] = foreign_by_script.get(s, 0) + 1
        elif s is not None:
            stats["foreign"] += 1
            foreign_by_script[s] = foreign_by_script.get(s, 0) + 1
        else:
            if ch == "\ufffd":
                stats["fffd"] += 1
            elif ch == "\u2581":
                stats["marker"] += 1
            else:
                cat = unicodedata.category(ch)
                if cat in ("Cc", "Cn", "Co", "Cf") and ch not in "\n\r\t":
                    stats["ctrl"] += 1
                elif cat == "So":
                    stats["emoji"] += 1
    stats["special"] = len(SPECIAL_RE.findall(text))
    stats["escape"] = len(ESCAPE_RE.findall(text))
    for w in text.split():
        core = w.strip(".,!?;:()[]{}«»\"'—–-…*_`|")
        if not core:
            continue
        has_lat = any(char_script(c) == "lat" for c in core)
        has_cyr = any(char_script(c) == "cyr" for c in core)
        if has_lat and has_cyr:
            stats["mixed_words"] += 1
        if has_lat and not has_cyr:
            stats["latin_words"] += 1
            if core.lower() in EN_STOP:
                stats["latin_stop"] += 1
    # Англ. вставки ловим по КАЖДОМУ буквенному токену текста — так находятся и склейки
    # вида «That-cold-rain» / «this-mess», которые старый детектор пропускал.
    stats["latin_stop"] = sum(
        1 for w in re.findall(r"[A-Za-z]+", text) if w.lower() in EN_STOP
    )
    letters = stats["cyr"] + stats["lat"] + stats["foreign"]
    stats["letters"] = letters
    stats["foreign_per_1k"] = (
        round(1000.0 * stats["foreign"] / letters, 2) if letters else 0.0
    )
    stats["cjk_per_1k"] = round(1000.0 * stats["cjk"] / letters, 2) if letters else 0.0
    stats["cyr_share"] = round(stats["cyr"] / letters, 3) if letters else 0.0
    stats["junk_per_1k"] = round(
        1000.0
        * (
            stats["fffd"] * 4
            + stats["ctrl"] * 3
            + stats["marker"] * 4
            + stats["special"] * 3
            + stats["escape"] * 3
            + stats["latin_stop"] * 4
            + stats["mixed_words"] * 4
            + stats["ukr_letters"] * 2
        )
        / max(1, len(text)),
        2,
    )
    words = text.split()
    stats["words"] = len(words)
    stats["rep8_max"], stats["rep8_dup"] = max_dup_ngram(words, 8)
    # Лексическое разнообразие (Type-Token Ratio). Слова — только кириллические
    # (латиница у нас обычно артефакт), нижний регистр. Сырой TTR занижается на
    # длинных текстах, поэтому главный для сравнения — ttr_win на первых 150 словах.
    cyr_words = [w.lower() for w in re.findall(r"[а-яё]+", text)]
    wc = len(cyr_words)
    stats["ttr_words"] = wc
    stats["ttr"] = round(len(set(cyr_words)) / wc, 4) if wc else 0.0
    _win = cyr_words[:150]
    stats["ttr_win"] = round(len(set(_win)) / len(_win), 4) if _win else 0.0
    stats["guiraud"] = round(len(set(cyr_words)) / (wc**0.5), 2) if wc else 0.0
    stats["foreign_scripts"] = (
        ",".join(sorted(foreign_by_script)) if foreign_by_script else ""
    )
    stats["clean"] = bool(
        stats["foreign"] == 0
        and stats["special"] == 0
        and stats["escape"] == 0
        and stats["fffd"] == 0
        and stats["marker"] == 0
        and stats["ctrl"] == 0
        and stats["latin_stop"] == 0
        and stats["mixed_words"] == 0
        and stats["ukr_letters"] == 0
        and stats["rep8_dup"] < 0.05
    )
    return stats


# ----------------------------------------------------------------------------
# HTTP
# ----------------------------------------------------------------------------
def http_json(url, payload=None, timeout=300):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST" if data else "GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def http_ok(url, timeout=3):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def gpu_mem_mb():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return int(out.stdout.strip().splitlines()[0])
    except Exception:
        return -1


def kill_proc(proc):
    if proc is None or proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=15)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


# ----------------------------------------------------------------------------
# Генерация
# ----------------------------------------------------------------------------
STOP_WORDS = [
    "<turn|>",
    "<|turn>",
    "<end_of_turn>",
    "<start_of_turn>",
    "<|im_end|>",
    "<|im_start|>",
    "<|endoftext|>",
    "<|eot_id|>",
    "<|end_of_text|>",
]


def default_sampling():
    return {
        "temperature": 0.8,
        "dynatemp_range": 0.0,
        "dynatemp_exponent": 1.0,
        "top_k": 40,
        "top_p": 0.95,
        "min_p": 0.05,
        "top_nsigma": -1.0,
        "typical_p": 1.0,
        "xtc_probability": 0.0,
        "xtc_threshold": 0.1,
        "repeat_last_n": 256,
        "repeat_penalty": 1.0,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
        "dry_multiplier": 0.0,
        "dry_base": 1.75,
        "dry_allowed_length": 2,
        "dry_penalty_last_n": 256,
        "mirostat": 0,
    }


def generate(port, prompt, sampling, n_predict, seed, n_probs=0):
    body = {
        "prompt": prompt,
        "n_predict": n_predict,
        "seed": seed,
        "stream": False,
        "cache_prompt": False,
        "stop": STOP_WORDS,
        "n_keep": 0,
    }
    if n_probs:
        body["n_probs"] = n_probs
    body.update(default_sampling())
    body.update(sampling)
    return http_json(f"http://127.0.0.1:{port}/completion", body, timeout=900)


def apply_template(port, messages):
    r = http_json(
        f"http://127.0.0.1:{port}/apply-template", {"messages": messages}, timeout=60
    )
    return r["prompt"]


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def avg(vals):
    vals = [v for v in vals if isinstance(v, (int, float))]
    return sum(vals) / len(vals) if vals else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("suite", help="JSON-файл набора (см. bench/quality/)")
    ap.add_argument("--only", default=None, help="префикс имени конфига")
    ap.add_argument("--seeds", default=None, help="переопределить seeds, через запятую")
    ap.add_argument("--limit", type=int, default=None, help="взять первые N промптов")
    ap.add_argument("--port", type=int, default=9952)
    ap.add_argument(
        "--out",
        default=None,
        help="папка результатов (по умолчанию quality/runs/<run>)",
    )
    ap.add_argument("--keep-server-log", action="store_true")
    ap.add_argument(
        "--stop-bad",
        type=float,
        default=0.5,
        help="ранний останов конфига, если доля чистых ниже порога (default 0.5)",
    )
    ap.add_argument(
        "--min-samples",
        type=int,
        default=6,
        help="минимум генераций до проверки раннего останова (default 6)",
    )
    args = ap.parse_args()

    suite = expand_obj(json.load(open(args.suite, encoding="utf-8")))
    server_exe = suite["server"]
    model = suite["model"]
    base_args = suite.get("base_args", [])
    prompts_path = suite.get("prompts", "quality/prompts/prompts_ru_rp.json")
    if isinstance(prompts_path, str):
        prompts_path = os.path.join(ROOT, prompts_path)
    prompts = json.load(open(prompts_path, encoding="utf-8"))
    if args.limit:
        prompts = prompts[: args.limit]
    n_predict = suite.get("n_predict", 256)
    seeds = suite.get("seeds", [11, 22])
    if args.seeds:
        seeds = [int(x) for x in args.seeds.split(",")]
    configs = suite["configs"]
    if args.only:
        configs = [c for c in configs if c["name"].startswith(args.only)]

    run_name = suite.get("name") or os.path.splitext(os.path.basename(args.suite))[0]
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = args.out or os.path.join(ROOT, "quality", "runs", f"{run_name}-{stamp}")
    os.makedirs(out_dir, exist_ok=True)
    raw_dir = os.path.join(out_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    metrics_path = os.path.join(out_dir, "metrics.jsonl")

    def _san(o):
        if isinstance(o, str):
            return sanitize(o)
        if isinstance(o, list):
            return [_san(x) for x in o]
        if isinstance(o, dict):
            return {k: _san(v) for k, v in o.items()}
        return o

    with open(os.path.join(out_dir, "suite.used.json"), "w", encoding="utf-8") as f:
        json.dump(_san(suite), f, ensure_ascii=False, indent=2)

    log_path = os.path.join(out_dir, "server.log")
    logf = open(log_path, "w", encoding="utf-8", errors="replace")
    cmd = [
        server_exe,
        "--host",
        "127.0.0.1",
        "--port",
        str(args.port),
        "--no-webui",
        "--model",
        model,
    ] + base_args
    print(f"[server] {sanitize(server_exe)}")
    print(f"[model ] {sanitize(model)}")
    print(f"[out   ] {os.path.relpath(out_dir, ROOT)}")
    t0 = time.time()
    proc = subprocess.Popen(
        cmd, cwd=os.path.dirname(server_exe), stdout=logf, stderr=subprocess.STDOUT
    )
    metrics = []
    try:
        ok = False
        while time.time() - t0 < 600:
            if http_ok(f"http://127.0.0.1:{args.port}/health"):
                ok = True
                break
            if proc.poll() is not None:
                break
            time.sleep(1.0)
        print(f"[load ] {time.time() - t0:.1f}s, VRAM {gpu_mem_mb()} MiB, health={ok}")
        if not ok:
            raise SystemExit("server did not become healthy; см. server.log")

        # Промпты форматируем шаблоном модели; кэш на (config-модификатор, промпт).
        tmpl_cache = {}

        def fmt_prompt(cfg, p, idx):
            key = (cfg.get("append_system"), idx)
            if key not in tmpl_cache:
                msgs = [dict(m) for m in p["messages"]]
                extra = cfg.get("append_system")
                if extra:
                    if msgs and msgs[0].get("role") == "system":
                        msgs[0] = dict(msgs[0])
                        msgs[0]["content"] = (
                            (msgs[0].get("content") or "") + " " + extra
                        )
                    else:
                        msgs.insert(0, {"role": "system", "content": extra})
                tmpl_cache[key] = apply_template(args.port, msgs)
            return tmpl_cache[key]

        print(
            f"[data ] промптов {len(prompts)}, конфигов {len(configs)}, seeds {seeds} "
            f"-> {len(prompts) * len(configs) * len(seeds)} генераций"
        )

        for ci, cfg in enumerate(configs, 1):
            cname = cfg["name"]
            sampling = cfg.get("sampling", {})
            # Дополнительные ограничители генерации: грамматика и logit_bias (файл с id).
            req_sampling = dict(sampling)
            if cfg.get("grammar"):
                req_sampling["grammar"] = cfg["grammar"]
            if cfg.get("logit_bias_file"):
                lb_path = cfg["logit_bias_file"]
                if not os.path.isabs(lb_path):
                    lb_path = os.path.join(ROOT, lb_path)
                with open(lb_path, encoding="utf-8") as lbf:
                    lb_data = json.load(lbf)
                lb_ids = lb_data[cfg.get("logit_bias_ids_key", "ids")]
                lb_bias = cfg.get("logit_bias_bias", -100.0)
                req_sampling["logit_bias"] = {str(i): lb_bias for i in lb_ids}
            print(f"\n[{ci}/{len(configs)}] {cname}  {cfg.get('title', '')}")
            cfg_metrics = []
            stop_early = False
            for pi, p in enumerate(prompts):
                if stop_early:
                    break
                prompt = fmt_prompt(cfg, p, pi)
                for seed in seeds:
                    tag = p.get("tag", "p")
                    t1 = time.time()
                    try:
                        resp = generate(
                            args.port,
                            prompt,
                            req_sampling,
                            p.get("n_predict", n_predict),
                            seed,
                            n_probs=suite.get("n_probs", 0),
                        )
                        raw = resp.get("content") or ""
                        text = strip_channels(raw)
                        tim = resp.get("timings", {}) or {}
                        rec = {
                            "config": cname,
                            "tag": tag,
                            "seed": seed,
                            "wall_s": round(time.time() - t1, 1),
                            "predicted_n": tim.get("predicted_n"),
                            "tg_t_s": round(tim.get("predicted_per_second") or 0, 2),
                            "accept_%": (
                                round(
                                    100.0
                                    * (tim.get("draft_n_accepted") or 0)
                                    / tim["draft_n"],
                                    1,
                                )
                                if tim.get("draft_n")
                                else None
                            ),
                            "sampling": sampling,
                            "text": text,
                            "raw_content": raw,
                        }
                        rec.update(analyze(text))
                        # Опережающий сигнал: какую долю вероятности модель отдаёт
                        # чужим/служебным токенам (нужен n_probs>0 в запросе).
                        probs = resp.get("completion_probabilities")
                        if probs:
                            fm = []
                            for pos in probs:
                                cand = pos.get("probs") or []
                                fm.append(
                                    sum(
                                        c.get("prob", 0.0)
                                        for c in cand
                                        if piece_is_foreign(c.get("token", ""))
                                    )
                                )
                            if fm:
                                rec["foreign_mass_mean"] = round(
                                    100 * sum(fm) / len(fm), 2
                                )
                                rec["foreign_mass_max"] = round(100 * max(fm), 2)
                        rec["text_head"] = text[:300]
                    except Exception as e:
                        rec = {
                            "config": cname,
                            "tag": tag,
                            "seed": seed,
                            "error": f"{type(e).__name__}: {e}",
                        }
                    metrics.append(rec)
                    if "error" not in rec:
                        cfg_metrics.append(rec)
                    with open(metrics_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    fname = f"{cname}__{tag}__s{seed}.txt"
                    with open(os.path.join(raw_dir, fname), "w", encoding="utf-8") as f:
                        f.write(f"### config: {cname}\n### tag: {tag}  seed: {seed}\n")
                        f.write(
                            f"### sampling: {json.dumps(sampling, ensure_ascii=False)}\n\n"
                        )
                        f.write(rec.get("text", ""))
                    # Сырой ответ целиком (с блоком thinking) — нужен для судьи и разбора.
                    if rec.get("raw_content"):
                        full_dir = os.path.join(out_dir, "raw_full")
                        os.makedirs(full_dir, exist_ok=True)
                        with open(
                            os.path.join(full_dir, fname), "w", encoding="utf-8"
                        ) as f:
                            f.write(rec["raw_content"])
                    mark = "OK " if rec.get("clean") else "!! "
                    print(
                        f"  {mark}{tag:<10} s{seed}  fgn/1k {rec.get('foreign_per_1k', 0):>6}"
                        f"  cjk/1k {rec.get('cjk_per_1k', 0):>6}  junk {rec.get('junk_per_1k', 0):>6}"
                        f"  stop {rec.get('latin_stop', 0)} mix {rec.get('mixed_words', 0)}"
                        f" ukr {rec.get('ukr_letters', 0)}  rep8 {rec.get('rep8_dup', 0):>5}"
                        f"  TTR {rec.get('ttr_win', 0):.3f}"
                        f"  f-mass {rec.get('foreign_mass_mean', -1):>6}"
                        f"  {rec.get('chars', 0)}ch"
                    )
                    if len(cfg_metrics) >= args.min_samples:
                        _cl = sum(1 for m in cfg_metrics if m.get("clean")) / len(
                            cfg_metrics
                        )
                        if _cl < args.stop_bad:
                            print(
                                f"  ==> {cname}: EARLY STOP — чисто {_cl:.0%} после "
                                f"{len(cfg_metrics)} генераций (порог {args.stop_bad:.0%})"
                            )
                            stop_early = True
                            break
            rs = [m for m in metrics if m.get("config") == cname and "error" not in m]
            if rs:
                clean = 100.0 * sum(1 for m in rs if m.get("clean")) / len(rs)
                print(
                    f"  ==> {cname}: Чисто {clean:.0f}% (N={len(rs)}) | "
                    f"EN-стоп {avg([m.get('latin_stop') for m in rs]):.2f} | "
                    f"Смеш {avg([m.get('mixed_words') for m in rs]):.2f} | "
                    f"Junk {avg([m.get('junk_per_1k') for m in rs]):.2f} | "
                    f"TG {avg([m.get('tg_t_s') for m in rs]):.1f} t/s"
                )
    finally:
        kill_proc(proc)
        logf.close()
        try:
            txt = open(log_path, encoding="utf-8", errors="replace").read()
            open(log_path, "w", encoding="utf-8").write(sanitize(txt))
        except Exception:
            pass

    # ---- сводка ----
    lines = [
        "| Конфиг | Чисто | Чужой/1k | CJK/1k | EN-стоп | Смеш | UKR | Junk/1k | F-масса % | rep8 | TTR150 | Giraud | Cyr % | TG t/s |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cfg in configs:
        rs = [m for m in metrics if m.get("config") == cfg["name"] and "error" not in m]
        if not rs:
            continue
        clean = 100.0 * sum(1 for m in rs if m.get("clean")) / len(rs)
        lines.append(
            "| {n} | {c:.0f}% | {f:.2f} | {j:.2f} | {s:.2f} | {x:.2f} | {u:.2f} | {k:.2f} | {fm:.2f} | {r:.3f} | {tw:.3f} | {gr:.1f} | {y:.1f} | {t:.1f} |".format(
                n=cfg["name"],
                c=clean,
                f=avg([m.get("foreign_per_1k") for m in rs]),
                j=avg([m.get("cjk_per_1k") for m in rs]),
                s=avg([m.get("latin_stop") for m in rs]),
                x=avg([m.get("mixed_words") for m in rs]),
                u=avg([m.get("ukr_letters") for m in rs]),
                k=avg([m.get("junk_per_1k") for m in rs]),
                fm=avg([m.get("foreign_mass_mean") for m in rs]),
                r=avg([m.get("rep8_dup") for m in rs]),
                tw=avg([m.get("ttr_win") for m in rs]),
                gr=avg([m.get("guiraud") for m in rs]),
                y=100 * avg([m.get("cyr_share") for m in rs]),
                t=avg([m.get("tg_t_s") for m in rs]),
            )
        )
    summary = "\n".join(lines)
    print("\n" + summary)
    with open(os.path.join(out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write(summary + "\n")
    print(f"\nМетрики: {os.path.relpath(metrics_path, ROOT)}")
    print(f"Ответы : {os.path.relpath(raw_dir, ROOT)}")


if __name__ == "__main__":
    main()
