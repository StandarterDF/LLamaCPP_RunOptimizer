#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RP-судья через облачный API (DeepSeek Flash/Pro) — облачный аналог `bench\\quality\\rp_judge.py`.

Полностью переиспользует промпт судьи, сборку транскрипта и чтение метрик из локального
`rp_judge.py`, поэтому тексты судьи и парсинг `judge_score.py` идентичны локальным судьям.
Отличие — вместо llama-server запрос идёт в API (ключ в `.env`), причём запросы
отправляются ПАРАЛЛЕЛЬНО (пул потоков), а не по одному.

Запуск (интерпретатор venv):
  .venv\\Scripts\\python.exe bench\\quality\\api_judge.py --all --model deepseek-flash `
      --out bench\\quality\\runs\\rp_judge_dsflash_api --concurrency 10
"""

import argparse
import glob
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))  # bench/quality
ROOT = os.path.dirname(HERE)  # bench
PROJ = os.path.dirname(ROOT)
RUNS = os.path.join(HERE, "runs")
ENV_FILE = os.path.join(PROJ, ".env")
sys.path.insert(0, HERE)

import rp_judge as rj  # noqa: E402  (переиспользуем JUDGE_SYSTEM/build_item/read_metrics)

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

PROVIDERS = {
    "deepseek": ("DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "zai": ("ZAI_API_KEY", "ZAI_BASE_URL", "https://api.z.ai/api/paas/v4"),
}


def load_env(path):
    d = {}
    try:
        with open(path, encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if not ln or ln.startswith("#") or "=" not in ln:
                    continue
                k, v = ln.split("=", 1)
                d[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return d


def api_chat(base, key, model, messages, max_tokens, temperature, thinking):
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if thinking == "disabled":
        body["thinking"] = {"type": "disabled"}
    else:
        body["thinking"] = {"type": "enabled"}
        body["reasoning_effort"] = thinking
    body["temperature"] = temperature
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
        method="POST",
    )
    last = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=900) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(3 * (attempt + 1))
                continue
            raise
    raise last


def main():
    ap = argparse.ArgumentParser(description="RP-судья через облачный API")
    ap.add_argument("dirs", nargs="*", help="каталоги прогонов (с metrics.jsonl)")
    ap.add_argument("--all", action="store_true", help="взять все rp_eval_* под runs/")
    ap.add_argument("--model", default="deepseek-flash")
    ap.add_argument("--provider", default="deepseek", choices=list(PROVIDERS))
    ap.add_argument(
        "--prompts", default=os.path.join("quality", "prompts", "scenarios_rp.json")
    )
    ap.add_argument("--out", default=None)
    ap.add_argument("--batch", type=int, default=3)
    ap.add_argument("--max-tokens", type=int, default=3000)
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--concurrency", type=int, default=10, help="параллельных запросов")
    ap.add_argument(
        "--thinking", default="disabled", choices=["disabled", "low", "high", "max"]
    )
    args = ap.parse_args()

    env = load_env(ENV_FILE)
    key_env, base_env, base_default = PROVIDERS[args.provider]
    key = env.get(key_env)
    base = env.get(base_env, base_default)
    if not key:
        raise SystemExit(f"нет {key_env} в .env")

    prompts_path = args.prompts
    if not os.path.isabs(prompts_path):
        prompts_path = os.path.join(ROOT, args.prompts)
    scenarios = {
        s.get("tag"): s for s in json.load(open(prompts_path, encoding="utf-8"))
    }

    dirs = []
    if args.all:
        for d in sorted(glob.glob(os.path.join(RUNS, "rp_eval_*"))):
            if os.path.isfile(os.path.join(d, "metrics.jsonl")):
                dirs.append(d)
    for d in args.dirs:
        dirs += sorted(glob.glob(d)) if any(c in d for c in "*?[") else [d]

    stamp = time.strftime("%Y%m%d-%H%M%S")
    model_slug = args.model.replace("/", "_")
    out_dir = args.out or os.path.join(RUNS, f"rp_judge_{model_slug}_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    # задачи: (имя прогона, номер части, messages)
    tasks = []
    for run_dir in dirs:
        run_dir = os.path.abspath(run_dir)
        recs = rj.read_metrics(run_dir)
        if not recs:
            print(f"[skip ] {os.path.basename(run_dir)}: нет ответов")
            continue
        name = os.path.basename(run_dir.rstrip("\\/"))
        for bi in range(0, len(recs), args.batch):
            chunk = recs[bi : bi + args.batch]
            body_text = "\n\n".join(rj.build_item(r, scenarios) for r in chunk)
            messages = [
                {"role": "system", "content": rj.JUDGE_SYSTEM},
                {
                    "role": "user",
                    "content": (
                        "Ниже результаты RP-оценки. Разбери каждый ответ "
                        "и найди ошибки/несостыковки.\n\n" + body_text
                    ),
                },
            ]
            tasks.append((name, bi // args.batch + 1, messages))

    print(f"[judge] {args.model} ({args.provider}, thinking={args.thinking})")
    print(
        f"[judge] {len(dirs)} прогонов, {len(tasks)} запросов, "
        f"параллельно {args.concurrency} -> {os.path.relpath(out_dir, ROOT)}"
    )
    t0 = time.time()
    done = 0

    def run_one(messages):
        resp = api_chat(
            base,
            key,
            args.model,
            messages,
            args.max_tokens,
            args.temperature,
            args.thinking,
        )
        return (resp["choices"][0]["message"].get("content") or "").strip()

    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {ex.submit(run_one, m): (name, part) for name, part, m in tasks}
        for fut in as_completed(futs):
            name, part = futs[fut]
            try:
                text = fut.result()
            except Exception as e:  # noqa: BLE001
                text = f"[ОШИБКА СУДЬИ: {e}]"
            with open(
                os.path.join(out_dir, f"{name}__part{part}.txt"), "w", encoding="utf-8"
            ) as f:
                f.write(f"### run: {name} (батч {part})\n\n")
                f.write(rj.sanitize(text))
            done += 1
            print(f"  [{done}/{len(tasks)}] {name} part{part}: {len(text)} симв.")

    print(
        f"\nГотово за {time.time() - t0:.0f}s. Тексты судьи: {os.path.relpath(out_dir, ROOT)}"
    )


if __name__ == "__main__":
    main()
