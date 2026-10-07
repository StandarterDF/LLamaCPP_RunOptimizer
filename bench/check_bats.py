#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка .bat-конфигов: раскрывает переменные путей и проверяет, что файлы существуют.

Читает переменные из `config.local.bat` (или `config.example.bat`), затем для каждого
`.bat` в `launch/` подставляет значения и проверяет пути из `-m`, `-md`,
`--chat-template-file`, `--mmproj`.

Запуск: python bench/check_bats.py
"""

import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SET_RE = re.compile(r'set\s+"([^"]+)=([^"]*)"')


def read_sets(path: pathlib.Path) -> dict:
    values = {}
    if not path.exists():
        return values
    text = path.read_text(encoding="utf-8", errors="replace")
    for key, val in SET_RE.findall(text):
        if "%%" in val or "%~" in val:
            continue  # динамические значения (for %%~dpI и т.п.) пропускаем
        values[key] = val
    return values


def expand(value: str, env: dict, depth: int = 0) -> str:
    if depth > 5:
        return value

    def sub(m):
        return expand(env.get(m.group(1), m.group(0)), env, depth + 1)

    return re.sub(r"%([A-Za-z_][A-Za-z0-9_]*)%", sub, value)


def resolve_env() -> dict:
    env = read_sets(ROOT / "config.example.bat")
    env.update(read_sets(ROOT / "config.local.bat"))
    if not env.get("LLAMA_DIR") and env.get("LLAMA_SERVER"):
        env["LLAMA_DIR"] = str(pathlib.Path(env["LLAMA_SERVER"]).parent)
    return env


def main():
    env = resolve_env()
    env["PROJECT_DIR"] = str(ROOT)
    check_keys = {
        "-m": "Модель",
        "-md": "Драфт",
        "--chat-template-file": "Шаблон",
        "--mmproj": "Проектор",
    }
    bad = 0
    for bat in sorted((ROOT / "launch").rglob("*.bat")):
        rel = os.path.relpath(ROOT, bat.parent)
        local = dict(env)
        local["PROJECT_DIR"] = str((bat.parent / rel).resolve())
        local.update(
            {k: v for k, v in read_sets(bat).items() if "%%" not in v and "%~" not in v}
        )
        text = bat.read_text(encoding="utf-8", errors="replace")
        checks = []
        for flag, label in check_keys.items():
            m = re.search(rf'{re.escape(flag)}\s+"([^"]+)"', text)
            if not m:
                continue
            raw = m.group(1)
            value = expand(raw, local)
            if "%" in value:
                checks.append(f"{label}: НЕ РАСКРЫТО {value}")
                bad += 1
            elif not pathlib.Path(value).exists():
                checks.append(f"{label}: НЕТ ФАЙЛА {value}")
                bad += 1
        status = "OK" if not checks else "; ".join(checks)
        print(f"{str(bat.relative_to(ROOT)):55s} {status}")
    print("ИТОГ:", "все пути найдены" if not bad else f"проблем: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
