#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка: участились ли срывы в коде под квантованным KV (несколько сэмплов).

При temp=0 декодирование жадно и сид не влияет — поэтому единичный провал ничего не
доказывает. Здесь гоняем задачи кода на нескольких сидах при температуре > 0 и
сравниваем f16 / q8_0 / q4_0 по доле успеха и по языку кода (py / js / другое).

Запуск:
  .venv\\Scripts\\python.exe bench\\kv_code_seeds.py bench\\suites\\kv\\kv_canary.json
  .venv\\Scripts\\python.exe bench\\kv_code_seeds.py <suite> --kvs f16,q8_0,q4_0 --temperature 0.7
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv_canary as C  # noqa: E402
import kv_quality as K  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def run_cfg(server_exe, model, kv, suite, out_dir, port, seeds, temperature):
    cfg_dir = os.path.join(out_dir, f"{model['name']}__{kv}")
    os.makedirs(cfg_dir, exist_ok=True)
    log_path = os.path.join(cfg_dir, "server.log")
    ctx = int(model.get("ctx", 16384))
    cli = (
        ["--model", model["model"], "-np", "1", "-c", str(ctx)]
        + model.get("base_args", [])
        + K.KV_ARGS[kv]
    )
    proc, logf = K.start_server(server_exe, {"port": port, "cli": cli}, log_path)
    rec = {"model": model["name"], "kv": kv, "tasks": {}, "error": None}
    try:
        if not K.wait_health(port, proc, timeout=900):
            rec["error"] = "server did not become healthy"
            return rec
        time.sleep(2.0)
        for task in suite["code_tasks"]:
            passes, langs = 0, {}
            for sd in seeds:
                r = C.chat(
                    port,
                    "Ты пишешь код. Отвечай только кодом функции.",
                    task["prompt"],
                    n_predict=220,
                    seed=sd,
                    temperature=temperature,
                    cache_prompt=False,
                )
                code = C.extract_code(r["content"])
                ok = C.run_code(code, task["test"])
                passes += ok
                has_def = "def " in code
                has_js = bool(re.search(r"\bfunction\s+\w+\s*\(", code))
                key = "py" if has_def else ("js" if has_js else "other")
                langs[key] = langs.get(key, 0) + 1
            rec["tasks"][task["id"]] = {"pass": passes, "n": len(seeds), "langs": langs}
            print(f"   {kv:6} {task['id']:8} pass={passes}/{len(seeds)}  langs={langs}")
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"
    finally:
        K.kill_proc(proc)
        logf.close()
        time.sleep(1.5)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("suite")
    ap.add_argument("--seeds", default="1,2,3,4,5,6,7,8,9,10")
    ap.add_argument("--kvs", default="f16,q8_0,q4_0")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--port", type=int, default=9961)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    seeds = [int(x) for x in a.seeds.split(",")]
    kvs = [x.strip() for x in a.kvs.split(",")]
    suite = K.expand_obj(json.load(open(a.suite, encoding="utf-8")))
    server_exe = suite["server"]
    run_dir = a.out or os.path.join(
        K.ROOT, "runs", "kv_canary", f"code_seeds-{datetime.now():%Y%m%d-%H%M%S}"
    )
    os.makedirs(run_dir, exist_ok=True)

    results = []
    i = 0
    for model in suite["models"]:
        for kv in kvs:
            i += 1
            print(f"\n[{model['name']}] KV={kv}  temp={a.temperature}  n={len(seeds)}")
            results.append(
                run_cfg(
                    server_exe,
                    model,
                    kv,
                    suite,
                    run_dir,
                    a.port + (i % 3),
                    seeds,
                    a.temperature,
                )
            )
            time.sleep(4)

    with open(os.path.join(run_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n===== ИТОГ: доля успешных генераций кода и языки =====")
    for model in suite["models"]:
        for kv in kvs:
            r = next(
                (x for x in results if x["model"] == model["name"] and x["kv"] == kv),
                None,
            )
            if not r or r.get("error"):
                continue
            tot_pass = sum(t["pass"] for t in r["tasks"].values())
            tot = sum(t["n"] for t in r["tasks"].values())
            langs = {}
            for t in r["tasks"].values():
                for k, v in t["langs"].items():
                    langs[k] = langs.get(k, 0) + v
            print(
                f"{model['name']:20} {kv:6} pass={tot_pass}/{tot} "
                f"({tot_pass / tot:.2f})  языки={langs}"
            )
    print(f"\n{run_dir}\\results.json")


if __name__ == "__main__":
    main()
