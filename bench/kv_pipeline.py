#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Оркестратор KV-исследования: ждёт освобождения GPU и выполняет всё подряд.

Шаги (последовательно, в одном фоновом процессе):
  1) дождаться, пока числовая матрица NIAH добьёт все конфиги и освободится GPU;
  2) --ppl-only: досчитать PPL для готовых конфигов dense-модели;
  3) kv_prompts.py: промптовое сравнение KV (f16/q8_0/q4_0/смешанный) — ответы рядом;
  4) plot_kv.py: перестроить все графики (вычисленные + измеренные).

Зачем: прогон идёт часами и не должен требовать ручного запуска между шагами.
Запуск: .venv\\Scripts\\python.exe bench\\kv_pipeline.py
"""

import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, "bench")
PY = sys.executable
MATRIX = os.path.join(BENCH, "runs", "kv", "matrix")
PROMPTS_OUT = os.path.join(BENCH, "runs", "kv_prompts", "run")

KV_SUITE = os.path.join(BENCH, "suites", "kv", "kv_gemma.json")
PROMPTS_SUITE = os.path.join(BENCH, "suites", "kv", "kv_prompts.json")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def log(msg):
    print(f"[pipeline {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def gpu_busy():
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq llama-server.exe"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        return "llama-server.exe" in (out.stdout or "")
    except Exception:
        return False


def matrix_count():
    path = os.path.join(MATRIX, "results.jsonl")
    if not os.path.exists(path):
        return 0
    return sum(1 for ln in open(path, encoding="utf-8") if ln.strip())


def wait_for_matrix(n_expect=18, timeout_min=120):
    t0 = time.time()
    while time.time() - t0 < timeout_min * 60:
        if matrix_count() >= n_expect and not gpu_busy():
            return True
        log(
            f"ждём матрицу: {matrix_count()}/{n_expect}, GPU "
            f"{'занят' if gpu_busy() else 'свободен'}"
        )
        time.sleep(30)
    log("таймаут ожидания матрицы — продолжаю как есть")
    return False


def run(step_name, args):
    log(f"СТАРТ: {step_name}")
    p = subprocess.run([PY] + args, cwd=ROOT)
    log(f"ГОТОВО: {step_name} (код {p.returncode})")
    return p.returncode


def main():
    os.makedirs(PROMPTS_OUT, exist_ok=True)
    wait_for_matrix()
    run(
        "PPL",
        [
            os.path.join("bench", "kv_quality.py"),
            KV_SUITE,
            "--ppl-only",
            "--out",
            MATRIX,
        ],
    )
    run(
        "промптовое сравнение KV",
        [os.path.join("bench", "kv_prompts.py"), PROMPTS_SUITE, "--out", PROMPTS_OUT],
    )
    run(
        "графики",
        [
            os.path.join("bench", "plot_kv.py"),
            "--suite",
            KV_SUITE,
            "--results",
            os.path.join(MATRIX, "results.jsonl"),
            "--out",
            "docs/images",
        ],
    )
    log("ВСЁ ГОТОВО")
    print("PIPELINE_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
