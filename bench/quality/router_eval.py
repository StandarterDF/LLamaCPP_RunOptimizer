#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
router_eval.py — прогон RP-оценки через УЖЕ ЗАПУЩЕННЫЙ router-сервер llama.cpp.

Зачем: `bench\\rp_quality.py` и `bench\\quality\\rp_judge.py` поднимают свой llama-server.
Когда поднят роутер (`launch\\router\\run-router.bat`, порт 9931), поднимать второй сервер
нельзя (VRAM), а переключать модели умеет сам роутер. Этот оркестратор:
  1) собирает suite-файлы под каждую (модель, режим) с блоком `router`;
  2) гоняет `rp_quality.py` (генерация + языковые метрики, RU или EN);
  3) судит прогоны локальными судьями через роутер (`rp_judge.py`) и/или облачными
     (`api_judge.py`);
  4) сводит средние баллы (`judge_score.py`).

Один запуск — один язык и один набор моделей. Имена каталогов: `rp_eval_<slug>_<lang>_<mode>`.

Пример (английский скрин, 6 моделей, 2 сценария, оба режима, 4 судьи):
  .venv\\Scripts\\python.exe bench\\quality\\router_eval.py --name en_screen --lang en ^
      --models blume,schatten,glisten,dtv2,styletune,base_gemma26 ^
      --modes nothink,think --judges gemma,qwen,dsflash,dsv4pro

Только стандартная библиотека.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))  # bench/quality
ROOT = os.path.dirname(HERE)  # bench
PROJ = os.path.dirname(ROOT)  # корень проекта

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

VENV_PY = os.path.join(PROJ, ".venv", "Scripts", "python.exe")
PY = VENV_PY if os.path.isfile(VENV_PY) else sys.executable
QUALITY = os.path.join(ROOT, "rp_quality.py")
JUDGE = os.path.join(HERE, "rp_judge.py")
API_JUDGE = os.path.join(HERE, "api_judge.py")
SCORE = os.path.join(HERE, "judge_score.py")
RUNS = os.path.join(HERE, "runs")
SUITES = os.path.join(HERE, "suites")
LOG_DIR = os.path.join(PROJ, "logs")

# Модели роутера: slug -> {режим: model id}
MODELS = {
    "blume": {
        "nothink": "gemma4-31b-blume-v1",
        "think": "gemma4-31b-blume-v1-think",
    },
    "schatten": {
        "nothink": "gemma4-31b-schattenblume",
        "think": "gemma4-31b-schattenblume-think",
    },
    "glisten": {
        "nothink": "gemma4-31b-glistening",
        "think": "gemma4-31b-glistening-think",
    },
    "dtv2": {
        "nothink": "gemma4-31b-dark-thoughts",
        "think": "gemma4-31b-dark-thoughts-think",
    },
    "styletune": {
        # в общем роутере есть только styletune-rp (nothink) и styletune (chat, spec);
        # отдельного RP-think профиля нет — think не собираем.
        "nothink": "gemma4-26a4b-styletune-rp",
        "think": None,
    },
    "base_gemma26": {
        "nothink": "gemma4-26a4b-base-nothink",
        "think": "gemma4-26a4b-base-think",
    },
    "base_gemma31": {
        "nothink": "gemma4-31b-base-nothink",
        "think": "gemma4-31b-base-think",
    },
    "qwen36": {
        "nothink": "qwen36-35b-a3b-base-rp-nothink",
        "think": "qwen36-35b-a3b-base-rp-think",
    },
    "qwen38": {
        "nothink": "qwen38-27b-base-rp-nothink",
        "think": "qwen38-27b-base-rp-think",
    },
}

# Локальные судьи: имя -> id модели в роутере (та же модель, что у одиночных .bat).
LOCAL_JUDGES = {
    "gemma": "gemma4-26a4b-base-nothink",
    "qwen": "qwen36-35b-a3b-base-rp-nothink",
}
# Облачные судьи: имя -> id модели у провайдера (см. api_judge.py / .env).
API_JUDGES = {
    "dsflash": "deepseek-flash",
    "dsv4pro": "deepseek-v4-pro",
}

SCEN = {
    "base": "quality/prompts/scenarios_rp.json",
    "full": "quality/prompts/scenarios_rp_full.json",
    "en": "quality/prompts/scenarios_rp_en.json",
}

SAMPLING = {"temperature": 0.6, "min_p": 0.1, "top_k": 0, "top_p": 0.95}
N_PREDICT = {"nothink": 500, "think": 1600}


class RunLog:
    def __init__(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.f = open(path, "a", encoding="utf-8", errors="replace")

    def __call__(self, msg=""):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        self.f.write(line + "\n")
        self.f.flush()

    def raw(self, msg):
        print(msg, flush=True)
        self.f.write(msg + "\n")
        self.f.flush()

    def close(self):
        self.f.close()


def run(cmd, log, phase=""):
    log("")
    log(f"=== {phase or 'cmd'} ===")
    log("$ " + " ".join(cmd))
    t0 = time.time()
    p = subprocess.Popen(
        cmd,
        cwd=PROJ,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    assert p.stdout is not None
    for line in p.stdout:
        log.raw("    | " + line.rstrip("\n"))
    p.wait()
    log(f"=== {phase or 'cmd'}: rc={p.returncode}, {time.time() - t0:.0f}s ===")
    return p.returncode


def main():
    ap = argparse.ArgumentParser(description="RP-оценка через роутер")
    ap.add_argument("--name", required=True, help="короткое имя прогона")
    ap.add_argument("--lang", choices=["ru", "en"], default="en")
    ap.add_argument("--models", required=True, help="slug'и через запятую (см. MODELS)")
    ap.add_argument("--modes", default="nothink,think")
    ap.add_argument(
        "--scenarios", default=None, help="base|full|en (по умолчанию = lang)"
    )
    ap.add_argument("--seeds", default="11,22,33")
    ap.add_argument(
        "--judges",
        default="gemma,qwen,dsflash,dsv4pro",
        help="gemma,qwen (локальные через роутер) | dsflash,dsv4pro (облако) | none",
    )
    ap.add_argument("--router-url", default="http://127.0.0.1:9931")
    ap.add_argument("--judge-batch", type=int, default=3)
    ap.add_argument("--skip-generate", action="store_true")
    ap.add_argument("--skip-judge", action="store_true")
    ap.add_argument(
        "--reuse", action="store_true", help="не перегонять, если metrics.jsonl есть"
    )
    ap.add_argument("--log", default=None)
    args = ap.parse_args()

    stamp = time.strftime("%Y%m%d-%H%M%S")
    log_path = args.log or os.path.join(LOG_DIR, f"rp_eval_{args.name}_{stamp}.log")
    log = RunLog(log_path)

    scen_key = args.scenarios or ("en" if args.lang == "en" else "base")
    scen_path = SCEN[scen_key]
    slugs = [s.strip() for s in args.models.split(",") if s.strip()]
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    seeds = [int(x) for x in args.seeds.split(",")]
    judge_names = [j.strip() for j in args.judges.split(",") if j.strip()]

    log("=" * 72)
    log(f"RP router eval: {args.name}  lang={args.lang}  scenarios={scen_key}")
    log(f"лог     : {os.path.relpath(log_path, PROJ)}")
    log(f"роутер  : {args.router_url}")
    log(f"модели  : {', '.join(slugs)}")
    log(
        f"режимы  : {', '.join(modes)} | сиды: {seeds} | судьи: {', '.join(judge_names)}"
    )
    log("=" * 72)

    run_dirs = []
    # ---- 1. suite-файлы + генерация ----
    for slug in slugs:
        if slug not in MODELS:
            log(f"[warn ] неизвестный slug {slug}, пропуск")
            continue
        for mode in modes:
            model_id = MODELS[slug].get(mode)
            if not model_id:
                log(f"[warn ] у {slug} нет режима {mode}, пропуск")
                continue
            suite_name = f"rp_eval_{slug}_{args.lang}_{mode}"
            suite_path = os.path.join(SUITES, f"suite_{suite_name}.json")
            out_dir = os.path.join(RUNS, suite_name)
            run_dirs.append(out_dir)
            suite = {
                "_комментарий": f"RP через роутер: {slug} ({model_id}), lang={args.lang}, режим {mode}.",
                "name": suite_name,
                "lang": args.lang,
                "router": {"url": args.router_url, "model": model_id},
                "prompts": scen_path,
                "n_predict": N_PREDICT.get(mode, 500),
                "seeds": seeds,
                "configs": [
                    {
                        "name": "ru_safe",
                        "title": f"{args.lang}-safe: temp0.6 min-p0.1 top-k0 top-p0.95",
                        "sampling": dict(SAMPLING),
                    }
                ],
            }
            os.makedirs(SUITES, exist_ok=True)
            with open(suite_path, "w", encoding="utf-8") as f:
                json.dump(suite, f, ensure_ascii=False, indent=2)
            log(f"[suite] {os.path.relpath(suite_path, PROJ)}  model={model_id}")

    if not args.skip_generate:
        log("")
        log("--- ФАЗА 1: генерация через роутер ---")
        for slug in slugs:
            for mode in modes:
                if not MODELS.get(slug, {}).get(mode):
                    continue
                suite_name = f"rp_eval_{slug}_{args.lang}_{mode}"
                out_dir = os.path.join(RUNS, suite_name)
                if args.reuse and os.path.isfile(
                    os.path.join(out_dir, "metrics.jsonl")
                ):
                    log(f"[skip ] {suite_name}: metrics.jsonl уже есть")
                    continue
                suite_path = os.path.join(SUITES, f"suite_{suite_name}.json")
                run(
                    [PY, QUALITY, suite_path, "--out", out_dir],
                    log,
                    phase=f"генерация {slug}/{mode}",
                )

    # ---- 2. судейство ----
    judge_dirs = []
    if not args.skip_judge and judge_names and judge_names != ["none"]:
        log("")
        log("--- ФАЗА 2: судейство ---")
        for jname in judge_names:
            if jname in LOCAL_JUDGES:
                jout = os.path.join(RUNS, f"rp_judge_{jname}_{args.name}")
                cmd = [
                    PY,
                    JUDGE,
                    *run_dirs,
                    "--router-url",
                    args.router_url,
                    "--router-model",
                    LOCAL_JUDGES[jname],
                    "--lang",
                    args.lang,
                    "--prompts",
                    scen_path,
                    "--batch",
                    str(args.judge_batch),
                    "--out",
                    jout,
                ]
                os.makedirs(jout, exist_ok=True)
                run(cmd, log, phase=f"судья {jname} (router)")
                judge_dirs.append(jout)
            elif jname in API_JUDGES:
                jout = os.path.join(RUNS, f"rp_judge_{jname}_{args.name}")
                cmd = [
                    PY,
                    API_JUDGE,
                    *run_dirs,
                    "--model",
                    API_JUDGES[jname],
                    "--lang",
                    args.lang,
                    "--prompts",
                    scen_path,
                    "--batch",
                    str(args.judge_batch),
                    "--out",
                    jout,
                ]
                os.makedirs(jout, exist_ok=True)
                run(cmd, log, phase=f"судья {jname} (api)")
                judge_dirs.append(jout)
            else:
                log(f"[warn ] неизвестный судья {jname}, пропуск")

    # ---- 3. сводка ----
    if judge_dirs:
        log("")
        log("--- ФАЗА 3: сводка баллов ---")
        for jout in judge_dirs:
            run([PY, SCORE, jout], log, phase=f"сводка {os.path.basename(jout)}")

    log("")
    log("Готово.")
    log("Прогоны : " + ", ".join(os.path.relpath(d, PROJ) for d in run_dirs))
    if judge_dirs:
        log("Судьи   : " + ", ".join(os.path.relpath(d, PROJ) for d in judge_dirs))
    log(f"Лог     : {os.path.relpath(log_path, PROJ)}")
    log.close()


if __name__ == "__main__":
    main()
