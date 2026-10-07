#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Практический сценарий: многоходовой чат и переиспользование кэша промпта.

Проверяет, сколько токенов реально пересчитывается на 2-м и 3-м запросе с общим префиксом
(cache_prompt=true) и сколько времени это занимает, в сравнении с полным пересчётом.

Запуск:
  .venv\\Scripts\\python.exe bench\\usecase_cache.py [--cache-reuse N] [--no-cache-reuse]
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(ROOT, "runs", "usecase_cache")
os.makedirs(RUNS, exist_ok=True)
SERVER = r"<папка llama.cpp>\llama-server.exe"
MODEL = r"<папка моделей>\ukisai\Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF\Swift-1.5-Qwen3.8-27B-GSQ-RCO-IQ2_S-mtp.gguf"
PORT = 9977

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SYSTEM = (
    "You are a careful assistant. Follow these rules: answer briefly, use Markdown, "
    "never invent facts, and always end with the word DONE. "
    "Additional context for tone: keep the language formal. "
) * 200  # длинный системный префикс (~несколько тысяч токенов)


def post(url, payload, timeout=600):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def get_ok(url):
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def ask(messages, n=64, cache=True):
    t0 = time.time()
    resp = post(
        f"http://127.0.0.1:{PORT}/v1/chat/completions",
        {
            "messages": messages,
            "max_tokens": n,
            "temperature": 1.0,
            "top_p": 0.95,
            "top_k": 20,
            "min_p": 0.0,
            "seed": 7,
            "cache_prompt": cache,
        },
    )
    dt = time.time() - t0
    t = resp.get("timings", {}) or {}
    msg = resp["choices"][0]["message"]
    return {
        "wall_s": round(dt, 2),
        "prompt_n_eval": t.get("prompt_n"),
        "pp_t_s": t.get("prompt_per_second"),
        "gen_n": t.get("predicted_n"),
        "tg_t_s": t.get("predicted_per_second"),
        "usage": resp.get("usage"),
        "answer_head": (msg.get("content") or "")[:80],
        "message": msg,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-reuse", type=int, default=0)
    ap.add_argument("--no-cache-reuse", action="store_true")
    ap.add_argument(
        "--no-cache-prompt", action="store_true", help="слать cache_prompt=false"
    )
    a = ap.parse_args()

    args = [
        SERVER,
        "--host",
        "127.0.0.1",
        "--port",
        str(PORT),
        "--no-webui",
        "-m",
        MODEL,
        "-np",
        "1",
        "-c",
        "81920",
        "-fa",
        "on",
        "--fit",
        "on",
        "-ctk",
        "q4_0",
        "-ctv",
        "q4_0",
        "--no-mmap",
        "--spec-type",
        "draft-mtp",
        "--spec-draft-n-max",
        "4",
        "--spec-draft-n-min",
        "1",
        "--spec-draft-p-min",
        "0.5",
    ]
    if not a.no_cache_reuse:
        args += ["--cache-reuse", str(a.cache_reuse)]
    tag = "noreuse" if a.no_cache_reuse else f"reuse{a.cache_reuse}"
    if a.no_cache_prompt:
        tag += "_nocacheprompt"
    log = open(
        os.path.join(RUNS, f"usecase_cache_{tag}.log"),
        "w",
        encoding="utf-8",
        errors="replace",
    )
    proc = subprocess.Popen(
        args, cwd=os.path.dirname(SERVER), stdout=log, stderr=subprocess.STDOUT
    )
    try:
        t0 = time.time()
        while time.time() - t0 < 300 and not get_ok(f"http://127.0.0.1:{PORT}/health"):
            if proc.poll() is not None:
                raise RuntimeError("сервер упал")
            time.sleep(1)
        print("сервер готов")

        msgs = [
            {"role": "system", "content": SYSTEM},
            {
                "role": "user",
                "content": "Name the three primary colors in one sentence.",
            },
        ]
        r1 = ask(msgs, n=64, cache=not a.no_cache_prompt)
        print("запрос 1 (первый):", {k: v for k, v in r1.items() if k != "message"})

        msgs2 = msgs + [
            r1["message"],
            {
                "role": "user",
                "content": "Now name the three secondary colors in one sentence.",
            },
        ]
        r2 = ask(msgs2, n=64, cache=not a.no_cache_prompt)
        print(
            "запрос 2 (общий префикс):", {k: v for k, v in r2.items() if k != "message"}
        )

        msgs3 = msgs2 + [
            r2["message"],
            {
                "role": "user",
                "content": "And the three tertiary colors in one sentence.",
            },
        ]
        r3 = ask(msgs3, n=64, cache=not a.no_cache_prompt)
        print(
            "запрос 3 (общий префикс):", {k: v for k, v in r3.items() if k != "message"}
        )

        with open(
            os.path.join(RUNS, f"usecase_cache_result_{tag}.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                {
                    "cache_reuse": (None if a.no_cache_reuse else a.cache_reuse),
                    "no_cache_prompt": a.no_cache_prompt,
                    "r1": {k: v for k, v in r1.items() if k != "message"},
                    "r2": {k: v for k, v in r2.items() if k != "message"},
                    "r3": {k: v for k, v in r3.items() if k != "message"},
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=15)
        except Exception:
            proc.kill()
        log.close()


if __name__ == "__main__":
    main()
