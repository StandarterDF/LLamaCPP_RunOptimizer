#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сводка объективных метрик по каталогам API-прогонов (api_rp_eval.py).

Переиспользует `analyze()` из `bench\\rp_quality.py` — те же метрики «Чисто %»,
чужие алфавиты, junk, Cyr %, TTR — но без генерации (читает только metrics.jsonl).

Запуск (интерпретатор venv):
  .venv\\Scripts\\python.exe bench\\quality\\api_metrics_summary.py bench\\quality\\runs\\rp_eval_*_nothink ...
"""

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))  # bench/quality
ROOT = os.path.dirname(HERE)  # bench
sys.path.insert(0, ROOT)

import rp_quality as rq  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)


def load_texts(run_dir):
    texts = []
    path = os.path.join(run_dir, "metrics.jsonl")
    if not os.path.isfile(path):
        return texts
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("error"):
                continue
            t = (r.get("text") or "").strip()
            if t:
                texts.append(t)
    return texts


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def main():
    dirs = []
    for pat in sys.argv[1:]:
        dirs += sorted(glob.glob(pat)) if any(c in pat for c in "*?[") else [pat]
    if not dirs:
        print("укажите каталоги прогонов (маски допустимы)")
        return

    hdr = f"{'run':<34}{'N':>3}{'Чисто':>7}{'Чужой/1k':>10}{'CJK/1k':>8}{'Junk/1k':>9}{'Cyr%':>7}{'TTR150':>8}"
    print(hdr)
    print("-" * len(hdr))
    for d in dirs:
        texts = load_texts(d)
        if not texts:
            print(f"{os.path.basename(d):<34}  0  (нет ответов)")
            continue
        st = [rq.analyze(t) for t in texts]
        clean = 100.0 * sum(1 for s in st if s["clean"]) / len(st)
        name = os.path.basename(d.rstrip("\\/"))
        print(
            f"{name:<34}{len(st):>3}{clean:>6.0f}%"
            f"{mean([s['foreign_per_1k'] for s in st]):>10.2f}"
            f"{mean([s['cjk_per_1k'] for s in st]):>8.2f}"
            f"{mean([s['junk_per_1k'] for s in st]):>9.2f}"
            f"{mean([s['cyr_share'] for s in st]) * 100:>7.1f}"
            f"{mean([s['ttr_win'] for s in st]):>8.3f}"
        )


if __name__ == "__main__":
    main()
