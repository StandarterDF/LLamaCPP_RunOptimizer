#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Читает словарь из GGUF (только метаданные, без загрузки весов) и собирает
«чёрный список» токенов для logit_bias: чужие алфавиты (CJK, хангыль и т.п.)
и подозрительные чисто-латинские служебные слова.

Печатает статистику и (опционально) сохраняет JSON со списком id.

Запуск:
  python bench/quality/gguf_vocab.py "<model.gguf>" [--save blacklist.json]
"""

import argparse
import json
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TYPE_SIZES = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}
EN_STOP = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "that",
    "this",
    "these",
    "those",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "of",
    "to",
    "in",
    "on",
    "at",
    "by",
    "for",
    "with",
    "from",
    "as",
    "it",
    "its",
    "you",
    "he",
    "she",
    "they",
    "we",
    "not",
    "no",
    "yes",
    "do",
    "does",
    "did",
    "have",
    "has",
    "had",
    "will",
    "would",
    "can",
    "could",
    "should",
    "if",
    "then",
    "than",
    "so",
}


def script_of(ch):
    o = ord(ch)
    if (
        0x0400 <= o <= 0x052F
        or 0x2DE0 <= o <= 0x2DFF
        or 0xA640 <= o <= 0xA69F
        or 0x1C80 <= o <= 0x1C8F
    ):
        return "cyr"
    if (
        0x0041 <= o <= 0x005A
        or 0x0061 <= o <= 0x007A
        or 0x00C0 <= o <= 0x024F
        or 0x1E00 <= o <= 0x1EFF
        or 0x2C60 <= o <= 0x2C7F
        or 0xA720 <= o <= 0xA7FF
    ):
        return "lat"
    if (
        0x4E00 <= o <= 0x9FFF
        or 0x3400 <= o <= 0x4DBF
        or 0xF900 <= o <= 0xFAFF
        or 0x20000 <= o <= 0x2FA1F
    ):
        return "han"
    if 0x3040 <= o <= 0x30FF or 0x31F0 <= o <= 0x31FF:
        return "kana"
    if (
        0xAC00 <= o <= 0xD7AF
        or 0x1100 <= o <= 0x11FF
        or 0x3130 <= o <= 0x318F
        or 0xA960 <= o <= 0xA97F
    ):
        return "hangul"
    if 0x0E00 <= o <= 0x0E7F:
        return "thai"
    if (
        0x0600 <= o <= 0x06FF
        or 0x0750 <= o <= 0x077F
        or 0xFB50 <= o <= 0xFDFF
        or 0xFE70 <= o <= 0xFEFF
    ):
        return "arab"
    if 0x0590 <= o <= 0x05FF:
        return "hebr"
    if 0x0900 <= o <= 0x097F:
        return "deva"
    return "other" if ch.isalpha() else None


def read_str(f):
    n = struct.unpack("<Q", f.read(8))[0]
    return f.read(n).decode("utf-8", "replace")


def skip_value(f, t):
    if t == 8:
        read_str(f)
    elif t == 9:
        et = struct.unpack("<I", f.read(4))[0]
        cnt = struct.unpack("<Q", f.read(8))[0]
        for _ in range(cnt):
            skip_value(f, et)
    elif t in TYPE_SIZES:
        f.read(TYPE_SIZES[t])
    else:
        raise ValueError(f"unknown gguf type {t}")


def read_tokens(path):
    with open(path, "rb") as f:
        if f.read(4) != b"GGUF":
            raise ValueError("not a GGUF file")
        struct.unpack("<I", f.read(4))[0]
        struct.unpack("<Q", f.read(8))[0]  # tensor count
        n_kv = struct.unpack("<Q", f.read(8))[0]
        for _ in range(n_kv):
            key = read_str(f)
            t = struct.unpack("<I", f.read(4))[0]
            if key == "tokenizer.ggml.tokens":
                et = struct.unpack("<I", f.read(4))[0]
                cnt = struct.unpack("<Q", f.read(8))[0]
                assert et == 8, f"tokens elem type {et}"
                return [read_str(f) for _ in range(cnt)]
            skip_value(f, t)
    raise ValueError("tokenizer.ggml.tokens not found")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--save", default=None)
    a = ap.parse_args()
    toks = read_tokens(a.model)
    print(f"Токенов всего: {len(toks)}")

    by_script = {}
    foreign_ids = []
    for i, piece in enumerate(toks):
        text = piece.replace("\u2581", " ")
        scripts = {script_of(c) for c in text if c.isalpha()}
        for s in scripts:
            if s and s not in ("cyr", "lat"):
                by_script.setdefault(s, []).append((i, piece))
                foreign_ids.append(i)

    print("Чужие алфавиты (поверхностные токены):")
    for s, items in sorted(by_script.items()):
        uniq = sorted({i for i, _ in items})
        print(f"  {s:8} {len(uniq):>7} id   примеры: {[p for _, p in items[:6]]}")

    stop_ids = []
    for i, piece in enumerate(toks):
        text = piece.replace("\u2581", " ").strip().lower()
        if text in EN_STOP and all(script_of(c) == "lat" for c in text if c.isalpha()):
            stop_ids.append(i)
    print(f"Чисто-латинских англ. служебных токенов: {len(stop_ids)}")
    print(f"  примеры: {[(i, toks[i]) for i in stop_ids[:20]]}")

    if a.save:
        data = {
            "model": a.model,
            "n_vocab": len(toks),
            "foreign_script_ids": sorted(set(foreign_ids)),
            "english_stopword_ids": sorted(set(stop_ids)),
        }
        with open(a.save, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"Сохранено: {a.save}")


if __name__ == "__main__":
    main()
