#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Санитайзер артефактов: заменяет личные пути на плейсхолдеры перед публикацией.

Пути берутся из `bench/env.local.json` (ключи LLAMA_SERVER, LLAMA_DIR, MODELS_DIR, PROJECT_DIR)
и заменяются в файлах на `<LLAMA_SERVER>`, `<LLAMA_DIR>`, `<MODELS_DIR>`, `<PROJECT_DIR>`.

Запуск:
  python bench/sanitize.py                  # bench/runs и bench/skill-selftest/runs
  python bench/sanitize.py <файлы...>       # конкретные файлы

Рекомендация: запускать перед каждым коммитом, если гонялись новые бенчмарки.
"""

import codecs
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENV = ROOT / "bench" / "env.local.json"
KEYS = ["LLAMA_SERVER", "LLAMA_DIR", "MODELS_DIR", "PROJECT_DIR"]
EXTS = {".log", ".jsonl", ".json", ".txt"}


def read_text_any(path):
    """Читает текст, определяя кодировку по BOM (PowerShell пишет UTF-16)."""
    data = path.read_bytes()
    if data.startswith(codecs.BOM_UTF16_LE) or data.startswith(codecs.BOM_UTF16_BE):
        return data.decode("utf-16"), "utf-16"
    if data.startswith(codecs.BOM_UTF8):
        return data.decode("utf-8-sig"), "utf-8-sig"
    return data.decode("utf-8", "replace"), "utf-8"


def load_pairs():
    cfg = json.loads(ENV.read_text(encoding="utf-8"))
    pairs = []
    for key in KEYS:
        value = cfg.get(key)
        if not value:
            continue
        ph = f"<{key}>"
        pairs.append((value, ph))  # C:\path
        pairs.append((value.replace("\\", "\\\\"), ph))  # C:\\path (в JSON)
        pairs.append((value.replace("\\", "/"), ph))  # C:/path
        pairs.sort(key=lambda item: len(item[0]), reverse=True)
    return pairs


def sanitize_text(text: str, pairs) -> str:
    for src, dst in pairs:
        text = text.replace(src, dst)
    return text


def main():
    args = sys.argv[1:]
    targets = []
    if args:
        targets = [pathlib.Path(a) for a in args]
    else:
        for folder in (
            ROOT / "bench" / "runs",
            ROOT / "bench" / "quality" / "runs",
            ROOT / "bench" / "skill-selftest" / "runs",
        ):
            if folder.exists():
                targets += [p for p in folder.rglob("*") if p.suffix.lower() in EXTS]
    pairs = load_pairs()
    changed = 0
    for path in targets:
        try:
            text, enc = read_text_any(path)
        except Exception:
            continue
        new = sanitize_text(text, pairs)
        if new != text:
            path.write_text(new, encoding=enc)
            changed += 1
    print(f"Санитизировано файлов: {changed}")


if __name__ == "__main__":
    main()
