#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сводка results.jsonl (от bench.py) в markdown-таблицу. Только стандартная библиотека.

Запуск:
  python report.py [--runs runs] [--out runs/summary.md]

Для каждого теста (последняя запись с таким именем) считает:
- загрузку, VRAM;
- PP/TG на "short" и "long";
- средний TG и среднее принятие по всем чат-подобным запросам (любой тег кроме short/long).
"""

import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def avg(vals):
    vals = [v for v in vals if isinstance(v, (int, float))]
    return sum(vals) / len(vals) if vals else None


def fmt(v, nd=0):
    if v is None:
        return "-"
    return round(v, nd) if isinstance(v, float) else v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="runs", help="папка с results.jsonl")
    ap.add_argument("--out", default=None, help="куда сохранить markdown")
    a = ap.parse_args()
    results = os.path.join(a.runs, "results.jsonl")
    out = a.out or os.path.join(a.runs, "summary.md")

    latest, order = {}, []
    with open(results, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec["name"] not in latest:
                order.append(rec["name"])
            latest[rec["name"]] = rec

    rows = []
    for name in order:
        r = latest[name]
        runs = r.get("runs", {})
        sh = runs.get("short", {}) or {}
        lo = runs.get("long", {}) or {}
        chats = [
            v
            for k, v in runs.items()
            if k not in ("short", "long") and isinstance(v, dict)
        ]
        chat_tg = avg([v.get("tg_t_s") for v in chats])
        chat_acc = avg([v.get("accept_%") for v in chats])
        chat_n = sum(v.get("predicted_n") or 0 for v in chats)
        rows.append(
            "| {name} | {load} | {vram} | {pp1} | {tg1} | {ppl} | {tgl} | {tgc} | {acc} | {n} |".format(
                name=name,
                load=fmt(r.get("load_s"), 1),
                vram=fmt(r.get("vram_after_load_mb")),
                pp1=fmt(sh.get("pp_t_s")),
                tg1=fmt(sh.get("tg_t_s"), 2),
                ppl=fmt(lo.get("pp_t_s")),
                tgl=fmt(lo.get("tg_t_s"), 1),
                tgc=fmt(chat_tg, 2),
                acc=("-" if chat_acc is None else f"{chat_acc:.1f}%"),
                n=(chat_n or "-"),
            )
        )
    header = (
        "| Тест | Загрузка, с | VRAM, MiB | PP 1.5k | TG 1.5k | PP 12k | TG 12k | TG чат (сред.) | Принятие чат | Сген. чат |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
    )
    text = header + "\n".join(rows) + "\n"
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"Сохранено: {out}")


if __name__ == "__main__":
    main()
