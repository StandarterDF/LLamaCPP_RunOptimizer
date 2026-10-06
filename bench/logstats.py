#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сводка по логам llama-server (папка logs\\ или любой файл/каталог/маска).

Читает строки `slot print_timing` и печатает по каждому запуску:
PP и TG, среднюю длину угадайки (`mean len`) и принятие спекуляции.
Только stdlib. Запуск интерпретатором venv:

    .venv\\Scripts\\python.exe bench\\logstats.py [путь ...]

Без аргументов сканирует папку `logs\\` в корне проекта — туда launch\\**\\*.bat
пишут датированный лог каждого старта (флаг --log-file).
"""

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RE_ACC = re.compile(
    r"draft acceptance =\s*([0-9.]+) \(\s*(\d+)\s*accepted\s*/\s*(\d+)\s*generated\),"
    r"\s*mean len =\s*([0-9.]+)"
)
RE_PROMPT = re.compile(
    r"prompt eval time =\s*[\d.]+ ms\s*/\s*(\d+) tokens \(\s*[\d.]+ ms per token,\s*([\d.]+) tokens per second\)"
)
RE_EVAL = re.compile(
    r"(?<!prompt )eval time =\s*[\d.]+ ms\s*/\s*(\d+) tokens \(\s*[\d.]+ ms per token,\s*([\d.]+) tokens per second\)"
)
RE_BAT = re.compile(r"^\s*bat\s*:\s*(.+?)\s*$", re.M)
RE_MODEL = re.compile(r"^\s*model\s*:\s*(.+?)\s*$", re.M)


def avg(vals):
    vals = [v for v in vals if isinstance(v, (int, float))]
    return sum(vals) / len(vals) if vals else None


def collect_files(args):
    if not args:
        args = [os.path.join(ROOT, "logs")]
    files = []
    for a in args:
        if os.path.isdir(a):
            files += sorted(glob.glob(os.path.join(a, "**", "*.log"), recursive=True))
        elif os.path.isfile(a):
            files.append(a)
        else:
            files += sorted(glob.glob(a, recursive=True))
    return files


def parse(path):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    accs = [
        (int(m.group(2)), int(m.group(3)), float(m.group(4)))
        for m in RE_ACC.finditer(text)
    ]
    tg = [float(m.group(2)) for m in RE_EVAL.finditer(text)]
    pp = [float(m.group(2)) for m in RE_PROMPT.finditer(text)]
    gen = [int(m.group(1)) for m in RE_EVAL.finditer(text)]
    bat_m = RE_BAT.search(text)
    model_m = RE_MODEL.search(text)
    accepted = sum(a for a, _, _ in accs)
    generated = sum(g for _, g, _ in accs)
    try:
        rel = os.path.relpath(path, ROOT)
    except ValueError:
        rel = path
    return {
        "file": rel,
        "bat": bat_m.group(1) if bat_m else "",
        "model": os.path.basename(model_m.group(1)) if model_m else "",
        "reqs": max(len(tg), len(accs)),
        "pp": avg(pp),
        "tg": avg(tg),
        "mean_len": avg([l for _, _, l in accs]),
        "accept": (100.0 * accepted / generated) if generated else None,
        "accepted": accepted,
        "generated": generated,
        "gen": sum(gen),
    }


def main():
    args = [a for a in sys.argv[1:] if a not in ("-h", "--help")]
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print(__doc__)
        return
    files = collect_files(args)
    if not files:
        print(
            "Логи не найдены. Запустите любой launch\\**\\*.bat — он создаст "
            "logs\\<имя>_<дата_время>.log, либо укажите путь:"
            "\n  .venv\\Scripts\\python.exe bench\\logstats.py <файл|папка>"
        )
        return

    rows = [r for r in (parse(f) for f in files) if r and (r["tg"] or r["mean_len"])]
    if not rows:
        print("В указанных файлах нет строк slot print_timing (пустой/чужой лог).")
        return

    def fmt(v, nd=2):
        return "-" if v is None else f"{v:.{nd}f}"

    head = (
        "| Лог | Запросов | PP, t/s | TG, t/s | mean len | Принятие | Сген., tok |\n"
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    print(head)
    for r in sorted(rows, key=lambda x: x["file"]):
        acc = "-" if r["accept"] is None else f"{r['accept']:.1f}%"
        print(
            f"| {r['file']} | {r['reqs']} | {fmt(r['pp'], 0)} | {fmt(r['tg'], 1)} "
            f"| {fmt(r['mean_len'])} | {acc} | {r['gen']} |"
        )

    tg = avg([r["tg"] for r in rows])
    ml = avg([r["mean_len"] for r in rows])
    tot_a = sum(r["accepted"] for r in rows)
    tot_g = sum(r["generated"] for r in rows)
    print(
        f"\nВсего запусков: {len(rows)} | TG сред.: {fmt(tg, 1)} t/s "
        f"| mean len сред.: {fmt(ml)} | принятие (взвеш.): "
        + ("-" if not tot_g else f"{100.0 * tot_a / tot_g:.1f}%")
    )


if __name__ == "__main__":
    main()
