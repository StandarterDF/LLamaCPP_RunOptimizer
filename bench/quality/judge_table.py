#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сводка баллов по судьям: per (модель, режим) -> среднее по каждому судье и общее (4 судьи).

Собирает все каталоги `bench\\quality\\runs\\rp_judge*`, раскладывает по судьям и печатает таблицу.
Переиспользует парсер `judge_score.py`.
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # bench
RUNS = os.path.join(HERE, "runs")
sys.path.insert(0, HERE)
import judge_score as js  # noqa: E402

GEMMA_EXTRA = {"rp_judge_b3", "rp_judge_full", "rp_judge_full1", "rp_judge_sg"}


def judge_of(dirname):
    b = os.path.basename(dirname)
    if b == "rp_judge_dsflash_api":
        return "dsflash"
    if b == "rp_judge_dsv4pro_api":
        return "dspro"
    if b.startswith("rp_judge_qwen"):
        return "qwen"
    if b.startswith("rp_judge_gemma") or b in GEMMA_EXTRA:
        return "gemma"
    return None


def main():
    # (judge, model, mode) -> список средних по батчам
    acc = {}
    for d in sorted(glob.glob(os.path.join(RUNS, "rp_judge*"))):
        if not os.path.isdir(d):
            continue
        j = judge_of(d)
        if not j:
            continue
        for f in os.listdir(d):
            if not f.endswith(".txt"):
                continue
            mdl, mode = js.model_mode(f)
            for _head, sc in js.parse_items(
                open(os.path.join(d, f), encoding="utf-8").read()
            ):
                acc.setdefault((j, mdl, mode), []).append(sum(sc.values()) / len(sc))

    # (model, mode) -> {judge: mean}
    per = {}
    for (j, mdl, mode), vals in acc.items():
        per.setdefault((mdl, mode), {})[j] = sum(vals) / len(vals)

    print(
        f"{'model':<24}{'mode':<8}{'gemma':>7}{'qwen':>7}{'dsflash':>8}{'dspro':>7}{'AVG4':>7}{'J':>3}"
    )
    for (mdl, mode), jm in sorted(
        per.items(), key=lambda kv: (kv[0][1], -sum(kv[1].values()) / len(kv[1]))
    ):
        vals = list(jm.values())
        avg = sum(vals) / len(vals)
        f = lambda k: f"{jm[k]:.2f}" if k in jm else "  -  "
        print(
            f"{mdl:<24}{mode:<8}{f('gemma'):>7}{f('qwen'):>7}{f('dsflash'):>8}{f('dspro'):>7}{avg:>7.2f}{len(vals):>3}"
        )


if __name__ == "__main__":
    main()
