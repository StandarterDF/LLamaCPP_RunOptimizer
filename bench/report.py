#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сводка результатов bench.py в markdown (bench/runs/summary.md). Только stdlib."""

import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(ROOT, "runs", "results.jsonl")
OUT = os.path.join(ROOT, "runs", "summary.md")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def avg(vals):
    vals = [v for v in vals if isinstance(v, (int, float))]
    return sum(vals) / len(vals) if vals else None


def main():
    latest = {}
    order = []
    with open(RESULTS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            name = rec["name"]
            if name not in latest:
                order.append(name)
            latest[name] = rec

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

        def fmt(v, nd=0):
            if v is None:
                return "-"
            return round(v, nd) if isinstance(v, float) else v

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
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"Сохранено: {OUT}")


if __name__ == "__main__":
    main()
