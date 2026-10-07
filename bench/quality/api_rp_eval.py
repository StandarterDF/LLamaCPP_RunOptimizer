#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RP-прогон ОБЛАЧНЫХ моделей через OpenAI-совместимый API (DeepSeek, z.ai/GLM)
в формате харнесса. Запросы отправляются ПАРАЛЛЕЛЬНО (пул потоков).

Зачем: локальный `bench\\rp_quality.py` поднимает llama-server и работает только с GGUF.
Этот скрипт делает то же (те же сценарии, те же seeds, RU-safe сэмплинг), но ходит в API и
пишет `metrics.jsonl` + `raw\\` так, что дальше работают штатные
`bench\\quality\\rp_judge.py` и `judge_score.py`.

Режим мышления:
  --thinking disabled|low|high|max   (по умолчанию disabled — сравнимо с локальным nothink)
  Для моделей, которые НЕ умеют отключать thinking (glm-5.3, glm-5.3-flash), в MODELS задан
  режим "low", и каталог прогона получает суффикс _think.

Ключи берутся из `.env` в корне проекта (см. .env.example).

Запуск (интерпретатор venv):
  .venv\\Scripts\\python.exe bench\\quality\\api_rp_eval.py --models dsflash,dsv4pro
  .venv\\Scripts\\python.exe bench\\quality\\api_rp_eval.py --models glm53,glm52,glm47 --concurrency 8
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))  # bench/quality
ROOT = os.path.dirname(HERE)  # bench
PROJ = os.path.dirname(ROOT)  # корень проекта
ENV_FILE = os.path.join(PROJ, ".env")
RUNS = os.path.join(HERE, "runs")

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

# provider -> (env-ключ, env-base-url, base-url по умолчанию)
PROVIDERS = {
    "deepseek": ("DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "zai": ("ZAI_API_KEY", "ZAI_BASE_URL", "https://api.z.ai/api/paas/v4"),
}

# slug -> (id модели, provider, режим thinking: None = взять --thinking)
# "low"/"high"/"max" = thinking неотключаем, используем усилие; "disabled" = отключён.
MODELS = {
    "dsflash": ("deepseek-flash", "deepseek", None),
    "dsv4pro": ("deepseek-v4-pro", "deepseek", None),
    "glm53flash": ("glm-5.3-flash", "zai", "low"),  # thinking неотключаем
    "glm53": ("glm-5.3", "zai", "low"),  # thinking неотключаем
    "glm52": ("glm-5.2", "zai", None),
    "glm51": ("glm-5.1", "zai", None),
    "glm5": ("glm-5", "zai", None),
    "glm47": ("glm-4.7", "zai", None),
    "glm47flashx": ("glm-4.7-flashx", "zai", None),
    "glm46": ("glm-4.6", "zai", None),
    "glm47flash": ("glm-4.7-flash", "zai", None),
    "glm45flash": ("glm-4.5-flash", "zai", None),
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


def api_chat(base, key, model, messages, max_tokens, temperature, top_p, thinking):
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
    # temperature/top_p: в thinking-режиме DeepSeek их игнорирует, в non-thinking применяет.
    body["temperature"] = temperature
    body["top_p"] = top_p
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + key,
        },
        method="POST",
    )
    last = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=900) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:  # ретраим лимиты и временные сбои
            last = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(5 * (attempt + 1))
                continue
            raise
    raise last


def main():
    ap = argparse.ArgumentParser(description="RP-прогон API-моделей в формат харнесса")
    ap.add_argument("--models", required=True, help="slug'и через запятую (см. MODELS)")
    ap.add_argument(
        "--scenarios",
        default=os.path.join("quality", "prompts", "scenarios_rp.json"),
        help="файл сценариев (относительно bench/)",
    )
    ap.add_argument("--seeds", default="11,22,33")
    ap.add_argument("--n-predict", type=int, default=4000)
    ap.add_argument("--temperature", type=float, default=0.6)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--concurrency", type=int, default=8, help="параллельных запросов")
    ap.add_argument(
        "--thinking",
        default="disabled",
        choices=["disabled", "low", "high", "max"],
        help="режим мышления по умолчанию (disabled = как локальный nothink)",
    )
    ap.add_argument("--config", default="api_safe", help="имя конфига в метриках")
    args = ap.parse_args()

    env = load_env(ENV_FILE)

    scen_path = args.scenarios
    if not os.path.isabs(scen_path):
        scen_path = os.path.join(ROOT, args.scenarios)
    scenarios = json.load(open(scen_path, encoding="utf-8"))
    seeds = [int(x) for x in args.seeds.split(",")]

    for slug in [s.strip() for s in args.models.split(",") if s.strip()]:
        if slug not in MODELS:
            print(f"[warn] неизвестный slug {slug}, пропуск")
            continue
        model, provider, override = MODELS[slug]
        thinking = override or args.thinking
        key_env, base_env, base_default = PROVIDERS[provider]
        key = env.get(key_env)
        base = env.get(base_env, base_default)
        if not key:
            print(f"[warn] нет {key_env} в .env — пропуск {slug}")
            continue

        mode = "nothink" if thinking == "disabled" else "think"
        out_dir = os.path.join(RUNS, f"rp_eval_{slug}_{mode}")
        raw_dir = os.path.join(out_dir, "raw")
        os.makedirs(raw_dir, exist_ok=True)

        print(
            f"\n[{slug}] {model} ({provider}, thinking={thinking}) -> {os.path.relpath(out_dir, ROOT)}"
        )
        tasks = []
        for sc in scenarios:
            for seed in seeds:
                tasks.append((sc.get("tag"), seed, sc["messages"]))

        def run_one(tag, seed, messages):
            t0 = time.time()
            rec = {"config": args.config, "tag": tag, "seed": seed, "model": model}
            try:
                resp = api_chat(
                    base,
                    key,
                    model,
                    [{"role": m["role"], "content": m["content"]} for m in messages],
                    args.n_predict,
                    args.temperature,
                    args.top_p,
                    thinking,
                )
                msg = resp["choices"][0]["message"]
                rec["text"] = (msg.get("content") or "").strip()
                rec["raw_content"] = (msg.get("reasoning_content") or "").strip()
                usage = resp.get("usage", {})
                rec["gen_tokens"] = usage.get("completion_tokens")
                rec["reasoning_tokens"] = usage.get(
                    "completion_tokens_details", {}
                ).get("reasoning_tokens")
            except Exception as e:  # noqa: BLE001
                rec["error"] = str(e)
                rec["text"] = ""
                rec["raw_content"] = ""
            rec["_secs"] = round(time.time() - t0, 1)
            return rec

        records = []
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            futs = [ex.submit(run_one, *t) for t in tasks]
            for fut in as_completed(futs):
                rec = fut.result()
                records.append(rec)
                mark = "ERR" if rec.get("error") else "OK "
                print(
                    f"  {mark} {rec['tag']:<10} s{rec['seed']}  "
                    f"{len(rec['text'])}ch  ({rec['_secs']}s)"
                )

        # стабильный порядок: сценарий, затем сид
        order = {f"{s.get('tag')}": i for i, s in enumerate(scenarios)}
        records.sort(key=lambda r: (order.get(r["tag"], 99), r["seed"]))
        metrics_path = os.path.join(out_dir, "metrics.jsonl")
        with open(metrics_path, "w", encoding="utf-8") as f:
            for rec in records:
                clean_rec = {k: v for k, v in rec.items() if k != "_secs"}
                f.write(json.dumps(clean_rec, ensure_ascii=False) + "\n")
                fname = f"{args.config}__{rec['tag']}__s{rec['seed']}.txt"
                with open(os.path.join(raw_dir, fname), "w", encoding="utf-8") as rf:
                    rf.write(
                        f"### config: {args.config}\n### tag: {rec['tag']}  seed: {rec['seed']}\n"
                        f"### model: {model}  thinking: {thinking}\n\n"
                    )
                    rf.write(rec["text"])
                    if rec["raw_content"]:
                        rf.write("\n\n### reasoning\n" + rec["raw_content"])

    print(
        f"\nМетрики: {os.path.relpath(RUNS, ROOT)}\\rp_eval_<slug>_<mode>\\metrics.jsonl"
    )


if __name__ == "__main__":
    main()
