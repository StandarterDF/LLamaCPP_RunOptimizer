#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Графики из данных репозитория (seaborn): рейтинг RP, спекуляция, кэш промпта.

Только графики по реальным замерам (никаких «схем со стрелками»):
  * chart_rp_ranking.png        — RP-балл моделей (Non-Think и Think), Local/Cloud;
  * chart_speculation_models.png — без спекуляции vs MTP, среднее по задачам;
  * chart_speculation_tasks.png  — без спекуляции vs MTP по задачам (Qwen3.6);
  * chart_cache_prompt.png       — кэш префикса: оценённые токены и время на ход.

Запуск:
  .venv\\Scripts\\python.exe bench\\make_charts.py --out docs\\images
"""

import argparse
import json
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sns.set_theme(
    style="whitegrid",
    context="notebook",
    rc={
        "font.family": "DejaVu Sans",
        "savefig.bbox": "tight",
        "figure.dpi": 150,
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
    },
)
C_LOCAL, C_CLOUD = "#2a76b5", "#e9a100"
C_NOSPEC, C_MTB = "#9aa5b1", "#2e7d32"


def chart_rp_ranking(out):
    text = open(
        os.path.join(ROOT, "docs", "quality", "rp-ranking.md"), encoding="utf-8"
    ).read()
    tables, cur = {}, None
    for line in text.splitlines():
        if line.startswith("## Non-Thinking"):
            cur, tables[cur] = "Non-Think", []
        elif line.startswith("## Thinking"):
            cur, tables[cur] = "Think", []
        elif cur and line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 4 and re.match(r"^\d+$", cells[0]):
                model = re.sub(r"\*\(.*?\)\*", "", cells[1]).replace("*", "").strip()
                try:
                    rp = float(cells[3].replace("*", ""))
                except ValueError:
                    continue
                tables[cur].append((model, cells[2], rp))
    fig, axes = plt.subplots(1, 2, figsize=(13, 7))
    for ax, mode in zip(axes, ["Non-Think", "Think"]):
        rows = sorted(tables.get(mode, []), key=lambda x: x[2])
        names = [r[0] for r in rows]
        vals = [r[2] for r in rows]
        cols = [C_CLOUD if r[1] == "Cloud" else C_LOCAL for r in rows]
        ax.barh(names, vals, color=cols)
        for i, v in enumerate(vals):
            ax.text(v + 0.02, i, f"{v:.2f}", va="center", fontsize=8.5)
        ax.set_xlim(3.0, 4.25)
        ax.set_xlabel("средний балл RP (4 судьи, 1–5)")
        ax.set_title(mode)
        ax.tick_params(axis="y", labelsize=8.5)
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=C_LOCAL),
        plt.Rectangle((0, 0), 1, 1, color=C_CLOUD),
    ]
    fig.legend(
        handles,
        ["Local", "Cloud"],
        loc="lower center",
        ncol=2,
        fontsize=9,
        frameon=False,
        bbox_to_anchor=(0.5, -0.01),
    )
    fig.suptitle("RP-рейтинг моделей (панель 4 судей)", fontweight="bold", fontsize=14)
    fig.subplots_adjust(bottom=0.10)
    fig.savefig(os.path.join(out, "chart_rp_ranking.png"))
    plt.close(fig)


def load_real_runs():
    recs = {}
    for ln in open(
        os.path.join(ROOT, "bench", "runs", "results.jsonl"), encoding="utf-8"
    ):
        ln = ln.strip()
        if ln:
            r = json.loads(ln)
            recs[r.get("name")] = r
    return recs


SPEC_MODELS = [
    ("Qwen3.6-35B-A3B (MoE)", "real_q36_nospec", "real_q36_mtp5"),
    ("Gemma-26B-A4B (MoE)", "real_g26_nospec", "real_g26_mtp5"),
    ("Gemma-31B (dense)", "real_g31_nospec", "real_g31_mtp5"),
    ("Swift-1.5-27B (dense)", "real_swift_nospec", "real_swift_mtp5"),
    ("Split-Untied-31B (dense)", "real_split_nospec", "real_split_mtp"),
    ("MeroMero-26B (MoE)", "real_meromero_nospec", "real_meromero_mtp"),
]
TASKS = ["rp", "chat", "code", "math", "summ"]


def mean_tg(rec, tags=TASKS):
    vals = [(rec.get("runs", {}).get(t, {}) or {}).get("tg_t_s") for t in tags]
    vals = [v for v in vals if v]
    return sum(vals) / len(vals) if vals else 0.0


def _pair_bars(ax, labels, no, mt, xlabels, rot=0):
    x = np.arange(len(labels))
    w = 0.38
    ymax = max(max(no or [1]), max(mt or [1]))
    b1 = ax.bar(x - w / 2, no, w, label="без спекуляции", color=C_NOSPEC)
    b2 = ax.bar(x + w / 2, mt, w, label="MTP-спекуляция", color=C_MTB)
    for bars in (b1, b2):
        for b in bars:
            ax.text(
                b.get_x() + b.get_width() / 2,
                b.get_height() + ymax * 0.012,
                f"{b.get_height():.0f}",
                ha="center",
                fontsize=9,
            )
    for i in range(len(labels)):
        if no[i]:
            ax.text(
                x[i],
                max(no[i], mt[i]) + ymax * 0.06,
                f"×{mt[i] / no[i]:.2f}",
                ha="center",
                fontsize=9,
                color=C_MTB,
                fontweight="bold",
            )
    ax.set_ylim(0, ymax * 1.22)
    ax.set_xticks(x)
    ax.set_xticklabels(
        xlabels, rotation=rot, ha="right" if rot else "center", fontsize=9
    )
    ax.set_ylabel("скорость генерации, t/s")


def chart_speculation_models(recs, out):
    labels, no, mt = [], [], []
    for label, nname, mname in SPEC_MODELS:
        if nname in recs and mname in recs:
            labels.append(label)
            no.append(mean_tg(recs[nname]))
            mt.append(mean_tg(recs[mname]))
    fig, ax = plt.subplots(figsize=(11, 5))
    _pair_bars(ax, labels, no, mt, labels, rot=12)
    ax.set_title("Спекуляция MTP: выигрыш по скорости на реалистичных задачах")
    ax.legend(loc="upper right")
    fig.savefig(os.path.join(out, "chart_speculation_models.png"))
    plt.close(fig)


def chart_speculation_tasks(recs, out):
    no = recs.get("real_q36_nospec", {})
    mt = recs.get("real_q36_mtp5", {})
    labels = [mean_tg(no, [t]) for t in TASKS]
    mtv = [mean_tg(mt, [t]) for t in TASKS]
    fig, ax = plt.subplots(figsize=(9, 5))
    _pair_bars(
        ax,
        TASKS,
        labels,
        mtv,
        ["RP/креатив", "чат", "код", "математика", "суммаризация"],
    )
    ax.set_title("Qwen3.6-35B-A3B: где спекуляция окупается сильнее")
    ax.legend(loc="upper left")
    fig.savefig(os.path.join(out, "chart_speculation_tasks.png"))
    plt.close(fig)


def chart_cache_prompt(out):
    base = os.path.join(ROOT, "bench", "runs", "usecase_cache")
    on = json.load(
        open(os.path.join(base, "usecase_cache_result_reuse256.json"), encoding="utf-8")
    )
    off = json.load(
        open(
            os.path.join(base, "usecase_cache_result_noreuse_nocacheprompt.json"),
            encoding="utf-8",
        )
    )
    turns = ["r2", "r3"]
    x = np.arange(len(turns))
    w = 0.38
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    for ax, key, ylab, title, fmt in [
        (
            axes[0],
            "prompt_n_eval",
            "пересчитано токенов промпта",
            "Сколько промпта пересчитывает сервер",
            "{:.0f}",
        ),
        (axes[1], "wall_s", "время ответа, с", "Время ответа на ход", "{:.1f} c"),
    ]:
        voff = [off[t][key] for t in turns]
        von = [on[t][key] for t in turns]
        ymax = max(max(voff), max(von))
        b1 = ax.bar(x - w / 2, voff, w, label="без cache_prompt", color="#d1495b")
        b2 = ax.bar(x + w / 2, von, w, label="cache_prompt: true", color=C_MTB)
        for bars in (b1, b2):
            for b in bars:
                ax.text(
                    b.get_x() + b.get_width() / 2,
                    b.get_height() + ymax * 0.02,
                    fmt.format(b.get_height()),
                    ha="center",
                    fontsize=9,
                )
        ax.set_ylim(0, ymax * 1.2)
        ax.set_xticks(x)
        ax.set_xticklabels(["ход 2", "ход 3"])
        ax.set_ylabel(ylab)
        ax.set_title(title)
    handles, labs = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labs,
        loc="lower center",
        ncol=2,
        fontsize=9,
        frameon=False,
        bbox_to_anchor=(0.5, -0.02),
    )
    fig.suptitle(
        "Кэш промпта в многотирне: ~7800 → ~25 токенов пересчёта",
        fontweight="bold",
        fontsize=13,
    )
    fig.subplots_adjust(bottom=0.16)
    fig.savefig(os.path.join(out, "chart_cache_prompt.png"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join("docs", "images"))
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    recs = load_real_runs()
    chart_rp_ranking(out)
    chart_speculation_models(recs, out)
    chart_speculation_tasks(recs, out)
    chart_cache_prompt(out)
    print("графики готовы:", out)


if __name__ == "__main__":
    main()
