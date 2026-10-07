#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка ссылок на файлы проекта в текстовых артефактах (.md, .bat).

Ищет токены вида `docs\...\*.md`, `launch\...\*.bat`, `bench\...\*.json`
(в косых и обратных слэшах), а также относительные пути с `..\\`, и проверяет,
что файл существует. Токены с масками (`*`), плейсхолдерами (`<...>`, `${...}`)
и известные внешние пути пропускаются.

Запуск (интерпретатором venv):
  .venv\\Scripts\\python.exe bench\\check_links.py
Вывод: список отсутствующих файлов + итог; код возврата 1 при проблемах.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKIP_DIRS = {
    ".git",
    ".venv",
    "downloads",
    "logs",
    "__pycache__",
    ".playwright-mcp",
    ".ruff_cache",
}
EXTS = {".md", ".bat", ".json"}
ROOTS = ("docs", "launch", "bench")

# Внешние пути (документация llama.cpp), которые нельзя резолвить от корня проекта.
ALLOW = {"docs/speculative.md"}

TOKEN = re.compile(
    r"(?:\.\.[\\/])*(?:docs|launch|bench)[\\/][^\s`\"'()<>\[\]]+?\.(?:md|bat|json)(?![\w])"
)
BAD_CHARS = set("*<>$")


def iter_text_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in (".md", ".bat"):
                yield os.path.join(dirpath, fn)


def main():
    missing = []
    checked = 0
    for path in iter_text_files():
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in TOKEN.finditer(text):
            raw = m.group(0)
            if any(c in raw for c in BAD_CHARS) or "${" in raw:
                continue
            norm = raw.replace("\\", "/")
            if norm in ALLOW:
                continue
            if raw.startswith(".."):
                base = os.path.dirname(path)
            else:
                base = ROOT
            target = os.path.normpath(os.path.join(base, raw.replace("/", os.sep)))
            checked += 1
            if not os.path.isfile(target):
                rel = os.path.relpath(path, ROOT)
                missing.append(f"{rel}: {raw}")

    for line in missing:
        print("НЕТ ФАЙЛА:", line)
    print(f"Проверено ссылок: {checked}, отсутствует: {len(missing)}")
    print("ИТОГ:", "все ссылки найдены" if not missing else f"проблем: {len(missing)}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
