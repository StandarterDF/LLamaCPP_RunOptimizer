#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Быстрый статический профиль GGUF-токенизатора под русский язык.
Читает только словарь (метаданные, без весов) и считает:
  * долю кириллических и чужих токенов;
  * длину «русских» кусков (сколько токенов из 4+ букв — признак хорошего покрытия);
  * оценку сжатия русского текста (символов на токен) жадным матчем;
  * долю байтового фолбэка (символы, которых нет в словаре).
Чем выше сжатие и доля длинных кириллических токенов и меньше фолбэка —
тем меньше риск, что модель «рассыпется» на русском.

Запуск:
  python bench/quality/tokenizer_profile.py <model1.gguf> [model2.gguf ...]
"""

import collections
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gguf_vocab import read_tokens, script_of  # noqa: E402

# Текст-образец для оценки сжатия (живой русский, ~1000 символов).
SAMPLE = (
    "Поздний вечер. Ария заходит в таверну после недели в дороге и чувствует, "
    "как мокрая одежда липнет к спине. Снаружи льёт дождь, пахнет дымом и мокрой "
    "шерстью. Она оглядывает зал: косые взгляды, приглушённые разговоры, тусклый "
    "свет свечей дрожит на стенах. Девушка не любит магов и не доверяет знати, "
    "потому что слишком хорошо помнит, чем заканчивается доверие. Наёмница "
    "медленно идёт к стойке, считая выходы и руки сидящих. Трактирщик молчит, "
    "протирает кружку и ждёт заказ. В воздухе висит напряжение, и кажется, что "
    "каждый здесь знает что-то, чего не говорит вслух. Она усмехается и заказывает "
    "самого крепкого пойла, которое найдётся за этой грязной стойкой."
)


def bytes_to_unicode():
    bs = (
        list(range(ord("!"), ord("~") + 1))
        + list(range(ord("\u00a1"), ord("\u00ac") + 1))
        + list(range(ord("\u00ae"), ord("\u00ff") + 1))
    )
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, [chr(c) for c in cs]))


B2U = bytes_to_unicode()
U2B = {v: k for k, v in B2U.items()}


def decode_piece(p):
    if "\u2581" in p:  # SentencePiece
        return p.replace("\u2581", " ")
    if p and all(c in U2B for c in p):  # GPT-2 byte-level BPE
        return bytes(U2B[c] for c in p).decode("utf-8", "replace")
    return p


def detect_style(tokens):
    sp = sum(1 for t in tokens if "\u2581" in t)
    bpe = sum(1 for t in tokens if "\u0120" in t)
    if sp > 50:
        return "sp"
    if bpe > 50:
        return "bpe"
    return "sp"


def greedy_compress(tokens, style, text):
    tset = set(tokens)
    if style == "sp":
        t = "\u2581" + text.replace(" ", "\u2581")
    else:
        t = "".join(B2U[b] for b in (" " + text).encode("utf-8"))
    maxlen = min(24, max((len(x) for x in tset), default=1))
    i = 0
    n_tok = 0
    fallback = 0
    while i < len(t):
        matched = 0
        for L in range(min(maxlen, len(t) - i), 0, -1):
            if t[i : i + L] in tset:
                matched = L
                break
        if matched:
            i += matched
        else:
            i += 1
            fallback += 1
        n_tok += 1
    return len(text), n_tok, fallback


def profile(path):
    toks = read_tokens(path)
    style = detect_style(toks)
    n = len(toks)
    stats = collections.Counter()
    cyr_len = collections.Counter()
    byte_tokens = 0
    for p in toks:
        if p.startswith("<0x") and p.endswith(">") and len(p) == 6:
            byte_tokens += 1
            continue
        text = decode_piece(p)
        scripts = {script_of(c) for c in text if c.isalpha()}
        has_cyr = "cyr" in scripts
        foreign = scripts - {"cyr", "lat"}
        if has_cyr:
            stats["has_cyr"] += 1
            core = "".join(c for c in text if c.isalpha())
            if all(script_of(c) == "cyr" for c in core) and core:
                stats["pure_cyr"] += 1
                cyr_len[len(core)] += 1
        if foreign:
            stats["foreign"] += 1
        if scripts and not has_cyr:
            stats["no_cyr_letters"] += 1
    chars, n_tok, fallback = greedy_compress(toks, style, SAMPLE)
    return {
        "path": path,
        "style": style,
        "n_vocab": n,
        "pct_has_cyr": round(100 * stats["has_cyr"] / n, 2),
        "pct_pure_cyr": round(100 * stats["pure_cyr"] / n, 2),
        "pct_foreign": round(100 * stats["foreign"] / n, 2),
        "byte_tokens": byte_tokens,
        "cyr_ge4": sum(v for k, v in cyr_len.items() if k >= 4),
        "cyr_ge6": sum(v for k, v in cyr_len.items() if k >= 6),
        "max_cyr_len": max(cyr_len) if cyr_len else 0,
        "chars_per_token": round(chars / n_tok, 2),
        "fallback_pct": round(100 * fallback / n_tok, 1),
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    rows = []
    for path in sys.argv[1:]:
        try:
            rows.append(profile(path))
        except Exception as e:
            rows.append({"path": path, "error": f"{type(e).__name__}: {e}"})
    hdr = (
        "| Модель | Тип | Словарь | Кириллица % | Чисто-кир. % | Чужое % | Кусков ≥4 | ≥6 | Макс | Симв/токен | Фолбэк % |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    )
    print("\n".join(hdr))
    for r in rows:
        name = os.path.splitext(os.path.basename(r["path"]))[0][:42]
        if "error" in r:
            print(f"| {name} | — | ОШИБКА: {r['error']} |")
            continue
        print(
            "| {n} | {st} | {v} | {hc} | {pc} | {fo} | {g4} | {g6} | {mx} | {cpt} | {fb} |".format(
                n=name,
                st=r["style"],
                v=r["n_vocab"],
                hc=r["pct_has_cyr"],
                pc=r["pct_pure_cyr"],
                fo=r["pct_foreign"],
                g4=r["cyr_ge4"],
                g6=r["cyr_ge6"],
                mx=r["max_cyr_len"],
                cpt=r["chars_per_token"],
                fb=r["fallback_pct"],
            )
        )


if __name__ == "__main__":
    main()
