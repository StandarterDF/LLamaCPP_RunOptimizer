#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Агрегатор оценок RP-судьи: парсит тексты rp_judge.py и считает средний балл.

Судья (`bench\\quality\\rp_judge.py`) по каждому ответу пишет оси 1-5:
ум, память, персонаж, инструкция, инициатива, русский, проза, повторы.
Скрипт достаёт эти оценки и сводит их по модели и режиму (think/nothink).

Запуск (интерпретатором venv):
  .venv\\Scripts\\python.exe bench\\quality\\judge_score.py bench\\quality\\runs\\rp_judge_b3
"""

import os
import re
import sys

LABELS = [
    "ум",
    "память",
    "персонаж",
    "инструкция",
    "инициатива",
    "русский",
    "проза",
    "повторы",
]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)


def scores_from(chunk):
    m = re.search(r"Оценк", chunk)
    region = chunk[m.start() :] if m else chunk
    region = re.split(r"Итог|Общий вывод|\*\*\*", region)[0]
    sc = {}
    for lab in LABELS:
        mm = re.search(r"(?<![а-яё])" + lab + r"(?![а-яё])\s*[:—\-]?\s*([1-5])", region)
        if mm:
            sc[lab] = int(mm.group(1))
    if len(sc) == len(LABELS):
        return sc
    r2 = re.sub(r"1\s*[-–]\s*5", "", region)
    nums = [int(x) for x in re.findall(r"(?<!\d)([1-5])(?!\d)", r2)]
    if len(nums) >= len(LABELS):
        return {lab: nums[i] for i, lab in enumerate(LABELS)}
    return sc or None


def parse_items(text):
    lines = text.splitlines()
    items, cur = [], []
    for ln in lines:
        s = ln.strip()
        if s.startswith("==="):
            if cur:
                items.append("\n".join(cur))
            cur = [ln]
        elif cur:
            cur.append(ln)
    if cur:
        items.append("\n".join(cur))
    out = []
    for ch in items:
        head = next((l.strip() for l in ch.splitlines() if l.strip()), "")
        sc = scores_from(ch)
        if sc:
            out.append((head, sc))
    return out


def model_mode(fname):
    m = re.search(r"(rp_eval_.+?)_(nothink|think)", fname)
    if m:
        return m.group(1).replace("rp_eval_", ""), m.group(2)
    return fname, "?"


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def main():
    srcs = sys.argv[1:] or [os.path.join(ROOT, "quality", "runs", "rp_judge_b3")]
    paths = []
    for src in srcs:
        paths += [
            os.path.join(src, f) for f in sorted(os.listdir(src)) if f.endswith(".txt")
        ]
    by = {}
    for path in paths:
        mdl, mode = model_mode(os.path.basename(path))
        for head, sc in parse_items(open(path, encoding="utf-8").read()):
            by.setdefault((mdl, mode), []).append(sc)

    hdr = ["ум", "память", "персонаж", "инстр", "иниц", "рус", "проза", "повт"]
    print(
        f"{'model':<14}{'mode':<9}{'N':>3}  "
        + "  ".join(f"{h:>6}" for h in hdr)
        + "   СРЕДНИЙ"
    )
    rows = []
    for (mdl, mode), items in by.items():
        ax = {lab: mean([it[lab] for it in items if lab in it]) for lab in LABELS}
        overall = mean([mean(list(it.values())) for it in items])
        rows.append((mdl, mode, len(items), ax, overall))
    for mdl, mode, n, ax, overall in sorted(rows, key=lambda r: -r[4]):
        vals = "  ".join(f"{ax[l]:>6.2f}" for l in LABELS)
        print(f"{mdl:<14}{mode:<9}{n:>3}  {vals}   {overall:.2f}")

    print("\nСредний по модели (все режимы, все ответы):")
    per_model = {}
    for (mdl, mode), items in by.items():
        per_model.setdefault(mdl, []).extend(items)
    for mdl, items in sorted(
        per_model.items(),
        key=lambda kv: -mean([mean(list(it.values())) for it in kv[1]]),
    ):
        overall = mean([mean(list(it.values())) for it in items])
        ax_text = " ".join(
            f"{lab[:3]}:{mean([it[lab] for it in items if lab in it]):.1f}"
            for lab in LABELS
        )
        print(f"  {mdl:<16} N={len(items):>2}  средний {overall:.2f}   ({ax_text})")


if __name__ == "__main__":
    main()
