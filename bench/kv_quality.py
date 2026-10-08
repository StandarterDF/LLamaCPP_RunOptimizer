#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Харнесс влияния типа KV-кэша на качество и скорость (NIAH + PPL).

Отвечает на вопрос «сколько качества/контекста даёт квантование KV»:
  * NIAH (needle-in-a-haystack) — кладём в длинный русский контекст уникальный
    «кодовый» факт на заданной глубине и просим его вспомнить. Это прямой тест
    верности KV-кэша: если квант теряет дальние токены, recall падает.
    Глубины 10/50/90 % показывают, ломается ли «середина» (lost in the middle).
  * PPL (llama-perplexity) — языковая верность на общем корпусе; работает только
    для dense-моделей (на Gemma-4-26B-A4B MoE инструмент врёт, см. why-ru-models.md).
  * Скорость (PP/TG) и VRAM фиксируются на каждом конфиге.

Матрица: модель × тип KV × длина контекста × глубина. Для каждой комбинации
поднимается свой llama-server (порт), запросы идут через /v1/chat/completions.

Только стандартная библиотека. Запуск:
  .venv\\Scripts\\python.exe bench\\kv_quality.py bench\\suites\\kv\\kv_gemma.json
  .venv\\Scripts\\python.exe bench\\kv_quality.py <suite.json> --only-kv q4_0,f16
  .venv\\Scripts\\python.exe bench\\kv_quality.py <suite.json> --dry-run

Артефакты: bench/runs/kv/<run>/  (results.jsonl, server.log, answers/*.txt, ppl_*.txt).
Плейсхолдеры путей — как в bench.py (${MODELS_DIR} и т.п. из bench/env.local.json).
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_LOCAL = os.path.join(ROOT, "env.local.json")
SANITIZE_KEYS = ("LLAMA_SERVER", "LLAMA_DIR", "MODELS_DIR", "PROJECT_DIR")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Тип KV -> аргументы llama-server. Смешанный K/V отдельным ключом.
KV_ARGS = {
    "f16": ["-ctk", "f16", "-ctv", "f16"],
    "q8_0": ["-ctk", "q8_0", "-ctv", "q8_0"],
    "q5_1": ["-ctk", "q5_1", "-ctv", "q5_1"],
    "q4_1": ["-ctk", "q4_1", "-ctv", "q4_1"],
    "q4_0": ["-ctk", "q4_0", "-ctv", "q4_0"],
    "iq4_nl": ["-ctk", "iq4_nl", "-ctv", "iq4_nl"],
    "q8k_q4v": ["-ctk", "q8_0", "-ctv", "q4_0"],
    "q8k_f16v": ["-ctk", "q8_0", "-ctv", "f16"],
}

KV_LABEL = {
    "f16": "f16",
    "q8_0": "q8_0",
    "q5_1": "q5_1",
    "q4_1": "q4_1",
    "q4_0": "q4_0",
    "iq4_nl": "iq4_nl",
    "q8k_q4v": "q8_0 K / q4_0 V",
    "q8k_f16v": "q8_0 K / f16 V",
}


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


# ---------------------------------------------------------------------------
# HTTP / GPU
# ---------------------------------------------------------------------------
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
        proc.wait(timeout=20)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Текст и оценка
# ---------------------------------------------------------------------------
CYR = re.compile(r"[А-Яа-яЁё]")
LAT = re.compile(r"[A-Za-z]")
ALNUM = re.compile(r"[^0-9A-Za-zА-Яа-яЁё]")


def cyr_frac(text):
    c, l = len(CYR.findall(text)), len(LAT.findall(text))
    return round(c / (c + l), 3) if (c + l) else 0.0


def make_code(seed_tag):
    """Детерминированный «кодовый» идентификатор: псевдослово + 4 цифры."""
    h = hashlib.sha256(seed_tag.encode("utf-8")).digest()
    letters = "БВГДЖЗКЛМНПРСТФХЦЧШЩ"
    word = "".join(letters[h[i] % len(letters)] for i in range(5))
    num = 1000 + int.from_bytes(h[5:7], "big") % 9000
    return f"{word}-{num}"


def score_answer(answer, code):
    a = ALNUM.sub("", answer).upper()
    c = ALNUM.sub("", code).upper()
    return 1 if c and c in a else 0


def count_tokens(port, text):
    r = http_json(f"http://127.0.0.1:{port}/tokenize", {"content": text}, timeout=120)
    return len(r.get("tokens") or [])


def load_corpus(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().strip()


def assemble_haystack(port, target_tokens, corpus, salt=0):
    """Сено ~target_tokens: перемешанные предложения корпуса, точная подгонка.

    Возвращает (seq, tokens). Перемешивание детерминировано по salt: у всех типов
    KV при одном salt контекст одинаковый (парное сравнение).
    """
    import random

    units = [s for s in re.split(r"(?<=[.!?])\s+|\n+", corpus) if s.strip()]
    if not units:
        units = [corpus]
    t_corpus = count_tokens(port, "\n".join(units))
    per = max(1.0, t_corpus / len(units))
    rng = random.Random(salt)
    order = units[:]
    rng.shuffle(order)
    need = max(1, int(round(target_tokens / per)))
    seq = [order[i % len(order)] for i in range(need)]
    hay = "\n".join(seq)
    t = count_tokens(port, hay)
    guard = 0
    while t > target_tokens * 1.01 and len(seq) > 1 and guard < 200:
        cut = max(1, int(len(seq) * (t - target_tokens) / t))
        seq = seq[: len(seq) - cut]
        hay = "\n".join(seq)
        t = count_tokens(port, hay)
        guard += 1
    while t < target_tokens * 0.99 and guard < 400:
        add = max(1, int(len(seq) * (target_tokens - t) / max(t, 1)))
        rng.shuffle(order)
        seq += [order[i % len(order)] for i in range(add)]
        hay = "\n".join(seq)
        t = count_tokens(port, hay)
        guard += 1
    return seq, t


def insert_needles(seq, needles):
    """Вставляет иглы [(depth, text), ...] в копию seq (от дальних к ближним)."""
    out = seq[:]
    for depth, text in sorted(needles, key=lambda x: -x[0]):
        idx = max(0, min(len(out), int(len(out) * depth)))
        out.insert(idx, text)
    return out


def gen_chat(port, content, n_predict, seed=1, temperature=0.0):
    body = {
        "messages": [{"role": "user", "content": content}],
        "max_tokens": n_predict,
        "temperature": temperature,
        "top_p": 1.0,
        "top_k": 0,
        "seed": seed,
        "stream": False,
        "cache_prompt": False,
    }
    t0 = time.time()
    resp = http_json(f"http://127.0.0.1:{port}/v1/chat/completions", body, timeout=2400)
    wall = time.time() - t0
    msg = (resp.get("choices") or [{}])[0].get("message") or {}
    content_out = msg.get("content") or ""
    tim = resp.get("timings") or {}
    out = {
        "wall_s": round(wall, 1),
        "prompt_n": tim.get("prompt_n"),
        "pp_t_s": tim.get("prompt_per_second"),
        "predicted_n": tim.get("predicted_n"),
        "tg_t_s": tim.get("predicted_per_second"),
        "content": content_out,
        "cyr_frac": cyr_frac(content_out),
    }
    return out


# ---------------------------------------------------------------------------
# Запуск конфига
# ---------------------------------------------------------------------------
def start_server(server_exe, args, log_path):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logf = open(log_path, "w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(
        [server_exe, "--host", "127.0.0.1", "--port", str(args["port"]), "--no-webui"]
        + args["cli"],
        cwd=os.path.dirname(server_exe),
        stdout=logf,
        stderr=subprocess.STDOUT,
    )
    return proc, logf


def wait_health(port, proc, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if http_ok(f"http://127.0.0.1:{port}/health"):
            return True
        if proc.poll() is not None:
            return False
        time.sleep(1.0)
    return False


def log_digest(path):
    keys = (
        "KV self size",
        "n_ctx",
        "offloaded",
        "fit",
        "error",
        "KV buffer",
        "model buffer",
        "compute buffer",
        "CUDA0",
    )
    out = []
    try:
        for ln in open(path, encoding="utf-8", errors="replace"):
            if any(k.lower() in ln.lower() for k in keys):
                out.append(ln.rstrip())
    except Exception:
        pass
    return [sanitize(x) for x in out[-80:]]


def parse_log_bits(log_path):
    bits = {"kv_self_size": None, "offloaded": False, "n_ctx_line": None}
    try:
        for ln in open(log_path, encoding="utf-8", errors="replace"):
            if "KV self size" in ln:
                bits["kv_self_size"] = ln.strip()
            if "offloaded" in ln.lower() and "layer" in ln.lower():
                bits["offloaded"] = True
            if "n_ctx_slot" in ln:
                bits["n_ctx_line"] = ln.strip()
    except Exception:
        pass
    return bits


def run_config(
    server_exe,
    model_name,
    model_path,
    base_args,
    kv_name,
    ctx,
    depths,
    n_predict,
    corpus,
    out_dir,
    port,
    timeout_load=900,
):
    """Один конфиг = один llama-server; прогон короткого + 3 глубинных NIAH."""
    cfg_dir = os.path.join(out_dir, f"{model_name}__{kv_name}__c{ctx}")
    os.makedirs(cfg_dir, exist_ok=True)
    log_path = os.path.join(cfg_dir, "server.log")
    kv_args = KV_ARGS[kv_name]
    cli = ["--model", model_path, "-np", "1", "-c", str(ctx)] + base_args + kv_args
    rec = {
        "name": f"{model_name}__{kv_name}__c{ctx}",
        "model": model_name,
        "kv": kv_name,
        "ctx_req": ctx,
        "time": datetime.now().isoformat(timespec="seconds"),
        "args": [sanitize(x) for x in cli],
        "load_s": None,
        "vram_before_mb": gpu_mem_mb(),
        "vram_after_load_mb": None,
        "n_ctx_actual": None,
        "props_error": None,
        "error": None,
        "probes": {},
        "log_path": os.path.relpath(log_path, ROOT),
        "log_bits": {},
    }
    proc, logf = start_server(server_exe, {"port": port, "cli": cli}, log_path)
    try:
        t0 = time.time()
        ok = wait_health(port, proc, timeout=timeout_load)
        rec["load_s"] = round(time.time() - t0, 1)
        if not ok:
            rec["error"] = "server did not become healthy"
            return rec
        time.sleep(2.0)
        rec["vram_after_load_mb"] = gpu_mem_mb()
        try:
            props = http_json(f"http://127.0.0.1:{port}/props", timeout=30)
            rec["n_ctx_actual"] = props.get("default_generation_settings", {}).get(
                "n_ctx"
            )
        except Exception as e:
            rec["props_error"] = str(e)
        work_ctx = rec["n_ctx_actual"] or ctx
        target = int(work_ctx * 0.82)
        salt = int.from_bytes(
            hashlib.sha256(f"{model_name}|{ctx}".encode()).digest()[:4], "big"
        )
        # сено строим один раз: короткое и длинное (одинаковое для всех типов KV)
        long_seq, long_tok = assemble_haystack(port, target, corpus, salt=salt)
        short_seq, short_tok = assemble_haystack(
            port, min(2048, max(512, target)), corpus, salt=salt + 1
        )
        md = [0.05, 0.25, 0.5, 0.75, 0.95]
        probes = [("short", short_seq, short_tok, [(0.5, f"{model_name}|{ctx}|short")])]
        for d in depths:
            tag = f"d{int(d * 100)}"
            probes.append((tag, long_seq, long_tok, [(d, f"{model_name}|{ctx}|{tag}")]))
        probes.append(
            (
                "multi",
                long_seq,
                long_tok,
                [(d, f"{model_name}|{ctx}|multi{d}") for d in md],
            )
        )
        for tag, seq, toks, needles_raw in probes:
            try:
                prepared = [
                    (d, f"Секретный код доступа: {make_code(c)}.")
                    for d, c in needles_raw
                ]
                content = "\n".join(insert_needles(seq, prepared))
                if tag == "multi":
                    question = (
                        "В тексте выше упоминались несколько секретных кодов доступа. "
                        "Перечисли их все, каждый с новой строки. "
                        "Если какой-то не помнишь — пропусти."
                    )
                    npred = max(n_predict, 64)
                else:
                    question = (
                        "В тексте выше упоминался секретный код доступа. "
                        "Назови его. Ответь только кодом, без пояснений."
                    )
                    npred = n_predict
                r = gen_chat(port, content + "\n\n" + question, npred)
                r["est_tokens"] = toks
                if tag == "multi":
                    found = {
                        make_code(c): score_answer(r["content"], make_code(c))
                        for _, c in needles_raw
                    }
                    r["codes"] = list(found)
                    r["depths"] = [d for d, _ in needles_raw]
                    r["found"] = found
                    r["score"] = round(sum(found.values()) / len(found), 3)
                    head = f"codes: {list(found)}\ndepths: {r['depths']}\nscore: {r['score']}"
                else:
                    code = make_code(needles_raw[0][1])
                    r["code"] = code
                    r["depth"] = needles_raw[0][0]
                    r["score"] = score_answer(r["content"], code)
                    head = f"code: {code}\ndepth: {r['depth']}\nscore: {r['score']}"
                ans_path = os.path.join(cfg_dir, "answers", f"{tag}.txt")
                os.makedirs(os.path.dirname(ans_path), exist_ok=True)
                with open(ans_path, "w", encoding="utf-8") as af:
                    af.write(f"{head}\nprompt_n: {r['prompt_n']}\n\n{r['content']}\n")
                r["answer_file"] = os.path.relpath(ans_path, ROOT)
                r["content"] = r["content"][:400]
                rec["probes"][tag] = r
            except Exception as e:
                rec["probes"][tag] = {"error": f"{type(e).__name__}: {e}"}
            rec["vram_after_req_mb"] = gpu_mem_mb()
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"
    finally:
        kill_proc(proc)
        logf.close()
        time.sleep(2.0)
        rec["log_bits"] = parse_log_bits(log_path)
        rec["log_digest"] = log_digest(log_path)
    return rec


def run_ppl(server_dir, model_path, kv_name, ctx, corpus_path, cfg_dir):
    """llama-perplexity на том же корпусе; возвращает итоговый PPL."""
    exe = os.path.join(server_dir, "llama-perplexity.exe")
    if not os.path.exists(exe):
        return {"error": "llama-perplexity.exe не найден"}
    kv_args = KV_ARGS[kv_name]
    out_path = os.path.join(cfg_dir, f"ppl_{kv_name}_c{ctx}.txt")
    cmd = [
        exe,
        "-m",
        model_path,
        "-f",
        corpus_path,
        "-c",
        str(ctx),
        "-ngl",
        "99",
        "-fa",
        "on",
    ] + kv_args
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=3600, cwd=server_dir
        )
        txt = (r.stdout or "") + (r.stderr or "")
        with open(out_path, "w", encoding="utf-8", errors="replace") as f:
            f.write(sanitize(txt))
        m = re.findall(r"Final estimate: PPL = ([0-9.]+)", txt)
        ppl = float(m[-1]) if m else None
        return {"ppl": ppl, "out": os.path.relpath(out_path, ROOT)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="KV-кэш: NIAH + PPL матрица")
    ap.add_argument("suite")
    ap.add_argument("--only-model", default=None)
    ap.add_argument("--only-kv", default=None)
    ap.add_argument("--only-ctx", default=None)
    ap.add_argument("--depths", default=None, help="напр. 0.1,0.5,0.9")
    ap.add_argument("--n-predict", type=int, default=None)
    ap.add_argument("--port", type=int, default=9971)
    ap.add_argument("--out", default=None)
    ap.add_argument("--force", action="store_true", help="не пропускать уже сделанное")
    ap.add_argument("--no-ppl", action="store_true")
    ap.add_argument(
        "--ppl-only",
        action="store_true",
        help="только досчитать PPL для уже готовых конфигов (c=512)",
    )
    ap.add_argument(
        "--ppl-refresh",
        action="store_true",
        help="с --ppl-only: пересчитать PPL даже там, где уже есть",
    )
    ap.add_argument(
        "--max-configs",
        type=int,
        default=None,
        help="за один запуск сделать не больше N новых конфигов (щадящий режим)",
    )
    ap.add_argument(
        "--cooldown",
        type=float,
        default=6.0,
        help="пауза между конфигами, с (дать машине остыть)",
    )
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    suite = expand_obj(json.load(open(a.suite, encoding="utf-8")))
    server_exe = suite["server"]
    server_dir = os.path.dirname(server_exe)
    kvs = [
        x.strip() for x in (a.only_kv or ",".join(suite["kvs"])).split(",") if x.strip()
    ]
    depths = (
        [float(x) for x in a.depths.split(",")]
        if a.depths
        else suite.get("depths", [0.1, 0.5, 0.9])
    )
    n_predict = a.n_predict or suite.get("n_predict", 24)
    corpus_path = suite.get("filler")
    if isinstance(corpus_path, str) and not os.path.isabs(corpus_path):
        corpus_path = os.path.join(ROOT, corpus_path)
    corpus = load_corpus(corpus_path)

    models = suite["models"]
    if a.only_model:
        models = [m for m in models if m["name"].startswith(a.only_model)]

    run_name = suite.get("name") or os.path.splitext(os.path.basename(a.suite))[0]
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = a.out or os.path.join(ROOT, "runs", "kv", f"{run_name}-{stamp}")
    results_path = os.path.join(out_dir, "results.jsonl")

    plan = []
    for m in models:
        ctxs = m.get("contexts", suite.get("contexts", [16384, 49152]))
        if a.only_ctx:
            ctxs = [int(x) for x in a.only_ctx.split(",")]
        for kv in kvs:
            for ctx in ctxs:
                plan.append((m, kv, ctx))
    if not a.only_ctx and not a.only_model:
        # «вытянутые» точки: где часть типов KV уже не помещается —
        # добавляем вручную, чтобы измерить длинный контекст на дешёвых KV
        for e in suite.get("extra", []):
            m = next((x for x in models if x["name"] == e["model"]), None)
            if m and e["kv"] in kvs:
                plan.append((m, e["kv"], e["ctx"]))

    if a.dry_run:
        print(f"server : {server_exe}")
        for m, kv, ctx in plan:
            print(f"  {m['name']:22} kv={kv:8} c={ctx:6} {' '.join(KV_ARGS[kv])}")
        return

    os.makedirs(out_dir, exist_ok=True)
    done = set()
    if os.path.exists(results_path) and not a.force:
        for ln in open(results_path, encoding="utf-8"):
            try:
                r = json.loads(ln)
                if not r.get("error"):
                    done.add(r["name"])
            except Exception:
                pass

    if a.ppl_only:
        ppl_done = set()
        recs = [
            json.loads(x) for x in open(results_path, encoding="utf-8") if x.strip()
        ]
        for r in recs:
            if not a.ppl_refresh and (r.get("ppl_c512") or r.get("ppl_c2048")):
                ppl_done.add((r.get("model"), r.get("kv")))
        m_by = {m["name"]: m for m in models}
        changed = False
        for r in recs:
            m = m_by.get(r.get("model"))
            if not m or not m.get("ppl"):
                continue
            key = (r["model"], r["kv"])
            if key in ppl_done:
                continue
            cfg_dir = os.path.join(out_dir, r["name"])
            ppl = run_ppl(server_dir, m["model"], r["kv"], 512, corpus_path, cfg_dir)
            r["ppl_c512"] = ppl
            ppl_done.add(key)
            changed = True
            print(f"PPL {r['model']} {r['kv']}: {ppl.get('ppl')}")
        if changed:
            with open(results_path, "w", encoding="utf-8") as f:
                for r in recs:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print("PPL-проход готов")
        return

    if a.max_configs:
        todo = [p for p in plan if f"{p[0]['name']}__{p[1]}__c{p[2]}" not in done]
        skip = [p for p in plan if f"{p[0]['name']}__{p[1]}__c{p[2]}" in done]
        plan = skip + todo[: a.max_configs]

    print(f"Стенд: {len(plan)} конфигов -> {os.path.relpath(out_dir, ROOT)}")
    idx = 0
    for m, kv, ctx in plan:
        idx += 1
        name = f"{m['name']}__{kv}__c{ctx}"
        if name in done:
            print(f"[{idx}/{len(plan)}] {name}: уже есть — пропуск")
            continue
        print(f"\n[{idx}/{len(plan)}] {name}")
        rec = run_config(
            server_exe,
            m["name"],
            m["model"],
            m.get("base_args", []),
            kv,
            ctx,
            depths,
            n_predict,
            corpus,
            out_dir,
            a.port + (idx % 3),
        )
        if not rec.get("error"):
            for tag, p in rec["probes"].items():
                if isinstance(p, dict) and "score" in p:
                    print(
                        f"   [{tag:5}] recall={p['score']} prompt_n={p.get('prompt_n')} "
                        f"TG={p.get('tg_t_s') and round(p['tg_t_s'], 1)} "
                        f"| {str(p.get('content', ''))[:60]!r}"
                    )
            print(
                f"   VRAM {rec['vram_after_load_mb']} MiB, "
                f"n_ctx={rec['n_ctx_actual']}, load {rec['load_s']}s"
            )
            if rec.get("log_bits", {}).get("offloaded"):
                print("   ВНИМАНИЕ: в логе есть выгрузка слоёв (offloaded)")
            # PPL — только там, где разрешено (dense; MoE врёт) и только на одном
            # контексте (PPL на c=2048 не зависит от -c сервера)
            if m.get("ppl") and not a.no_ppl and kv in KV_ARGS and ctx == 16384:
                cfg_dir = os.path.join(out_dir, f"{m['name']}__{kv}__c{ctx}")
                ppl = run_ppl(server_dir, m["model"], kv, 512, corpus_path, cfg_dir)
                rec["ppl_c512"] = ppl
                print(f"   PPL c512: {ppl.get('ppl')}")
        else:
            print(f"   ОШИБКА: {rec['error']}")
        with open(results_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        time.sleep(a.cooldown)

    print(f"\nРезультаты: {results_path}")


if __name__ == "__main__":
    main()
