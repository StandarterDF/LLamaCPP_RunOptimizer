#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RP Model Eval — оптимизированный оркестратор оценки RP-качества локальной GGUF-модели.

Один запуск делает всё:
  1) генерирует suite-файл(ы) под модель (fan out по режимам nothink/think);
  2) прогоняет bench\\rp_quality.py на базовом (2 сценария) или полном (6) наборе;
  3) судит прогоны ПАНЕЛЬЮ ИЗ ЧЕТЫРЁХ судей (два локальных: gemma-4-26B-A4B и Qwen3.6-35B-A3B
     MXFP4 через rp_judge.py; два облачных: DeepSeek-Flash и DeepSeek-Pro через api_judge.py);
  4) сводит средние баллы через judge_score.py — по каждому судье и единое «среднее по 4 судьям».

ВСЁ пишется в единый лог прогона (logs\\rp_eval_<name>_<stamp>.log): фазы, поток вывода
харнесса (по каждой генерации), вывод судей и сводка. Путь печатается в начале и конце.

Правило экономии: базовый набор (2 сценария) — скрин для ВСЕХ моделей; полный набор (6)
гоняется ТОЛЬКО для моделей, показавших лучший результат на скрине (см. SKILL.md).

Облачным судьям нужен ключ в .env (DEEPSEEK_API_KEY) — иначе скрипт останавливается с ошибкой,
чтобы не выдать молча оценку по 2 судьям вместо 4. Только локальные: --judges gemma,qwen.

Запуск (интерпретатором venv проекта; путь модели — в ОДИНАРНЫХ кавычках, иначе PowerShell
съест ${MODELS_DIR}):
  .venv\\Scripts\\python.exe .opencode\\skills\\rp-model-eval\\scripts\\run_eval.py ^
      --name base_gemma26 --model '${MODELS_DIR}/unsloth/gemma-4-26B-A4B-it-GGUF/gemma-4-26B-A4B-it-UD-IQ3_XXS.gguf' ^
      --family gemma --scenarios base --modes nothink,think --judges gemma,qwen,dsflash,dspro

Только стандартная библиотека.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def find_root(start):
    cur = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(cur, "bench", "rp_quality.py")):
            return cur
        nxt = os.path.dirname(cur)
        if nxt == cur:
            return None
        cur = nxt


PROJECT_DIR = find_root(HERE)
if not PROJECT_DIR:
    raise SystemExit("не найден корень проекта (bench/rp_quality.py)")

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

# ----------------------------------------------------------------------------
# env.local.json -> плейсхолдеры ${MODELS_DIR} и т.п.
# ----------------------------------------------------------------------------
ENV_LOCAL = os.path.join(PROJECT_DIR, "bench", "env.local.json")
ENV_MAP = {"PROJECT_DIR": PROJECT_DIR}
try:
    with open(ENV_LOCAL, encoding="utf-8") as f:
        ENV_MAP.update(json.load(f))
except Exception:
    pass


def expand(text):
    return re.sub(
        r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}",
        lambda m: str(ENV_MAP.get(m.group(1), m.group(0))),
        text,
    )


def read_env_keys():
    """Имена переменных из .env (без значений) — предпроверка облачных судей."""
    keys = set()
    try:
        with open(ENV_FILE, encoding="utf-8") as f:
            for ln in f:
                s = ln.strip()
                if s and not s.startswith("#") and "=" in s:
                    keys.add(s.split("=", 1)[0].strip())
    except OSError:
        pass
    return keys


VENV_PY = os.path.join(PROJECT_DIR, ".venv", "Scripts", "python.exe")
PY = VENV_PY if os.path.isfile(VENV_PY) else sys.executable
QUALITY = os.path.join(PROJECT_DIR, "bench", "rp_quality.py")
JUDGE = os.path.join(PROJECT_DIR, "bench", "quality", "rp_judge.py")
API_JUDGE = os.path.join(PROJECT_DIR, "bench", "quality", "api_judge.py")
SCORE = os.path.join(PROJECT_DIR, "bench", "quality", "judge_score.py")
ENV_FILE = os.path.join(PROJECT_DIR, ".env")
RUNS = os.path.join(PROJECT_DIR, "bench", "quality", "runs")
SUITE_DIR = os.path.join(PROJECT_DIR, "bench", "quality", "suites")
LOG_DIR = os.path.join(PROJECT_DIR, "logs")

SCEN = {
    "base": "quality/prompts/scenarios_rp.json",
    "full": "quality/prompts/scenarios_rp_full.json",
}

# Штатная панель — ЧЕТЫРЕ судьи (как в витрине docs\quality\rp-ranking.md): два локальных
# (абсолютная шкала через rp_judge.py) + два облачных DeepSeek через api_judge.py.
# Порядок в JUDGES = порядок прогонов. Значения локальных совпадают с rp_judge.py.
JUDGES = {
    "gemma": {
        "kind": "local",
        "model": "${MODELS_DIR}/unsloth/gemma-4-26B-A4B-it-GGUF/gemma-4-26B-A4B-it-UD-IQ3_XXS.gguf",
        "template": "${LLAMA_DIR}/gemma4.jinja",
        "spec": False,
    },
    "qwen": {
        "kind": "local",
        "model": "${MODELS_DIR}/unsloth/Qwen3.6-35B-A3B-MTP-GGUF/Qwen3.6-35B-A3B-MXFP4_MOE.gguf",
        "template": "none",
        "spec": True,
    },
    # Облачные судьи: ключи в .env (DEEPSEEK_API_KEY). thinking off — чтобы шкала была
    # сопоставима с локальными nothink-судьями (у DeepSeek в nothink учитывается temperature).
    "dsflash": {
        "kind": "api",
        "provider": "deepseek",
        "model": "deepseek-flash",
        "key_env": "DEEPSEEK_API_KEY",
        "thinking": "disabled",
    },
    "dsv4pro": {
        "kind": "api",
        "provider": "deepseek",
        "model": "deepseek-v4-pro",
        "key_env": "DEEPSEEK_API_KEY",
        "thinking": "disabled",
    },
}
# синонимы, чтобы не падать на «dspro»
JUDGE_ALIASES = {"dspro": "dsv4pro", "pro": "dsv4pro", "flash": "dsflash"}
DEFAULT_JUDGES = "gemma,qwen,dsflash,dsv4pro"


class RunLog:
    """Единый лог прогона: печать в консоль + запись в файл с таймстампами."""

    def __init__(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self.f = open(path, "a", encoding="utf-8", errors="replace")

    def __call__(self, msg=""):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        self.f.write(line + "\n")
        self.f.flush()

    def raw(self, msg):
        """Без таймстампа (для потока вывода подпроцесса)."""
        print(msg, flush=True)
        self.f.write(msg + "\n")
        self.f.flush()

    def close(self):
        self.f.close()


def sanitize_cmd(cmd):
    """Маскирует реальные пути плейсхолдерами, чтобы в run.log не текли личные пути."""
    s = " ".join(cmd)
    pairs = sorted(
        ((v, "${" + k + "}") for k, v in ENV_MAP.items() if isinstance(v, str) and v),
        key=lambda p: -len(p[0]),
    )
    for src, dst in pairs:
        s = s.replace(src, dst)
    return s


def run(cmd, log, phase=""):
    """Запуск подпроцесса с потоковой телетрансляцией в консоль и лог."""
    log("")
    log(f"=== {phase or 'cmd'} ===")
    log("$ " + sanitize_cmd(cmd))
    t0 = time.time()
    p = subprocess.Popen(
        cmd,
        cwd=PROJECT_DIR,
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


def build_base_args(family, mode, draft, no_spec, ctx, threads, budget_think):
    args = [
        "-np",
        "1",
        "-c",
        str(ctx),
        "-fa",
        "on",
        "--fit",
        "on",
        "--load-mode",
        "none",
        "-t",
        str(threads),
        "-tb",
        str(threads),
        "-ctk",
        "q4_0",
        "-ctv",
        "q4_0",
    ]
    if family == "gemma":
        args += ["--jinja", "--chat-template-file", "${LLAMA_DIR}/gemma4.jinja"]
    else:
        args += ["--jinja"]
    # Встроенная MTP-голова есть только у Qwen3.6. У gemma-26B и прочих (other, напр. Mistral)
    # её нет: спекуляция — только если явно задан внешний --draft.
    if family == "qwen":
        use_spec = not no_spec
    else:
        use_spec = (not no_spec) and bool(draft)
    if use_spec:
        args += [
            "--spec-type",
            "draft-mtp",
            "--spec-draft-n-max",
            "5",
            "--spec-draft-n-min",
            "1",
            "--spec-draft-p-min",
            "0.75",
        ]
    if draft:
        args += ["-md", draft]
    if mode == "think":
        if family == "gemma":
            args += [
                "--reasoning",
                "on",
                "--reasoning-effort",
                "low",
                "--reasoning-budget",
                str(budget_think),
            ]
        else:
            args += ["--reasoning", "on", "--reasoning-budget", str(budget_think)]
    else:
        args += ["--reasoning", "off", "--reasoning-budget", "0"]
    return args


def main():
    ap = argparse.ArgumentParser(description="RP Model Eval")
    ap.add_argument(
        "--name", required=True, help="короткое имя прогона, напр. base_gemma26"
    )
    ap.add_argument(
        "--model", required=True, help="путь к GGUF (можно ${MODELS_DIR}/...)"
    )
    ap.add_argument(
        "--family",
        choices=["gemma", "qwen", "other"],
        default="qwen",
        help="шаблон/спекуляция: gemma -> gemma4.jinja; qwen -> встроенный MTP",
    )
    ap.add_argument("--modes", default="nothink,think")
    ap.add_argument("--scenarios", choices=["base", "full"], default="base")
    ap.add_argument("--seeds", default="11,22,33")
    ap.add_argument(
        "--judges",
        default=DEFAULT_JUDGES,
        help="панель судей: gemma,qwen,dsflash,dspro | gemma,qwen (локальные) | none",
    )
    ap.add_argument("--judge-batch", type=int, default=3)
    ap.add_argument(
        "--judge-concurrency",
        type=int,
        default=10,
        help="параллельных запросов облачных судей (api_judge.py)",
    )
    ap.add_argument(
        "--draft", default=None, help="внешний MTP-драфт (-md), иначе встроенный"
    )
    ap.add_argument("--no-spec", action="store_true")
    ap.add_argument("--ctx", type=int, default=51200)
    ap.add_argument("--threads", type=int, default=12)
    ap.add_argument("--n-predict-nothink", type=int, default=500)
    ap.add_argument("--n-predict-think", type=int, default=1600)
    ap.add_argument(
        "--reasoning-budget-think",
        type=int,
        default=1024,
        help="бюджет мышления (think); -1 = безлимит, 0 = выкл",
    )
    ap.add_argument(
        "--reuse",
        action="store_true",
        help="не перегонять, если metrics.jsonl уже есть",
    )
    ap.add_argument("--skip-generate", action="store_true")
    ap.add_argument("--skip-judge", action="store_true")
    ap.add_argument(
        "--log",
        default=None,
        help="путь к логу прогона (по умолчанию logs\\rp_eval_<name>_<stamp>.log)",
    )
    args = ap.parse_args()

    stamp = time.strftime("%Y%m%d-%H%M%S")
    log_path = args.log or os.path.join(LOG_DIR, f"rp_eval_{args.name}_{stamp}.log")
    log = RunLog(log_path)

    model = expand(args.model)
    log("=" * 72)
    log(f"RP Model Eval: {args.name}")
    log(f"лог     : {os.path.relpath(log_path, PROJECT_DIR)}")
    log(f"модель  : {model}")
    log(
        f"family  : {args.family} | набор: {args.scenarios} | режимы: {args.modes} | сиды: {args.seeds}"
    )
    log(f"судьи   : {args.judges}")
    log("=" * 72)

    if not os.path.isfile(model):
        log(f"ОШИБКА: нет файла модели: {model}")
        log.close()
        raise SystemExit(1)
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    seed_list = [int(x) for x in args.seeds.split(",")]
    scen_path = SCEN[args.scenarios]

    # ---- 0. проверка судей до старта (чтобы не получить молча 2 судьи из 4) ----
    judge_list = []
    for j in [x.strip() for x in args.judges.split(",") if x.strip()]:
        judge_list.append(JUDGE_ALIASES.get(j, j))
    if args.judges.strip().lower() != "none" and not args.skip_judge:
        unknown = [j for j in judge_list if j not in JUDGES]
        if unknown:
            log(f"ОШИБКА: неизвестные судьи {unknown}; есть: {', '.join(JUDGES)}")
            log.close()
            raise SystemExit(2)
        env_keys = read_env_keys()
        missing = [
            JUDGES[j]["key_env"]
            for j in judge_list
            if JUDGES[j]["kind"] == "api" and JUDGES[j]["key_env"] not in env_keys
        ]
        if missing:
            log(
                "ОШИБКА: нет ключа(ей) "
                + ", ".join(sorted(set(missing)))
                + " в .env — облачные судьи недоступны. Оценка НЕ будет по 4 судьям."
            )
            log("        добавьте ключ в .env (шаблон .env.example) или запустите")
            log("        с --judges gemma,qwen (только локальные).")
            log.close()
            raise SystemExit(2)

    # ---- 1. suite-файлы ----
    run_dirs = []
    log("")
    log("--- ФАЗА 1: подготовка suite-файлов ---")
    for mode in modes:
        suite_name = f"rp_eval_{args.name}_{mode}"
        suite_path = os.path.join(SUITE_DIR, f"suite_{suite_name}.json")
        out_dir = os.path.join(RUNS, suite_name)
        run_dirs.append(out_dir)
        n_pred = args.n_predict_think if mode == "think" else args.n_predict_nothink
        suite = {
            "_комментарий": f"RP-оценка ({args.scenarios}): {args.name}, режим {mode}. Сгенерировано rp-model-eval.",
            "name": suite_name,
            "server": "${PROJECT_DIR}/downloads/llama-b11382-cu124/llama-server.exe",
            "model": args.model,
            "base_args": build_base_args(
                args.family,
                mode,
                args.draft,
                args.no_spec,
                args.ctx,
                args.threads,
                args.reasoning_budget_think,
            ),
            "prompts": scen_path,
            "n_predict": n_pred,
            "seeds": seed_list,
            "configs": [
                {
                    "name": "ru_safe",
                    "title": "RU-safe: temp0.6 min-p0.1 top-k0 top-p0.95",
                    "sampling": {
                        "temperature": 0.6,
                        "min_p": 0.1,
                        "top_k": 0,
                        "top_p": 0.95,
                    },
                }
            ],
        }
        with open(suite_path, "w", encoding="utf-8") as f:
            json.dump(suite, f, ensure_ascii=False, indent=2)
        log(
            f"[suite] {os.path.relpath(suite_path, PROJECT_DIR)}  (n_predict={n_pred}, seeds={seed_list})"
        )

    # ---- 2. генерация ----
    if not args.skip_generate:
        log("")
        log("--- ФАЗА 2: генерация ---")
        for mode, out_dir in zip(modes, run_dirs):
            metrics = os.path.join(out_dir, "metrics.jsonl")
            if args.reuse and os.path.isfile(metrics):
                log(f"[skip ] {os.path.basename(out_dir)}: metrics.jsonl уже есть")
                continue
            suite_path = os.path.join(
                SUITE_DIR, f"suite_rp_eval_{args.name}_{mode}.json"
            )
            rc = run(
                [PY, QUALITY, suite_path, "--out", out_dir],
                log,
                phase=f"генерация {args.name} / {mode}",
            )
            if rc != 0:
                log(f"[warn ] rp_quality.py вернул rc={rc} для {mode}")

    # ---- 3. судейство ----
    judge_dirs = []
    if not args.skip_judge and args.judges.strip().lower() != "none":
        log("")
        log(f"--- ФАЗА 3: судейство ({len(judge_list)} судей) ---")
        for jname in judge_list:
            j = JUDGES[jname]
            jout = os.path.join(RUNS, f"rp_judge_{jname}_{args.name}")
            if j["kind"] == "api":
                # облачный судья: те же ответы, тот же промпт, но через API (параллельно)
                cmd = [
                    PY,
                    API_JUDGE,
                    *run_dirs,
                    "--model",
                    j["model"],
                    "--provider",
                    j["provider"],
                    "--prompts",
                    scen_path,
                    "--batch",
                    str(args.judge_batch),
                    "--thinking",
                    j["thinking"],
                    "--concurrency",
                    str(args.judge_concurrency),
                    "--out",
                    jout,
                ]
            else:
                cmd = [
                    PY,
                    JUDGE,
                    *run_dirs,
                    "--model",
                    j["model"],
                    "--template",
                    j["template"],
                    "--prompts",
                    scen_path,
                    "--batch",
                    str(args.judge_batch),
                    "--out",
                    jout,
                ]
                if j["spec"]:
                    cmd.append("--spec")
            os.makedirs(jout, exist_ok=True)
            run(cmd, log, phase=f"судья {jname}")
            judge_dirs.append(jout)

    # ---- 4. сводка ----
    if judge_dirs:
        log("")
        log("--- ФАЗА 4: сводка баллов ---")
        for jout in judge_dirs:
            run([PY, SCORE, jout], log, phase=f"сводка {os.path.basename(jout)}")
        if len(judge_dirs) > 1:
            # единая цифра панели: judge_score.py, получив несколько каталогов судей,
            # объединяет все их оценки (это и есть «среднее по N судьям» для rp-ranking.md)
            run(
                [PY, SCORE, *judge_dirs],
                log,
                phase=f"сводка: среднее по {len(judge_dirs)} судьям",
            )

    log("")
    log("Готово.")
    log("Прогоны : " + ", ".join(os.path.relpath(d, PROJECT_DIR) for d in run_dirs))
    if judge_dirs:
        log(
            "Судьи   : "
            + ", ".join(os.path.relpath(d, PROJECT_DIR) for d in judge_dirs)
        )
    log(f"Лог     : {os.path.relpath(log_path, PROJECT_DIR)}")
    log.close()


if __name__ == "__main__":
    main()
