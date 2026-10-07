#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сводка metrics.jsonl от rp_quality.py: агрегат по конфигам.

Запуск: python bench/quality/aggregate.py <metrics.jsonl>
Читает файл, даже если он ещё дописывается (неполные строки пропускаются).
"""

import json
import os
import sys
from collections import OrderedDict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def avg(vals):
    v = [x for x in vals if isinstance(x, (int, float))]
    return sum(v) / len(v) if v else 0.0


def main():
    path = sys.argv[1]
    groups = OrderedDict()
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if "error" in r:
            continue
        groups.setdefault(r["config"], []).append(r)

    cols = [
        ("Чисто%", lambda rs: 100 * sum(1 for r in rs if r.get("clean")) / len(rs)),
        ("Чужой/1k", lambda rs: avg([r.get("foreign_per_1k") for r in rs])),
        ("CJK/1k", lambda rs: avg([r.get("cjk_per_1k") for r in rs])),
        ("EN-стоп", lambda rs: avg([r.get("latin_stop") for r in rs])),
        ("Смеш", lambda rs: avg([r.get("mixed_words") for r in rs])),
        ("UKR", lambda rs: avg([r.get("ukr_letters") for r in rs])),
        ("Junk/1k", lambda rs: avg([r.get("junk_per_1k") for r in rs])),
        ("F-масса", lambda rs: avg([r.get("foreign_mass_mean") for r in rs])),
        ("rep8", lambda rs: avg([r.get("rep8_dup") for r in rs])),
        ("Cyr%", lambda rs: 100 * avg([r.get("cyr_share") for r in rs])),
        ("TG", lambda rs: avg([r.get("tg_t_s") for r in rs])),
    ]
    hdr = "| Конфиг | N | " + " | ".join(c[0] for c in cols) + " |"
    sep = "| --- | ---: | " + " | ".join("---:" for _ in cols) + " |"
    print(hdr)
    print(sep)
    for name, rs in groups.items():
        row = (
            f"| {name} | {len(rs)} | "
            + " | ".join(f"{c[1](rs):.2f}" for c in cols)
            + " |"
        )
        print(row)


if __name__ == "__main__":
    main()
