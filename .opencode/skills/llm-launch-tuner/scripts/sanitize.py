#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Санитайзер артефактов: заменяет личные пути на плейсхолдеры перед публикацией.

Пути берутся из `env.local.json` (ключи LLAMA_SERVER, LLAMA_DIR, MODELS_DIR, PROJECT_DIR) —
ищется в текущей папке или рядом со скриптом — и заменяются в файлах на `<LLAMA_SERVER>`,
`<LLAMA_DIR>`, `<MODELS_DIR>`, `<PROJECT_DIR>`.

Запуск:
  python sanitize.py                 # обработает папку runs (если есть)
  python sanitize.py <файл|папка>...

Рекомендация: запускать перед каждым коммитом, если гонялись новые бенчмарки.
"""

import codecs
import json
import os
import pathlib
import sys

KEYS = ["LLAMA_SERVER", "LLAMA_DIR", "MODELS_DIR", "PROJECT_DIR"]
EXTS = {".log", ".jsonl", ".json", ".txt"}


def find_env():
    for base in (os.getcwd(), os.path.dirname(os.path.abspath(__file__))):
        path = os.path.join(base, "env.local.json")
        if os.path.exists(path):
            return path
    return None


def load_pairs():
    env_path = find_env()
    if not env_path:
        return []
    cfg = json.loads(pathlib.Path(env_path).read_text(encoding="utf-8"))
    pairs = []
    for key in KEYS:
        value = cfg.get(key)
        if not value:
            continue
        ph = f"<{key}>"
        pairs.append((value, ph))
        pairs.append((value.replace("\\", "\\\\"), ph))
        pairs.append((value.replace("\\", "/"), ph))
    pairs.sort(key=lambda item: len(item[0]), reverse=True)
    return pairs


def read_text_any(path):
    data = path.read_bytes()
    if data.startswith(codecs.BOM_UTF16_LE) or data.startswith(codecs.BOM_UTF16_BE):
        return data.decode("utf-16"), "utf-16"
    if data.startswith(codecs.BOM_UTF8):
        return data.decode("utf-8-sig"), "utf-8-sig"
    return data.decode("utf-8", "replace"), "utf-8"


def collect(args):
    targets = []
    if not args:
        runs = pathlib.Path("runs")
        if runs.exists():
            targets = [p for p in runs.rglob("*") if p.suffix.lower() in EXTS]
        return targets
    for arg in args:
        path = pathlib.Path(arg)
        if path.is_dir():
            targets += [p for p in path.rglob("*") if p.suffix.lower() in EXTS]
        elif path.is_file():
            targets.append(path)
    return targets


def main():
    pairs = load_pairs()
    if not pairs:
        print("env.local.json не найден — санитизировать нечем.")
        return
    changed = 0
    for path in collect(sys.argv[1:]):
        try:
            text, enc = read_text_any(path)
        except Exception:
            continue
        new = text
        for src, dst in pairs:
            new = new.replace(src, dst)
        if new != text:
            path.write_text(new, encoding=enc)
            changed += 1
    print(f"Санитизировано файлов: {changed}")


if __name__ == "__main__":
    main()
