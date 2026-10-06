#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сводит голоса панели судей (попарное A/B) в общий итог.

Вход: каталог с .txt-файлами — по одному на судью (имя файла = имя судьи),
строки в формате judge_pack.py:
  <режим>|<сцена>|<сид>|overall=<A|B|T>|ум=<A|B|T>|...|повторы=<A|B|T>

Запуск:
  .venv\\Scripts\\python.exe bench\\quality\\panel_score.py bench\\quality\\runs\\_panel\\votes
"""

import os
import re
import sys

AXES = [
    "ум",
    "память",
    "персонаж",
    "инструкция",
    "инициатива",
    "русский",
    "проза",
    "повторы",
]
VAL = re.compile(r"(?i)\b([ABT])\b")


def parse_line(line):
    if "|" not in line:
        return None
    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 3:
        return None
    mode, scen, seed = parts[0], parts[1], parts[2]
    vals = {}
    for p in parts[3:]:
        if "=" not in p:
            continue
        k, v = p.split("=", 1)
        k = k.strip().lower()
        v = v.strip().upper()[:1]
        if v in ("A", "B", "T"):
            vals[k] = v
    if "overall" not in vals:
        return None
    return mode, scen, seed, vals


def main():
    src = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "quality",
            "runs",
            "_panel",
            "votes",
        )
    )
    judges = {}
    for fn in sorted(os.listdir(src)):
        if not fn.endswith(".txt"):
            continue
        name = os.path.splitext(fn)[0]
        rows = []
        for ln in open(os.path.join(src, fn), encoding="utf-8", errors="replace"):
            r = parse_line(ln)
            if r:
                rows.append(r)
        if rows:
            judges[name] = rows

    if not judges:
        print("нет распознанных строк — проверь формат голосов")
        return

    print(f"{'судья':<16}{'пар':>4}   overall A/B/T")
    for name, rows in judges.items():
        c = {"A": 0, "B": 0, "T": 0}
        for _, _, _, v in rows:
            c[v["overall"]] += 1
        print(f"{name:<16}{len(rows):>4}   {c['A']}/{c['B']}/{c['T']}")

    # Свод по всем парам всех судей: для каждой пары — сколько раз выбрали A/B/T
    allvals = {ax: {"A": 0, "B": 0, "T": 0} for ax in AXES + ["overall"]}
    total = 0
    for rows in judges.values():
        for _, _, _, v in rows:
            total += 1
            allvals["overall"][v["overall"]] += 1
            for ax in AXES:
                if ax in v:
                    allvals[ax][v[ax]] += 1

    print(f"\nСвод по {total} голосам ({len(judges)} судей):")
    print(f"{'ось':<12}{'A':>6}{'B':>6}{'T':>6}   доля A   доля B")
    for ax in ["overall"] + AXES:
        c = allvals[ax]
        n = c["A"] + c["B"] + c["T"] or 1
        print(
            f"{ax:<12}{c['A']:>6}{c['B']:>6}{c['T']:>6}   {c['A'] / n:>5.0%}   {c['B'] / n:>5.0%}"
        )
    print(
        "\n(A = модель A, B = модель B; A/B анонимны в пакете — сопоставление знает агент)"
    )


if __name__ == "__main__":
    main()
