#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Разбор «мусора» в сохранённых ответах quality.py: печатает проблемные токены
с кодами символов. Запуск: python bench/quality/inspect_junk.py <папка raw> [> файл]"""

import os
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quality import char_script, EN_STOP  # noqa: E402

UKR = set("іїєґІЇЄҐ")


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".txt"):
            continue
        path = os.path.join(folder, name)
        text = open(path, encoding="utf-8").read()
        body = "\n".join(
            ln for ln in text.splitlines() if not ln.startswith("###")
        ).strip()
        bad = []
        for w in body.split():
            core = w.strip(".,!?;:()[]{}«»\"'—–-…*_`|>&")
            if not core:
                continue
            scripts = {char_script(c) for c in core} - {None}
            lat = "lat" in scripts
            cyr = "cyr" in scripts
            weird = [
                c
                for c in core
                if char_script(c) not in ("cyr", "lat")
                and unicodedata.category(c).startswith("L")
            ]
            if (
                (lat and cyr)
                or (lat and core.lower() in EN_STOP)
                or weird
                or any(c in UKR for c in core)
            ):
                info = ",".join(f"{c}=U+{ord(c):04X}" for c in weird)
                bad.append(f"{core}  [{info or 'mix/stop'}]")
        if bad:
            print(f"=== {name}")
            for b in bad:
                print("   " + b)


if __name__ == "__main__":
    main()
