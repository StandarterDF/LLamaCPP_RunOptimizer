#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Читалка метаданных GGUF (чистый stdlib) + расчёт размера KV-кэша.

Зачем: чтобы планировать эксперименты по KV-кэшу (f16/q8_0/q4_0...) не поднимая
llama-server. Скрипт достаёт параметры архитектуры из заголовка GGUF и считает,
сколько памяти займёт KV-кэш при разных типах квантования и длинах контекста.

Учитывает особенности современных архитектур:
  * GQA/MQA — число K/V-голов может быть меньше числа Q-голов;
  * sliding-window attention (Gemma-4): локальные слои хранят только окно (1024),
    полные слои — весь контекст; у них разная размерность K/V;
  * гибрид linear/full attention (Qwen3.5/3.6): линейные слои KV-кэша не имеют.

Использование:
  .venv\\Scripts\\python.exe bench\\gguf_info.py "<путь к модели>.gguf"
  .venv\\Scripts\\python.exe bench\\gguf_info.py "<модель>.gguf" --json
  .venv\\Scripts\\python.exe bench\\gguf_info.py "<модель>.gguf" --contexts 8192,32768,131072

Только чтение; ничего не запускает и не меняет.
"""

import argparse
import json
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# GGUF value types (0..12)
FMT = {
    0: "<B",
    1: "<b",
    2: "<H",
    3: "<h",
    4: "<I",
    5: "<i",
    6: "<f",
    7: "<B",
    8: None,
    9: None,
    10: "<Q",
    11: "<q",
    12: "<d",
}

# Байт на элемент KV по типам llama.cpp (данные + блок scales):
# q8_0: 8 бит + 2 байта/32 значения = 8.5 бита; q4_0: 4.5; f16 — эталон.
KV_BYTES = {
    "f32": 4.0,
    "f16": 2.0,
    "bf16": 2.0,
    "q8_0": 8.5 / 8,
    "q5_1": 6.0 / 8,
    "q5_0": 5.5 / 8,
    "q4_1": 5.0 / 8,
    "q4_0": 4.5 / 8,
    "iq4_nl": 4.5 / 8,
}


class Reader:
    def __init__(self, f):
        self.f = f

    def read(self, n):
        b = self.f.read(n)
        if len(b) != n:
            raise EOFError("неожиданный конец файла")
        return b

    def u32(self):
        return struct.unpack("<I", self.read(4))[0]

    def u64(self):
        return struct.unpack("<Q", self.read(8))[0]

    def string(self):
        return self.read(self.u64()).decode("utf-8", "replace")

    def value(self, vtype):
        if vtype == 8:
            return self.string()
        if vtype == 9:
            et = self.u32()
            n = self.u64()
            return [self.value(et) for _ in range(n)]
        fmt = FMT.get(vtype)
        if fmt is None:
            raise ValueError(f"неизвестный тип GGUF: {vtype}")
        return struct.unpack(fmt, self.read(struct.calcsize(fmt)))[0]


def read_metadata(path):
    with open(path, "rb") as f:
        r = Reader(f)
        if r.read(4) != b"GGUF":
            raise ValueError("это не GGUF-файл")
        version, n_tensors, n_kv = r.u32(), r.u64(), r.u64()
        meta = {}
        for _ in range(n_kv):
            key = r.string()
            meta[key] = r.value(r.u32())  # vtype читается до значения
    return {"version": version, "n_tensors": n_tensors, "metadata": meta}


def _get(meta, *keys, default=None):
    for k in keys:
        if k in meta:
            return meta[k]
    return default


def _as_list(v, n):
    if isinstance(v, list):
        return v
    return [v] * n


def _at(seq, i, n):
    return (
        seq[i]
        if isinstance(seq, list) and i < len(seq)
        else (seq if not isinstance(seq, list) else seq[-1])
    )


def analyze(path):
    info = read_metadata(path)
    m = info["metadata"]
    arch = _get(m, "general.architecture", default="?")
    p = f"{arch}."
    n_layer = _get(m, p + "block_count") or 0
    n_head = _get(m, p + "attention.head_count")
    n_embd = _get(m, p + "embedding_length")
    n_kv = _get(m, p + "attention.head_count_kv")

    k_len = _get(m, p + "attention.key_length")
    v_len = _get(m, p + "attention.value_length")
    k_swa = _get(m, p + "attention.key_length_swa")
    v_swa = _get(m, p + "attention.value_length_swa")
    swa = _get(m, p + "attention.sliding_window")
    pattern = _get(m, p + "attention.sliding_window_pattern")
    layer_types = _get(m, p + "attention.layer_types")

    if k_len is None and n_head and n_embd:
        k_len = n_embd // n_head
    if v_len is None:
        v_len = k_len
    if k_swa is None:
        k_swa, v_swa = k_len, v_len

    out = {
        "file": path,
        "gguf_version": info["version"],
        "architecture": arch,
        "name": _get(m, "general.name"),
        "n_layer": n_layer,
        "n_embd": n_embd,
        "n_head": n_head,
        "n_head_kv": n_kv,
        "key_length": k_len,
        "value_length": v_len,
        "key_length_swa": k_swa,
        "value_length_swa": v_swa,
        "sliding_window": swa,
        "sliding_window_pattern": pattern,
        "n_ctx_train": _get(m, p + "context_length"),
    }

    # Раскладка слоёв: сколько с полным вниманием / окном / linear.
    if isinstance(pattern, list) and pattern:
        out["n_full_attn"] = sum(1 for x in pattern if x == 0)
        out["n_swa_layers"] = sum(1 for x in pattern if x == 1)
    elif isinstance(layer_types, list) and layer_types:
        out["layer_types"] = layer_types
        out["n_full_attn"] = sum(
            1 for x in layer_types if x in ("full_attention", "attention")
        )
        out["n_swa_layers"] = sum(1 for x in layer_types if "slid" in str(x))
        out["n_linear"] = sum(1 for x in layer_types if "linear" in str(x))
    else:
        out["n_full_attn"] = n_layer
        out["n_swa_layers"] = 0

    # Кол-во уникальных KV-«полос» (у Gemma-4 global-слои по 4 головы, local — по 16).
    kvg = n_kv if not isinstance(n_kv, list) else max(set(n_kv), key=n_kv.count)
    out["n_head_kv_global"] = kvg
    if isinstance(n_kv, list):
        uniq = sorted(set(n_kv))
        out["n_head_kv_values"] = uniq
    return out


def kv_layout(info):
    """Список (n_kv_heads, k_dim, v_dim, window|None) по слоям."""
    n = info["n_layer"]
    n_kv = _as_list(info["n_head_kv"], n)
    pattern = info.get("sliding_window_pattern")
    lay = []
    for i in range(n):
        is_swa = bool(pattern[i]) if isinstance(pattern, list) else False
        nk = n_kv[i] if isinstance(info["n_head_kv"], list) else info["n_head_kv"]
        if is_swa:
            lay.append(
                (
                    nk,
                    info["key_length_swa"],
                    info["value_length_swa"],
                    info["sliding_window"] or 0,
                )
            )
        else:
            lay.append((nk, info["key_length"], info["value_length"], None))
    return lay


def kv_bytes(info, ctx, dtype):
    b = KV_BYTES.get(dtype, 2.0)
    total = 0.0
    for nk, kd, vd, win in kv_layout(info):
        eff = min(ctx, win) if win else ctx
        total += nk * (kd + vd) * b * eff
    return total


def report(info, contexts, dtypes):
    print(f"Файл: {info['file']}")
    print(
        f"  архитектура : {info['architecture']} (GGUF v{info['gguf_version']})"
        f"   name: {info['name']}"
    )
    print(
        f"  слоёв       : {info['n_layer']}   n_embd {info['n_embd']}   "
        f"Q-голов {info['n_head']}"
    )
    print(f"  K/V головы  : {info['n_head_kv']}")
    print(
        f"  размерности : global K/V {info['key_length']}/{info['value_length']}, "
        f"SWA K/V {info['key_length_swa']}/{info['value_length_swa']}, "
        f"окно {info['sliding_window']}"
    )
    print(
        f"  слои        : полных {info.get('n_full_attn')} / окна "
        f"{info.get('n_swa_layers')} / linear {info.get('n_linear', 0)}"
    )
    print(
        f"  контекст    : {info['n_ctx_train']}   "
        f"KV-головы по слоям {info.get('n_head_kv_values', info['n_head_kv'])}"
    )
    print()
    print("KV-кэш (МиБ) по длине контекста и типу K/V:")
    print("  ctx".ljust(10) + "".join(f"{d:>10}" for d in dtypes))
    for ctx in contexts:
        row = f"  {ctx:<8}"
        for d in dtypes:
            row += f"{kv_bytes(info, ctx, d) / 2**20:>10.0f}"
        print(row)


def main():
    ap = argparse.ArgumentParser(description="GGUF metadata + KV cache size (stdlib)")
    ap.add_argument("model")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--contexts", default="8192,32768,65536,131072")
    ap.add_argument("--dtypes", default="f16,q8_0,q4_1,q4_0")
    a = ap.parse_args()
    info = analyze(a.model)
    if a.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return
    report(
        info,
        [int(x) for x in a.contexts.split(",") if x.strip()],
        [x.strip() for x in a.dtypes.split(",") if x.strip()],
    )


if __name__ == "__main__":
    main()
