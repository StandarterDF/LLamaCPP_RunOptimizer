#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Объективная проверка промптового сравнения KV: сработали ли «критерии» из набора.

Читает suite (у промптов есть поле checks — группы альтернатив, все группы должны
совпасть) и results.json прогона kv_prompts.py; печатает таблицу pass/fail по
каждому (модель, промпт, тип KV). Нужна, чтобы не оценивать ответы только «на глаз».

Запуск: .venv\\Scripts\\python.exe bench\\kv_prompt_checks.py
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def norm(s):
    return (s or "").lower().replace("ё", "е")


def eval_prompt(content, prompt):
    low = norm(content)
    groups = prompt.get("checks", [])
    hits = []
    for grp in groups:
        hits.append(any(norm(alt) in low for alt in grp))
    bullets = len(re.findall(r"(?m)^\s*[—–\-]\s", content))
    bullets_ok = None
    if prompt.get("bullets_min"):
        bullets_ok = bullets >= prompt["bullets_min"]
    return hits, bullets, bullets_ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--suite", default=os.path.join("bench", "suites", "kv", "kv_prompts.json")
    )
    ap.add_argument(
        "--results",
        default=os.path.join("bench", "runs", "kv_prompts", "run", "results.json"),
    )
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    suite = json.load(open(a.suite, encoding="utf-8"))
    prompts = {p["id"]: p for p in suite["prompts"]}
    data = json.load(open(a.results, encoding="utf-8"))

    groups = {}
    for rec in data:
        if rec.get("error"):
            continue
        groups.setdefault(rec["model"], []).append(rec)

    lines = []
    for model, recs in groups.items():
        print("=" * 78)
        print(model)
        lines.append(f"### {model}\n")
        for p in suite["prompts"]:
            pid = p["id"]
            if not p.get("checks") and not p.get("bullets_min"):
                continue
            print(f"  {p['title']}")
            lines.append(f"**{p['title']}**\n")
            lines.append(
                "| KV | "
                + " | ".join(
                    [f"чек{i + 1}" for i in range(len(p.get("checks", [])))]
                    + (["пункты"] if p.get("bullets_min") else [])
                )
                + " |"
            )
            lines.append(
                "|"
                + "---|"
                * (1 + len(p.get("checks", [])) + (1 if p.get("bullets_min") else 0))
            )
            for rec in recs:
                ans = rec.get("answers", {}).get(pid, {})
                hits, bullets, bok = eval_prompt(ans.get("content", ""), p)
                cells = ["✓" if x else "✗" for x in hits]
                if p.get("bullets_min"):
                    cells.append(f"{'✓' if bok else '✗'} ({bullets})")
                kv = rec["kv"]
                print(f"    {kv:9} " + " ".join(cells))
                lines.append(f"| {kv} | " + " | ".join(cells) + " |")
            lines.append("")
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print("записано:", a.out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
