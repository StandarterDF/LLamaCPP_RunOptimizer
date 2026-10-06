#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Собирает пакет для ПОПАРНОГО сравнения двух моделей (A vs B) на RP-наборе.
Карточка+история показываются один раз на сцену, затем ответы A и B по каждому сиду.
Имена моделей судье НЕ раскрываются (A/B анонимны).

Запуск (интерпретатором venv):
  .venv\\Scripts\\python.exe bench\\quality\\judge_pack.py --a <dirA> --b <dirB> --mode nothink --out bench\\quality\\runs\\_panel\\pack_nothink.txt
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rp_judge as rj  # noqa: E402

TASK = """Ты — строгий эксперт по русскоязычной ролевой игре (RP).
Ниже даны сцены: карточка персонажа и уже сыгранная история, затем ДВА ответа разных моделей —
[A] и [B] — на один и тот же финальный ход игрока, при одном и том же сиде.
Сравни A и B и по каждой оси реши, кто лучше: A, B или T (ничья).
Оси: ум, память, персонаж, инструкция, инициатива, русский, проза, повторы.
Критерии (как у строгого рецензента):
- ум: логика, адекватность, нет бессмыслицы;
- память: держит факты истории (имена, числа, детали);
- персонаж: голос и характер, не «ассистент»;
- инструкция: правила карточки (формат, длина, запреты);
- инициатива: двигает сцену, а не «говорящие головы»;
- русский: чистота (без англ. вставок и склеек букв);
- проза: без штампов и шаблонов;
- повторы: нет самоповторов и одинаковых конструкций.
ФОРМАТ ОТВЕТА — строго по одной строке на каждую пару, БЕЗ лишнего текста:
<режим>|<сцена>|<сид>|overall=<A|B|T>|ум=<A|B|T>|память=<A|B|T>|персонаж=<A|B|T>|инструкция=<A|B|T>|инициатива=<A|B|T>|русский=<A|B|T>|проза=<A|B|T>|повторы=<A|B|T>
Значения <режим>, <сцена>, <сид> бери ровно как в заголовках ниже. Сначала ВСЕ строки, затем 3 строки краткого вывода.
"""


def render_msgs(msgs):
    return "\n".join(
        f"[{rj.ROLE_LABEL.get(m['role'], m['role'])}] {m['content']}" for m in msgs
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="каталог прогонов модели A")
    ap.add_argument("--b", required=True, help="каталог прогонов модели B")
    ap.add_argument(
        "--prompts",
        default=os.path.join(rj.ROOT, "quality", "scenarios_rp_full.json"),
    )
    ap.add_argument("--mode", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    scen = {s.get("tag"): s for s in json.load(open(args.prompts, encoding="utf-8"))}
    A = {(r.get("tag"), r.get("seed")): r for r in rj.read_metrics(args.a)}
    B = {(r.get("tag"), r.get("seed")): r for r in rj.read_metrics(args.b)}

    out = [TASK, "=" * 60, f"### РЕЖИМ: {args.mode}", ""]
    npairs = 0
    for tag, s in scen.items():
        out.append(f"#### Сценарий: {tag} — {s.get('_что_проверяем', '')}")
        out.append("КАРТОЧКА И ИСТОРИЯ:")
        out.append(render_msgs(s["messages"]))
        seeds = sorted({k[1] for k in list(A) + list(B) if k[0] == tag})
        for sd in seeds:
            ra, rb = A.get((tag, sd)), B.get((tag, sd))
            if not ra or not rb:
                continue
            out.append(f"--- сид {sd} ---")
            out.append("[A] " + (ra.get("text") or "").strip())
            out.append("[B] " + (rb.get("text") or "").strip())
            npairs += 1
        out.append("")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"wrote {args.out}: {npairs} пар, {len(''.join(out))} символов")


if __name__ == "__main__":
    main()
