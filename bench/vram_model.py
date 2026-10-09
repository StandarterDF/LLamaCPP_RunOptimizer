#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Эмпирическая модель памяти llama.cpp: сколько контекста влезает.

Раскладка памяти при загрузке:

    VRAM_after = VRAM_before + W + KV_arch(ctx) + O(ctx, W)

  W        — вес модели (файл GGUF, МиБ);
  KV_arch  — KV-кэш: считается по архитектуре из GGUF (gguf_info.kv_bytes):
             слои с полным вниманием — весь ctx, SWA-слои — min(ctx, окно),
             гибридные (Qwen3.5/3.6 DeltaNet) — только 1 из 4 слоёв;
  O        — накладные: compute-граф, CUDA-контекст, активации; калибруются
             по логам:  O ≈ o0 + o1*(W/1024) + c*ctx   (МиБ).

Тогда при бюджете VRAM:
    ctx_max = корень уравнения  W + KV_arch(ctx) + O(ctx,W) <= VRAM_total - reserve - VRAM_before.

Режимы:
  --fit      калибровка o0,o1,c по bench/runs/**/results.jsonl + отчёт
  --model X  предсказать ctx_max для конкретного GGUF
Только stdlib + bench/gguf_info.py.
"""

import argparse
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import gguf_info  # noqa: E402

MiB = 2**20
# архитектуры с гибридным линейным вниманием: на 3 linear-слоя 1 attention
HYBRID_ARCH = {"qwen35", "qwen36", "qwen3next"}


# ---------------------------------------------------------------------------
def load_env_map():
    env = {"PROJECT_DIR": str(ROOT)}
    try:
        env.update(
            json.loads((ROOT / "bench" / "env.local.json").read_text(encoding="utf-8"))
        )
    except Exception:
        pass
    return env


ENV = load_env_map()


def expand(t):
    if not isinstance(t, str):
        return t
    t = re.sub(
        r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}",
        lambda m: str(ENV.get(m.group(1), m.group(0))),
        t,
    )
    return re.sub(
        r"<([A-Za-z_][A-Za-z0-9_]*)>", lambda m: str(ENV.get(m.group(1), m.group(0))), t
    )


# ---------------------------------------------------------------------------
# KV по архитектуре, с поправкой на гибрид и раздельные K/V
# ---------------------------------------------------------------------------
def arch_attention_layers(info):
    """Сколько слоёв реально держат KV (после поправки на hybrid)."""
    n = info["n_layer"]
    n_full = info.get("n_full_attn", n)
    if (
        info["architecture"] in HYBRID_ARCH
        and n_full == n
        and not info.get("sliding_window_pattern")
    ):
        # GGUF не отдал раскладку: у Qwen3.5/3.6 attention — каждый 4-й слой
        n_full = max(1, n // 4)
    return n_full


def kv_layout_eff(info):
    n = info["n_layer"]
    n_full = arch_attention_layers(info)
    n_kv = info["n_head_kv"]
    nkv = n_kv if isinstance(n_kv, list) else [n_kv] * n
    pattern = info.get("sliding_window_pattern")
    out = []
    if isinstance(pattern, list):
        for i in range(n):
            nk = nkv[i] if i < len(nkv) else nkv[-1]
            if pattern[i]:
                out.append(
                    (
                        nk,
                        info["key_length_swa"],
                        info["value_length_swa"],
                        info.get("sliding_window") or 0,
                    )
                )
            else:
                out.append((nk, info["key_length"], info["value_length"], None))
    else:
        # hybrid без раскладки: первые/каждый 4-й считаем attention-слоем
        for i in range(n):
            nk = nkv[i] if i < len(nkv) else nkv[-1]
            is_attn = (
                (i % 4 == 3)
                if info["architecture"] in HYBRID_ARCH
                else (i < n_full or n_full == n)
            )
            if is_attn:
                out.append((nk, info["key_length"], info["value_length"], None))
    return out


def kv_bytes_sep(info, ctx, tk, tv):
    bk = gguf_info.KV_BYTES.get(tk, 2.0)
    bv = gguf_info.KV_BYTES.get(tv, 2.0)
    total = 0.0
    for nk, kd, vd, win in kv_layout_eff(info):
        eff = min(ctx, win) if win else ctx
        total += nk * (kd * bk + vd * bv) * eff
    return total


# ---------------------------------------------------------------------------
def get_flag(args, *names):
    for i, a in enumerate(args):
        if a in names and i + 1 < len(args):
            return args[i + 1]
    return None


def has_flag(args, *names):
    return any(a in names for a in args)


def parse_entries():
    rows = []
    for path in sorted((ROOT / "bench" / "runs").rglob("results.jsonl")):
        for ln in open(path, encoding="utf-8"):
            ln = ln.strip()
            if not ln:
                continue
            try:
                rec = json.loads(ln)
            except Exception:
                continue
            args = rec.get("args") or []
            model = get_flag(args, "--model") or rec.get("model")
            if not model:
                continue
            model = expand(model)
            ctx = get_flag(args, "-c", "--ctx-size")
            try:
                ctx = int(ctx)
            except Exception:
                ctx = None
            actual = rec.get("n_ctx_actual") or (rec.get("props") or {}).get("n_ctx")
            ctx = actual or ctx
            if not ctx:
                continue
            tk = get_flag(args, "-ctk", "--cache-type-k") or "f16"
            tv = get_flag(args, "-ctv", "--cache-type-v") or tk
            vb, va = rec.get("vram_before_mb"), rec.get("vram_after_load_mb")
            if vb is None or va is None:
                continue
            rows.append(
                {
                    "model": model,
                    "ctx": int(ctx),
                    "tk": tk,
                    "tv": tv,
                    "vb": float(vb),
                    "va": float(va),
                    "spec": get_flag(args, "--spec-type"),
                    "mmproj": has_flag(args, "--mmproj")
                    or has_flag(args, "--no-mmproj-offload"),
                    "ncmoe": get_flag(args, "--n-cpu-moe", "-ncmoe"),
                    "fit": get_flag(args, "--fit"),
                    "src": path.parent.name,
                }
            )
    return rows


def model_size_mib(path):
    try:
        return os.path.getsize(path) / MiB
    except OSError:
        return None


def expert_count(path):
    """0 = не MoE; иначе число экспертов (по метаданным GGUF)."""
    try:
        meta = gguf_info.read_metadata(path)["metadata"]
    except Exception:
        return 0
    for k, v in meta.items():
        if k.endswith("expert_count") and isinstance(v, int):
            return v
    return 0


def solve3(A, b):
    """Решение 3x3 методом Крамера."""

    def det(m):
        return (
            m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
        )

    D = det(A)
    if abs(D) < 1e-9:
        return None
    xs = []
    for c in range(3):
        M = [row[:] for row in A]
        for r in range(3):
            M[r][c] = b[r]
        xs.append(det(M) / D)
    return xs


# ---------------------------------------------------------------------------
def fit():
    rows = parse_entries()
    info_cache, size_cache, moe_cache = {}, {}, {}
    pts, skipped = [], 0
    for r in rows:
        if r["spec"] or r["mmproj"] or r["ncmoe"]:
            continue
        w = size_cache.get(r["model"])
        if w is None:
            w = model_size_mib(r["model"])
            size_cache[r["model"]] = w
        if w is None:
            skipped += 1
            continue
        info = info_cache.get(r["model"])
        if info is None:
            try:
                info = gguf_info.analyze(r["model"])
            except Exception:
                info = False
            info_cache[r["model"]] = info
        if not info:
            continue
        kv = kv_bytes_sep(info, r["ctx"], r["tk"], r["tv"]) / MiB
        if r["model"] not in moe_cache:
            moe_cache[r["model"]] = expert_count(r["model"]) > 0
        pts.append(
            {
                "W": w,
                "ctx": r["ctx"],
                "kv": kv,
                "delta": r["va"] - r["vb"],
                "info": info,
                "tk": r["tk"],
                "tv": r["tv"],
                "model": r["model"],
                "moe": moe_cache[r["model"]],
            }
        )

    print("=" * 86)
    print(
        f"Всего строк с VRAM: {len(rows)}; чистых точек (без spec/mmproj/ncmoe): {len(pts)}; "
        f"пропущено (файла нет): {skipped}"
    )
    print("=" * 86)

    # распределение накладных O = delta - W - KV (без регрессии)
    print("\nO = delta - W - KV_arch(точный), среднее/разброс по группам (модель+KV):")
    print(
        f"{'модель':<40}{'KV':<12}{'N':>3}{'W МиБ':>8}{'KV/ток':>9}{'O ср':>8}{'разб':>7}"
    )
    groups = {}
    for p in pts:
        groups.setdefault((os.path.basename(p["model"]), p["tk"], p["tv"]), []).append(
            p
        )
    for key, g in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        O = [p["delta"] - p["W"] - p["kv"] for p in g]
        # KV/токен из аналитики (наклон)
        g2 = sorted(g, key=lambda p: p["ctx"])
        slope = ""
        if len(g2) >= 2 and g2[-1]["ctx"] != g2[0]["ctx"]:
            dk = (
                kv_bytes_sep(g2[-1]["info"], g2[-1]["ctx"], key[1], key[2])
                - kv_bytes_sep(g2[0]["info"], g2[0]["ctx"], key[1], key[2])
            ) / MiB
            slope = f"{dk * 1024 / (g2[-1]['ctx'] - g2[0]['ctx']):.1f}"
        print(
            f"{key[0][:39]:<40}{key[1] + '/' + key[2]:<12}{len(g):>3}{g[0]['W']:>8.0f}{slope:>9}"
            f"{sum(O) / len(O):>8.0f}{max(O) - min(O):>7.0f}"
        )

    # накладные O: O почти не зависит от веса модели, но резко падает у MoE
    # (compute-граф считает только активных экспертов). Калибруем медианой
    # отдельно для dense и MoE, а не хрупкой линейной регрессией.
    print("\n" + "-" * 86)
    for label, moe in (("dense", False), ("MoE", True)):
        vals = sorted(p["delta"] - p["W"] - p["kv"] for p in pts if p["moe"] == moe)
        if vals:
            med = vals[len(vals) // 2]
            print(
                f"  O[{label:<5}] n={len(vals):>2}  медиана {med:>6.0f} МиБ   "
                f"(разброс {vals[0]:.0f}..{vals[-1]:.0f})"
            )
    print("-" * 86)
    print("\nАрхитектурная часть (точная, из GGUF) — KV на токен, КиБ (ctx>окна):")
    print(f"{'модель':<40}{'attn слоёв':>11}{'f16':>8}{'q8_0':>8}{'q4_0':>8}")
    seen = set()
    for p in pts:
        m = os.path.basename(p["model"])
        if m in seen:
            continue
        seen.add(m)
        info = p["info"]
        row = []
        for dt in ("f16", "q8_0", "q4_0"):
            k = kv_bytes_sep(info, 65536, dt, dt) - kv_bytes_sep(info, 32768, dt, dt)
            row.append(k / 32768)
        print(
            f"{m[:39]:<40}{arch_attention_layers(info):>11}{row[0]:>8.1f}{row[1]:>8.1f}{row[2]:>8.1f}"
        )
    print("\nГотово. Предсказание: --model <gguf> --gpu 16380 --reserve 700\n")


# ---------------------------------------------------------------------------
def predict(model, gpu, reserve, tk, tv, o_dense, o_moe, before):
    info = gguf_info.analyze(model)
    w = model_size_mib(model)
    experts = expert_count(model)
    o = o_moe if experts > 0 else o_dense
    print(
        json.dumps(
            {
                "model": os.path.basename(model),
                "architecture": info["architecture"],
                "weights_MiB": round(w),
                "n_layer": info["n_layer"],
                "attention_layers": arch_attention_layers(info),
                "sliding_window": info.get("sliding_window"),
                "experts": experts,
                "kv_k": tk,
                "kv_v": tv,
                "gpu_MiB": gpu,
                "reserve_MiB": reserve,
                "vram_before_MiB": before,
                "overhead_MiB": round(o),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print(f"\n{'ctx':>8} | {'KV МиБ':>8} | {'O МиБ':>7} | {'W+KV+O':>9} | влезает")
    avail = gpu - reserve - before
    for ctx in (16384, 32768, 49152, 65536, 81920, 98304, 131072, 196608, 262144):
        kv = kv_bytes_sep(info, ctx, tk, tv) / MiB
        total = w + kv + o
        print(
            f"{ctx:>8} | {kv:>8.0f} | {o:>7.0f} | {total:>9.0f} | {'да' if total <= avail else 'нет'}"
        )
    lo, hi, best = 1024, info.get("n_ctx_train") or 262144, 0
    while lo <= hi:
        mid = max(256, (lo + hi) // 2 // 256 * 256)
        kv = kv_bytes_sep(info, mid, tk, tv) / MiB
        if w + kv + o <= avail:
            best, lo = mid, mid + 256
        else:
            hi = mid - 256
    print(
        f"\nМаксимальный контекст (KV {tk}/{tv}, запас {reserve} МиБ): ~{best} токенов"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--model")
    ap.add_argument("--gpu", type=int, default=16380)
    ap.add_argument("--reserve", type=int, default=700)
    ap.add_argument("--tk", default="q4_0")
    ap.add_argument("--tv", default="q4_0")
    ap.add_argument("--o-dense", type=float, default=750)
    ap.add_argument("--o-moe", type=float, default=200)
    ap.add_argument(
        "--before", type=int, default=700, help="VRAM рабочего стола до загрузки, МиБ"
    )
    a = ap.parse_args()
    if a.fit or not a.model:
        fit()
    if a.model:
        predict(a.model, a.gpu, a.reserve, a.tk, a.tv, a.o_dense, a.o_moe, a.before)


if __name__ == "__main__":
    main()
