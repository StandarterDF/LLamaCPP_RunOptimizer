#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Графики по KV-кэшу: вычисленные (из метаданных GGUF) и измеренные (results.jsonl).

Вычисленные — детерминированные: размер KV-кэша, бюджет 16 ГБ, максимальный
контекст. Измеренные — из прогона bench/kv_quality.py: NIAH-recall, TG, VRAM, PPL.

Запуск:
  .venv\\Scripts\\python.exe bench\\plot_kv.py --suite bench\\suites\\kv\\kv_gemma.json \\
      --results bench\\runs\\kv\\<run>\\results.jsonl --out docs\\images

Без --results строятся только вычисленные графики и схема.
"""

import argparse
import json
import os
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import gguf_info  # noqa: E402

ENV_LOCAL = os.path.join(ROOT, "env.local.json")
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.axisbelow": True,
        "figure.dpi": 150,
        "savefig.bbox": "tight",
    }
)

KV_ORDER = ["f16", "q8_0", "q5_1", "q4_1", "q4_0", "iq4_nl", "q8k_q4v"]
KV_LABEL = {
    "f16": "f16",
    "q8_0": "q8_0",
    "q5_1": "q5_1",
    "q4_1": "q4_1",
    "q4_0": "q4_0",
    "iq4_nl": "iq4_nl",
    "q8k_q4v": "q8_0 K / q4_0 V",
}
KV_COLOR = {
    "f16": "#33415c",
    "q8_0": "#2a76b5",
    "q5_1": "#2a9d8f",
    "q4_1": "#e9a100",
    "q4_0": "#d1495b",
    "iq4_nl": "#8d6e63",
    "q8k_q4v": "#7b4fb5",
}
MODEL_TITLE = {
    "styletune-26b": "StyleTune-26B-A4B (MoE)",
    "schattenblume-31b": "Schattenblume-31B (dense)",
}
MODEL_FILE_GB = {"styletune-26b": 13.46, "schattenblume-31b": 11.25}


def expand(text):
    try:
        local = json.load(open(ENV_LOCAL, encoding="utf-8"))
    except Exception:
        local = {}
    return re.sub(
        r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}",
        lambda m: str(local.get(m.group(1), m.group(0))),
        text,
    )


def model_title(name):
    return MODEL_TITLE.get(name, name)


def kv_label(kv):
    return KV_LABEL.get(kv, kv)


def kv_color(kv):
    return KV_COLOR.get(kv, "#777777")


# ---------------------------------------------------------------------------
# Вычисленные графики
# ---------------------------------------------------------------------------
def load_models(suite_path):
    suite = json.load(open(suite_path, encoding="utf-8"))
    out = []
    for m in suite["models"]:
        info = gguf_info.analyze(expand(m["model"]))
        out.append(
            {
                "name": m["name"],
                "info": info,
                "file_mib": os.path.getsize(expand(m["model"])) / 2**20,
                "contexts": m.get("contexts", [16384, 49152]),
            }
        )
    return out, suite


def plot_memory_vs_context(models, out_dir):
    ctxs = [8192, 16384, 32768, 49152, 65536, 98304, 131072]
    dtypes = ["f16", "q8_0", "q5_1", "q4_1", "q4_0"]
    fig, axes = plt.subplots(1, len(models), figsize=(6.2 * len(models), 4.4))
    if len(models) == 1:
        axes = [axes]
    for ax, m in zip(axes, models):
        xs = list(range(len(ctxs)))
        for d in dtypes:
            ys = [gguf_info.kv_bytes(m["info"], c, d) / 2**20 for c in ctxs]
            ax.plot(xs, ys, marker="o", ms=4, color=kv_color(d), label=kv_label(d))
        fs = m["file_mib"]
        ax.axhline(
            fs, ls="--", lw=1, color="#888", label=f"веса модели ({fs / 1024:.1f} ГБ)"
        )
        ax.set_title(model_title(m["name"]))
        ax.set_xlabel("длина контекста, токенов")
        ax.set_ylabel("память KV-кэша, МиБ")
        ax.set_xticks(xs)
        ax.set_xticklabels([f"{c // 1024}k" for c in ctxs])
        ax.legend(fontsize=8, loc="upper left")
    fig.suptitle("Размер KV-кэша: как квантование экономит память", fontweight="bold")
    fig.savefig(os.path.join(out_dir, "kv_memory_vs_context.png"))
    plt.close(fig)


def feasible_ctx(info, budget_mib, file_mib, overhead, dtype):
    """Максимальный контекст (степень 2), при котором всё влезает в бюджет."""
    lo, hi = 1024, 262144
    best = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        total = file_mib + overhead + gguf_info.kv_bytes(info, mid, dtype) / 2**20
        if total <= budget_mib:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return round(best / 1024) * 1024


def plot_max_context(models, out_dir, budget_mib, overhead_by_model):
    dtypes = ["f16", "q8_0", "q4_1", "q4_0"]
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    n = len(models)
    w = 0.8 / n
    for i, m in enumerate(models):
        vals = [
            feasible_ctx(
                m["info"],
                budget_mib,
                m["file_mib"],
                overhead_by_model.get(m["name"], 900),
                d,
            )
            / 1024
            for d in dtypes
        ]
        xs = [j + i * w - 0.4 + w / 2 for j in range(len(dtypes))]
        bars = ax.bar(
            xs,
            vals,
            w,
            label=model_title(m["name"]),
            color=["#33415c", "#2a76b5"][i % 2],
        )
        for b, v in zip(bars, vals):
            ax.text(
                b.get_x() + b.get_width() / 2,
                v + 1.5,
                f"{v:.0f}k",
                ha="center",
                fontsize=9,
            )
    ax.set_xticks(range(len(dtypes)))
    ax.set_xticklabels([kv_label(d) for d in dtypes])
    ax.set_xlabel("тип KV-кэша")
    ax.set_ylabel("максимальный контекст, k токенов")
    ax.set_title(
        f"Сколько контекста даёт квант KV при {budget_mib / 1024:.1f} ГБ "
        "на GPU (больше — лучше)",
        fontweight="bold",
    )
    ax.legend()
    fig.savefig(os.path.join(out_dir, "kv_max_context.png"))
    plt.close(fig)


def plot_budget(models, out_dir, budget_mib, overhead_by_model):
    dtypes = ["f16", "q8_0", "q4_0"]
    fig, axes = plt.subplots(1, len(models), figsize=(6.0 * len(models), 4.8))
    if len(models) == 1:
        axes = [axes]
    for ax, m in zip(axes, models):
        ctx = 32768 if "31" in m["name"] else 49152
        weights = m["file_mib"] / 1024
        oh = overhead_by_model.get(m["name"], 900) / 1024
        xs, bottoms = [], 0
        labels, kvh = [], []
        for i, d in enumerate(dtypes):
            kvm = gguf_info.kv_bytes(m["info"], ctx, d) / 2**20 / 1024
            xs.append(i)
            bottom = weights + oh
            ax.bar(i, weights, 0.6, color="#5c6b73", label="веса" if i == 0 else None)
            ax.bar(
                i,
                oh,
                0.6,
                bottom=weights,
                color="#c9ada7",
                label="прочее (compute)" if i == 0 else None,
            )
            ax.bar(i, kvm, 0.6, bottom=bottom, color=kv_color(d), label=kv_label(d))
            inside = weights + oh + kvm
            ax.text(i, inside + 0.1, f"{inside:.1f}", ha="center", fontsize=9)
            if inside > budget_mib / 1024:
                ax.text(
                    i,
                    inside + 0.45,
                    "не влезает",
                    ha="center",
                    fontsize=8.5,
                    color="#b00020",
                )
        ax.axhline(budget_mib / 1024, ls="--", color="#b00020", lw=1.2)
        ax.text(
            len(dtypes) - 0.5,
            budget_mib / 1024 + 0.06,
            "лимит 16 ГБ",
            ha="right",
            color="#b00020",
            fontsize=9,
        )
        ax.set_xticks(range(len(dtypes)))
        ax.set_xticklabels([kv_label(d) for d in dtypes])
        ax.set_title(f"{model_title(m['name'])} @ {ctx // 1024}k")
        ax.set_ylabel("VRAM, ГБ")
        ax.set_ylim(0, max(budget_mib / 1024 + 1.2, 17))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=4,
        fontsize=9,
        frameon=False,
        bbox_to_anchor=(0.5, -0.02),
    )
    fig.suptitle(
        "Раскладка VRAM: квант KV освобождает память под контекст", fontweight="bold"
    )
    fig.subplots_adjust(bottom=0.18)
    fig.savefig(os.path.join(out_dir, "kv_vram_budget.png"))
    plt.close(fig)


def plot_concept(out_dir):
    fig, ax = plt.subplots(figsize=(9.6, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    def box(x, y, w, h, text, fc, ec):
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h, boxstyle="round,pad=0.12", fc=fc, ec=ec, lw=1.6
            )
        )
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            fontsize=10.5,
            wrap=True,
        )

    box(
        0.3,
        3.0,
        3.6,
        1.6,
        "ПРЯМОЙ ЭФФЕКТ\nКвантование K/V добавляет шум\n→ точность внимания ↓\n"
        "почти не видно на q8,\nрастёт с длиной контекста на q4",
        "#fdecea",
        "#d1495b",
    )
    box(
        6.1,
        3.0,
        3.6,
        1.6,
        "КОСВЕННЫЙ ЭФФЕКТ\nKV-кэш сжимается в 2–4×\n→ VRAM свободнее\n"
        "→ больше контекста и/или\nмодель целиком на GPU",
        "#e8f5e9",
        "#2e7d32",
    )
    box(
        3.2,
        0.35,
        3.6,
        1.5,
        "ИТОГ: «умнее» или нет?\nСравнивать надо не при одном\nконтексте, а при одном БЮДЖЕТЕ\n"
        "VRAM (16 ГБ). Побеждает тот KV,\nу которого выше качество\nна максимальном контексте.",
        "#e3f2fd",
        "#2a76b5",
    )
    ax.add_patch(
        FancyArrowPatch(
            (3.9, 3.8), (3.65, 1.9), arrowstyle="-|>", mutation_scale=18, color="#444"
        )
    )
    ax.add_patch(
        FancyArrowPatch(
            (6.1, 3.8), (6.35, 1.9), arrowstyle="-|>", mutation_scale=18, color="#444"
        )
    )
    ax.set_title("Два эффекта квантования KV-кэша", fontweight="bold", fontsize=13)
    fig.savefig(os.path.join(out_dir, "kv_concept.png"))
    plt.close(fig)


# ---------------------------------------------------------------------------
# Измеренные графики
# ---------------------------------------------------------------------------
def load_results(path):
    recs = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.strip()
        if ln:
            recs.append(json.loads(ln))
    return recs


def by_model(recs):
    d = {}
    for r in recs:
        if r.get("error"):
            continue
        d.setdefault(r["model"], []).append(r)
    return d


def multi_by_depth(r):
    p = r["probes"].get("multi") or {}
    dep = p.get("depths") or []
    fnd = p.get("found") or {}
    return dict(zip(dep, fnd.values()))


def single_recall(r):
    vals = [
        p["score"]
        for t, p in r["probes"].items()
        if t.startswith("d") and isinstance(p, dict) and "score" in p
    ]
    return sum(vals) / len(vals) if vals else None


def plot_niah_heatmap(recs, out_dir):
    groups = by_model(recs)
    for model, rs in groups.items():
        ctxs = sorted({r["ctx_req"] for r in rs})
        kvs = [k for k in KV_ORDER if any(r["kv"] == k for r in rs)]
        fig, axes = plt.subplots(
            1,
            len(ctxs),
            figsize=(4.6 * len(ctxs) + 1.5, 0.7 * len(kvs) + 3.2),
            squeeze=False,
        )
        for j, ctx in enumerate(ctxs):
            ax = axes[0][j]
            grid = []
            for kv in kvs:
                for r in rs:
                    if r["kv"] == kv and r["ctx_req"] == ctx:
                        md = multi_by_depth(r)
                        if md:
                            grid.append([md.get(d) for d in sorted(md)])
                        else:
                            grid.append([None] * 5)
            depths = [5, 25, 50, 75, 95]
            im = ax.imshow(
                [[1 if v is None else v for v in row] for row in grid],
                cmap="RdYlGn",
                vmin=0,
                vmax=1,
                aspect="auto",
            )
            ax.set_xticks(range(len(depths)))
            ax.set_xticklabels([f"{d}%" for d in depths])
            ax.set_yticks(range(len(kvs)))
            ax.set_yticklabels([kv_label(k) for k in kvs] if j == 0 else [])
            ax.set_xlabel("глубина иглы в контексте")
            ax.set_title(f"контекст {ctx // 1024}k")
            for yi, row in enumerate(grid):
                for xi, v in enumerate(row):
                    if v is not None:
                        ax.text(
                            xi,
                            yi,
                            f"{v:.0f}",
                            ha="center",
                            va="center",
                            fontsize=9.5,
                            color="#111",
                        )
            ax.grid(False)
        fig.suptitle(
            f"NIAH: доля найденных кодов (5 игл) — {model_title(model)}",
            fontweight="bold",
        )
        fig.colorbar(im, ax=axes[0][-1], fraction=0.046, pad=0.04, label="recall")
        fig.savefig(os.path.join(out_dir, f"kv_niah_{model}.png"))
        plt.close(fig)


def plot_recall_vs_context(recs, out_dir):
    groups = by_model(recs)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    for ax, (metric, title) in zip(
        axes,
        [
            ("single", "одна игла (среднее 3 глубин)"),
            ("multi", "5 игл (сеть по глубине)"),
        ],
    ):
        for model, rs in groups.items():
            for kv in KV_ORDER:
                pts = []
                for r in rs:
                    if r["kv"] != kv:
                        continue
                    if metric == "single":
                        v = single_recall(r)
                    else:
                        md = multi_by_depth(r)
                        v = sum(md.values()) / len(md) if md else None
                    if v is not None:
                        pts.append((r["ctx_req"], v))
                if not pts:
                    continue
                pts.sort()
                ax.plot(
                    [p[0] / 1024 for p in pts],
                    [p[1] for p in pts],
                    marker="o",
                    ls="-" if "31" in model else "--",
                    color=kv_color(kv),
                    label=f"{kv_label(kv)} · {model.split('-')[0]}",
                )
        ax.set_xlabel("длина контекста, k токенов")
        ax.set_ylabel("recall")
        ax.set_ylim(-0.05, 1.05)
        ax.set_title(title)
        ax.legend(fontsize=7.5, ncol=2)
    fig.suptitle(
        "Точность извлечения из длинного контекста vs тип KV-кэша", fontweight="bold"
    )
    fig.savefig(os.path.join(out_dir, "kv_recall_vs_context.png"))
    plt.close(fig)


def plot_tg_vs_context(recs, out_dir):
    groups = by_model(recs)
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    for model, rs in groups.items():
        for kv in KV_ORDER:
            pts = []
            for r in rs:
                if r["kv"] != kv:
                    continue
                p = r["probes"].get("d50") or r["probes"].get("d90") or {}
                if isinstance(p, dict) and p.get("tg_t_s"):
                    pts.append((r["ctx_req"], p["tg_t_s"]))
            if pts:
                pts.sort()
                ax.plot(
                    [p[0] / 1024 for p in pts],
                    [p[1] for p in pts],
                    marker="o",
                    ls="-" if "31" in model else "--",
                    color=kv_color(kv),
                    label=f"{kv_label(kv)} · {model.split('-')[0]}",
                )
    ax.set_xlabel("длина контекста, k токенов")
    ax.set_ylabel("скорость генерации, t/s")
    ax.set_title(
        "Скорость генерации vs контекст и тип KV (без спекуляции)", fontweight="bold"
    )
    ax.legend(fontsize=8, ncol=2, loc="lower left")
    fig.savefig(os.path.join(out_dir, "kv_tg_vs_context.png"))
    plt.close(fig)


def plot_vram_measured(recs, out_dir):
    groups = by_model(recs)
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    for model, rs in groups.items():
        for kv in KV_ORDER:
            pts = [
                (r["ctx_req"], r["vram_after_load_mb"])
                for r in rs
                if r["kv"] == kv and r.get("vram_after_load_mb")
            ]
            if pts:
                pts.sort()
                ax.plot(
                    [p[0] / 1024 for p in pts],
                    [p[1] / 1024 for p in pts],
                    marker="o",
                    ls="-" if "31" in model else "--",
                    color=kv_color(kv),
                    label=f"{kv_label(kv)} · {model.split('-')[0]}",
                )
    ax.axhline(16.0, ls="--", color="#b00020", lw=1.2)
    ax.text(0.5, 16.05, "16 ГБ", color="#b00020", fontsize=9)
    ax.set_xlabel("длина контекста, k токенов")
    ax.set_ylabel("занято VRAM, ГБ")
    ax.set_title("Фактическая VRAM при загрузке (измерено)", fontweight="bold")
    ax.legend(fontsize=8, ncol=2)
    fig.savefig(os.path.join(out_dir, "kv_vram_measured.png"))
    plt.close(fig)


def plot_ppl(recs, out_dir):
    def ppl_of(r):
        return (r.get("ppl_c512") or r.get("ppl_c2048") or {}).get("ppl")

    rows = [r for r in recs if ppl_of(r)]
    if not rows:
        return
    model = rows[0]["model"]
    kvs = [k for k in KV_ORDER if any(r["kv"] == k for r in rows)]
    vals = [next(ppl_of(r) for r in rows if r["kv"] == k) for k in kvs]
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    bars = ax.bar(range(len(kvs)), vals, color=[kv_color(k) for k in kvs])
    base = vals[0]
    for b, v in zip(bars, vals):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v * 1.01,
            f"{v:.2f}\n(×{v / base:.3f})",
            ha="center",
            fontsize=8.5,
        )
    ax.set_xticks(range(len(kvs)))
    ax.set_xticklabels([kv_label(k) for k in kvs])
    ax.set_ylabel("perplexity (русский корпус, c=512)")
    ax.set_title(
        f"PPL vs тип KV — {model_title(model)}\n(больше = хуже)", fontweight="bold"
    )
    fig.savefig(os.path.join(out_dir, "kv_ppl.png"))
    plt.close(fig)


# ---------------------------------------------------------------------------
def plot_prompt_flags(path, out_dir):
    data = json.load(open(path, encoding="utf-8"))
    groups = {}
    for rec in data:
        if rec.get("error"):
            continue
        groups.setdefault(rec["model"], []).append(rec)
    for model, recs in groups.items():
        pids = list(recs[0]["answers"].keys())
        kvs = [r["kv"] for r in recs]
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
        specs = [
            ("latin_words", "Латинские слова (утечка EN)", "штук"),
            ("max_repeat_ngram", "Макс. повтор n-грамма", "раз"),
            ("cyr_frac", "Доля кириллицы", "доля"),
        ]
        for ax, (metric, title, ylab) in zip(axes, specs):
            w = 0.8 / max(1, len(kvs))
            for i, kv in enumerate(kvs):
                rec = next(x for x in recs if x["kv"] == kv)
                vals = [
                    (rec["answers"].get(p, {}).get("flags", {}) or {}).get(metric) or 0
                    for p in pids
                ]
                xs = [j + i * w - 0.4 + w / 2 for j in range(len(pids))]
                ax.bar(xs, vals, w, color=kv_color(kv), label=kv_label(kv))
            ax.set_xticks(range(len(pids)))
            ax.set_xticklabels(pids, rotation=20, ha="right", fontsize=8)
            ax.set_title(title)
            ax.set_ylabel(ylab)
        axes[0].legend(fontsize=8)
        fig.suptitle(
            f"Признаки порчи текста по промптам — {model_title(model)}",
            fontweight="bold",
        )
        fig.savefig(os.path.join(out_dir, f"kv_prompt_flags_{model}.png"))
        plt.close(fig)


def plot_canary(path, out_dir):
    data = json.load(open(path, encoding="utf-8"))
    groups = {}
    for rec in data:
        if rec.get("summary"):
            groups.setdefault(rec["model"], []).append(rec)
    for model, recs in groups.items():
        kvs = [r["kv"] for r in recs]
        metrics = [
            ("json_valid_rate", "валидный\nJSON"),
            ("name_rate", "верная\nфункция"),
            ("functional_rate", "верные\nаргументы"),
            ("code_pass_rate", "код\npass@1"),
        ]
        fig, ax = plt.subplots(figsize=(8.6, 4.6))
        w = 0.8 / max(1, len(kvs))
        for i, kv in enumerate(kvs):
            s = next(r for r in recs if r["kv"] == kv)["summary"]
            vals = [s[m] for m, _ in metrics]
            xs = [j + i * w - 0.4 + w / 2 for j in range(len(metrics))]
            ax.bar(xs, vals, w, color=kv_color(kv), label=kv_label(kv))
            for x, v in zip(xs, vals):
                ax.text(x, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)
        ax.set_xticks(range(len(metrics)))
        ax.set_xticklabels([l for _, l in metrics])
        ax.set_ylim(0, 1.1)
        ax.set_ylabel("доля успеха")
        ax.set_title(
            f"Функциональная канарейка KV — {model_title(model)}", fontweight="bold"
        )
        ax.legend(fontsize=8, loc="lower left")
        fig.savefig(os.path.join(out_dir, f"kv_canary_{model}.png"))
        plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--suite", default=os.path.join("bench", "suites", "kv", "kv_gemma.json")
    )
    ap.add_argument("--results", default=None)
    ap.add_argument("--out", default=os.path.join("docs", "images"))
    ap.add_argument(
        "--budget-mib",
        type=float,
        default=15680.0,
        help="VRAM под сервер (16 ГБ минус система)",
    )
    ap.add_argument("--overhead", type=float, default=None)
    args = ap.parse_args()
    out_dir = (
        args.out if os.path.isabs(args.out) else os.path.join(ROOT, "..", args.out)
    )
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    models, suite = load_models(args.suite)
    overhead = {m["name"]: (args.overhead or 950.0) for m in models}

    # уточняем «прочее» по фактическим замерам, если есть
    if args.results and os.path.exists(args.results):
        recs = load_results(args.results)
        for m in models:
            for r in recs:
                if r.get("model") == m["name"] and r.get("vram_after_load_mb"):
                    kv_mib = (
                        gguf_info.kv_bytes(m["info"], r["ctx_req"], r["kv"]) / 2**20
                    )
                    oh = r["vram_after_load_mb"] - m["file_mib"] - kv_mib
                    if 0 < oh < 4000:
                        overhead[m["name"]] = oh
                        break
        print("overhead:", {k: round(v) for k, v in overhead.items()})
    else:
        recs = None

    plot_memory_vs_context(models, out_dir)
    plot_max_context(models, out_dir, args.budget_mib, overhead)
    plot_budget(models, out_dir, args.budget_mib, overhead)
    plot_concept(out_dir)
    print("вычисленные графики готовы:", out_dir)

    if recs is not None:
        plot_niah_heatmap(recs, out_dir)
        plot_recall_vs_context(recs, out_dir)
        plot_tg_vs_context(recs, out_dir)
        plot_vram_measured(recs, out_dir)
        plot_ppl(recs, out_dir)
        print("измеренные графики готовы")

    prompts_default = os.path.join(ROOT, "runs", "kv_prompts", "run", "results.json")
    if os.path.exists(prompts_default):
        plot_prompt_flags(prompts_default, out_dir)
        print("промптовые графики готовы")
    elif os.path.exists(os.path.join(ROOT, "runs", "kv_prompts")):
        cands = [
            os.path.join(ROOT, "runs", "kv_prompts", d, "results.json")
            for d in os.listdir(os.path.join(ROOT, "runs", "kv_prompts"))
        ]
        cands = [c for c in cands if os.path.exists(c)]
        if cands:
            plot_prompt_flags(sorted(cands)[-1], out_dir)
            print("промптовые графики готовы")

    canary_default = os.path.join(ROOT, "runs", "kv_canary", "run", "results.json")
    if os.path.exists(canary_default):
        plot_canary(canary_default, out_dir)
        print("графики канарейки готовы")


if __name__ == "__main__":
    main()
