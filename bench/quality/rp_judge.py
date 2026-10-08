#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RP-судья: прогоняет результаты RP-оценки через локальную модель-судью.

Зачем: агент-ревьюер тратит много токенов, читая десятки транскриптов. Методика —
сначала отдаём все результаты локальной модели-судье (по умолчанию базовой
`gemma-4-26B-A4B-it-UD-IQ3_XXS`), она ищет ошибки и несостыковки и пишет обычный
текст; агент анализирует уже этот текст, а сырые транскрипты читает сам только
при дополнительных вопросах.

Что делает:
  1) проверяет свободную VRAM (иначе судья уедет на CPU);
  2) поднимает llama-server с моделью-судьёй;
  3) на каждый каталог прогонов (metrics.jsonl) собирает транскрипты
     (карточка + история + ответ модели + скрытые размышления) и делает один запрос;
  4) сохраняет текст судьи.

Запуск (интерпретатором venv):
  .venv\\Scripts\\python.exe bench\\quality\\rp_judge.py bench\\quality\\runs\\rp_eval_dtv2_nothink-*
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))  # bench/quality
ROOT = os.path.dirname(HERE)  # bench
ENV_LOCAL = os.path.join(ROOT, "env.local.json")
SANITIZE_KEYS = ("LLAMA_SERVER", "LLAMA_DIR", "MODELS_DIR", "PROJECT_DIR")

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

DEFAULT_JUDGE_MODEL = (
    "${MODELS_DIR}/unsloth/gemma-4-26B-A4B-it-GGUF/gemma-4-26B-A4B-it-UD-IQ3_XXS.gguf"
)
STOP_WORDS = ["<turn|>", "<|turn>", "<end_of_turn>", "<start_of_turn>"]

JUDGE_SYSTEM = (
    "Ты — строгий рецензент ролевой игры (RP). Тебе дают карточку персонажа, "
    "уже сыгранную историю и ответ оцениваемой модели. Твоя задача — найти ОШИБКИ и "
    "НЕСОСТЫКОВКИ, а не хвалить.\n"
    "По каждому ответу проверь и, если есть проблема, приведи КОНКРЕТНУЮ цитату:\n"
    "1) логические ошибки и несостыковки, бессмыслица;\n"
    "2) факты из истории, которые модель забыла или исказила (имена, числа, детали, обещания);\n"
    "3) потеря характера и голоса (стала вежливым ассистентом, сменила манеру речи, POV);\n"
    "4) нарушение правил карточки (формат, длина, запреты вроде «не называть имя»);\n"
    "5) пассивность — не движет сцену, просто соглашается или повторяет вопрос игрока;\n"
    "6) языковые артефакты — английские вставки, склеенные слова из двух алфавитов, чужие алфавиты;\n"
    "7) повторы и шаблонность.\n"
    "Формат ответа строго такой:\n"
    "=== <сцена> / <режим> / сид <N> ===\n"
    "Проблемы: <нумерованный список с цитатами; если чисто — так и напиши>\n"
    "Оценки 1-5 (ум, память, персонаж, инструкция, инициатива, русский, проза, повторы): ...\n"
    "Итог: <одна строка>\n"
    "После всех — короткий общий вывод по этому режиму.\n"
    "Важно: раздел [СКРЫТЫЕ РАЗМЫШЛЕНИЯ] — это reasoning модели (обычно по-английски); "
    "его язык НЕ считай языковым артефактом самого ответа.\n"
    "Если видимый ответ начинается с английского плана, а ниже идёт реплика персонажа "
    "по-русски без закрывающей метки размышлений — это утёкший канал мышления (баг шаблона "
    "или конфига): отметь это ОДИН РАЗ как проблему конфига и оценивай саму русскую реплику.\n"
    "Пиши по-русски, кратко, без воды. Не придумывай проблем, которых нет."
)

JUDGE_SYSTEM_EN = (
    "You are a strict roleplay (RP) reviewer. You are given a character card, the "
    "roleplay history played so far, and one response from the model under evaluation. "
    "Your job is to find MISTAKES and INCONSISTENCIES, not to praise.\n"
    "For each response, check and, if there is a problem, quote a SPECIFIC excerpt:\n"
    "1) logical errors and inconsistencies, nonsense;\n"
    "2) facts from the history the model forgot or distorted (names, numbers, details, promises);\n"
    "3) loss of character and voice (turned into a polite assistant, changed speech style, POV);\n"
    "4) violation of the card's rules (format, length, prohibitions such as 'never say the name');\n"
    "5) passivity — does not move the scene, just agrees or repeats the player's question;\n"
    "6) language artifacts — Cyrillic insertions, words gluing two alphabets, foreign scripts, "
    "meta-commentary, self-corrections;\n"
    "7) repetition and template-like writing.\n"
    "Answer format must be exactly:\n"
    "=== <scenario> / <mode> / seed <N> ===\n"
    "Problems: <numbered list with quotes; if clean, say so>\n"
    "Scores 1-5 (intelligence, memory, character, instruction, initiative, english, prose, repetition): ...\n"
    "Verdict: <one line>\n"
    "After all — a short overall conclusion for this mode.\n"
    "Important: the [HIDDEN REASONING] section is the model's reasoning (usually in English); "
    "do NOT count its language as an artifact of the visible answer.\n"
    "If the visible answer starts with an English plan and below it there is a character "
    "line in English without a closing reasoning marker — that is a leaked thinking channel "
    "(template/config bug): flag it ONCE as a config problem and judge the character line itself.\n"
    "Write in English, concise, no filler. Do not invent problems that are not there."
)


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


def http_json(url, payload=None, timeout=1800):
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


def gpu_mem():
    try:
        out = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        used, total = [int(x) for x in out.stdout.strip().splitlines()[0].split(",")]
        return used, total
    except Exception:
        return -1, -1


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


ROLE_LABEL = {"system": "КАРТОЧКА ПЕРСОНАЖА", "user": "ИГРОК", "assistant": "ПЕРСОНАЖ"}
ROLE_LABEL_EN = {"system": "CHARACTER CARD", "user": "PLAYER", "assistant": "CHARACTER"}


def build_item(rec, scenarios, lang="ru"):
    labels = ROLE_LABEL_EN if lang == "en" else ROLE_LABEL
    sc = scenarios.get(rec.get("tag"), {})
    if lang == "en":
        parts = [
            f"### Scenario: {rec.get('tag')} | mode: {rec.get('config')} | seed: {rec.get('seed')}"
        ]
    else:
        parts = [
            f"### Сцена: {rec.get('tag')} | режим: {rec.get('config')} | сид: {rec.get('seed')}"
        ]
    for m in sc.get("messages", []):
        parts.append(f"[{labels.get(m['role'], m['role'])}] {m['content']}")
    ans_label = (
        "[MODEL RESPONSE UNDER REVIEW]"
        if lang == "en"
        else "[ОТВЕТ ОЦЕНИВАЕМОЙ МОДЕЛИ]"
    )
    parts.append(ans_label + "\n" + (rec.get("text") or ""))
    raw = rec.get("raw_content") or ""
    if raw.strip() and raw.strip() != (rec.get("text") or "").strip():
        hid = (
            "[HIDDEN REASONING (thinking)]"
            if lang == "en"
            else "[СКРЫТЫЕ РАЗМЫШЛЕНИЯ МОДЕЛИ (thinking)]"
        )
        parts.append(hid + "\n" + raw)
    return "\n\n".join(parts)


def read_metrics(run_dir):
    path = os.path.join(run_dir, "metrics.jsonl")
    if not os.path.isfile(path):
        return []  # прогон не состоялся (напр. модель недоступна) — судье нечего читать
    recs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if "error" in r:
                continue
            if not (r.get("text") or "").strip():
                continue  # пустой ответ (напр. незакрытый thinking) — судье нечего оценивать
            recs.append(r)
    return recs


def sample(recs, mode):
    """Собирает блок для судьи. mode: 'model' (модель+режим), 'all' (всё в один)."""
    if mode == "model":
        return recs
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+", help="каталоги прогонов (с metrics.jsonl)")
    ap.add_argument("--port", type=int, default=9953)
    ap.add_argument("--model", default=DEFAULT_JUDGE_MODEL)
    ap.add_argument(
        "--prompts", default="quality/prompts/scenarios_rp.json", help="файл сценариев"
    )
    ap.add_argument("--out", default=None, help="каталог для текстов судьи")
    ap.add_argument(
        "--batch", type=int, default=6, help="сколько ответов в одном запросе"
    )
    ap.add_argument("--n-predict", type=int, default=3000)
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--min-free-mb", type=int, default=12000)
    ap.add_argument(
        "--template",
        default="${LLAMA_DIR}/gemma4.jinja",
        help="jinja-шаблон; 'none' — брать встроенный из модели",
    )
    ap.add_argument("--spec", action="store_true", help="включить MTP-спекуляцию")
    ap.add_argument("--reasoning", choices=["on", "off"], default="off")
    ap.add_argument("--reasoning-budget", type=int, default=8192)
    ap.add_argument("--ctx", type=int, default=32768)
    ap.add_argument("--keep-server-log", action="store_true")
    ap.add_argument(
        "--lang", choices=["ru", "en"], default="ru", help="язык судейства и сценариев"
    )
    ap.add_argument(
        "--router-url",
        default=None,
        help="URL запущенного роутера (напр. http://127.0.0.1:9931) — не поднимать свой сервер",
    )
    ap.add_argument(
        "--router-model",
        default=None,
        help="id модели-судьи в роутере (напр. gemma4-26a4b-base-nothink)",
    )
    args = ap.parse_args()

    use_router = bool(args.router_url)
    judge_system = JUDGE_SYSTEM_EN if args.lang == "en" else JUDGE_SYSTEM
    model = expand_str(args.model)
    if use_router:
        from urllib.parse import urlparse

        args.port = urlparse(args.router_url).port or args.port
        model = args.router_model or args.model
    prompts_path = args.prompts
    if not os.path.isabs(prompts_path):
        prompts_path = os.path.join(ROOT, prompts_path)
    scenarios = {
        s.get("tag"): s for s in json.load(open(prompts_path, encoding="utf-8"))
    }

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = args.out or os.path.join(ROOT, "quality", "runs", f"rp_judge-{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    # 1) VRAM (в router-режиме GPU уже держит роутер — проверку пропускаем)
    if use_router:
        print(f"[router] {args.router_url}  judge={model}  lang={args.lang}")
    else:
        used, total = gpu_mem()
        free = (total - used) if used >= 0 else -1
        print(f"[vram ] used {used} / {total} MiB, free {free} MiB")
        if 0 <= free < args.min_free_mb:
            raise SystemExit(
                f"мало свободной VRAM ({free} MiB < {args.min_free_mb}); "
                "остановите другие процессы с видеопамятью"
            )

    server_exe = expand_str(
        "${PROJECT_DIR}/downloads/llama-b11382-cu124/llama-server.exe"
    )
    base = [
        "--fit",
        "on",
        "-fa",
        "on",
        "--load-mode",
        "none",
        "-t",
        "14",
        "-tb",
        "14",
        "-np",
        "1",
        "-c",
        str(args.ctx),
        "-ctk",
        "q4_0",
        "-ctv",
        "q4_0",
        "--jinja",
    ]
    if args.template and args.template.lower() != "none":
        base += ["--chat-template-file", args.template]
    if args.spec:
        base += [
            "--spec-type",
            "draft-mtp",
            "--spec-draft-n-max",
            "5",
            "--spec-draft-n-min",
            "1",
            "--spec-draft-p-min",
            "0.75",
        ]
    if args.reasoning == "off":
        base += ["--reasoning", "off", "--reasoning-budget", "0"]
    else:
        base += ["--reasoning", "on", "--reasoning-budget", str(args.reasoning_budget)]
    base_args = expand_obj(base)
    log_path = os.path.join(out_dir, "judge_server.log")
    logf = open(log_path, "w", encoding="utf-8", errors="replace")
    if use_router:
        proc = None
        print(f"[judge] {model} (router, lang={args.lang})")
    else:
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
        print(f"[judge] {sanitize(model)}")
        proc = subprocess.Popen(
            cmd, cwd=os.path.dirname(server_exe), stdout=logf, stderr=subprocess.STDOUT
        )
    results = []
    try:
        t0 = time.time()
        ok = False
        while time.time() - t0 < 600:
            if http_ok(f"http://127.0.0.1:{args.port}/health"):
                ok = True
                break
            if proc is not None and proc.poll() is not None:
                break
            time.sleep(1.0)
        u, t = gpu_mem()
        print(f"[judge] load {time.time() - t0:.1f}s, VRAM {u}/{t} MiB, health={ok}")
        if not ok:
            raise SystemExit("судья не поднялась; см. judge_server.log")

        for run_dir in args.dirs:
            run_dir = os.path.abspath(run_dir)
            if not os.path.isdir(run_dir):
                print(f"[skip ] нет каталога {run_dir}")
                continue
            recs = read_metrics(run_dir)
            name = os.path.basename(run_dir.rstrip("\\/"))
            print(f"\n[judge] {name}: {len(recs)} ответов, батч {args.batch}")
            for bi in range(0, len(recs), args.batch):
                chunk = recs[bi : bi + args.batch]
                body_text = "\n\n".join(
                    build_item(r, scenarios, args.lang) for r in chunk
                )
                if args.lang == "en":
                    user_msg = (
                        "Below are the RP evaluation results. Review each response "
                        "and find errors/inconsistencies.\n\n" + body_text
                    )
                else:
                    user_msg = (
                        "Ниже результаты RP-оценки. Разбери каждый ответ "
                        "и найди ошибки/несостыковки.\n\n" + body_text
                    )
                tmpl_payload = {
                    "messages": [
                        {"role": "system", "content": judge_system},
                        {"role": "user", "content": user_msg},
                    ]
                }
                if use_router:
                    tmpl_payload["model"] = model
                prompt = http_json(
                    f"http://127.0.0.1:{args.port}/apply-template",
                    tmpl_payload,
                    timeout=120,
                )["prompt"]
                t1 = time.time()
                comp_payload = {
                    "prompt": prompt,
                    "n_predict": args.n_predict,
                    "temperature": args.temperature,
                    "top_k": 40,
                    "top_p": 0.95,
                    "min_p": 0.05,
                    "repeat_penalty": 1.0,
                    "cache_prompt": False,
                    "stop": STOP_WORDS,
                    "stream": False,
                }
                if use_router:
                    comp_payload["model"] = model
                resp = http_json(
                    f"http://127.0.0.1:{args.port}/completion",
                    comp_payload,
                    timeout=1800,
                )
                text = (resp.get("content") or "").strip()
                part = f"{name}__part{bi // args.batch + 1}.txt"
                with open(os.path.join(out_dir, part), "w", encoding="utf-8") as f:
                    f.write(f"### run: {name} (батч {bi // args.batch + 1})\n\n")
                    f.write(sanitize(text))
                results.append((name, bi // args.batch + 1, text))
                print(
                    f"  part {bi // args.batch + 1}: {len(text)} символов, {time.time() - t1:.0f}s"
                )
    finally:
        kill_proc(proc)
        logf.close()
        try:
            txt = open(log_path, encoding="utf-8", errors="replace").read()
            open(log_path, "w", encoding="utf-8").write(sanitize(txt))
        except Exception:
            pass

    print(f"\nТексты судьи: {os.path.relpath(out_dir, ROOT)}")


if __name__ == "__main__":
    main()
