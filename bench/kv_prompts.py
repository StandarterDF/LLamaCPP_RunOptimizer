#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Промптовое сравнение KV-кэшей: одни и те же промпты через f16/q8_0/q4_0.

Не про «баллы», а про глаза: кладём ответы рядом и смотрим, где квант KV
ломает память, вносит глитчи или не меняет ничего.

Промпты подобраны под три разных риска:
  * memory_long   — факты в начале длинного (~12k) контекста, вопрос в конце:
                    проверить, помнит ли модель детали под q4.
  * rule_far      — правило-инструкция в начале длинного документа, задание в
                    конце: проверка удержания служебных токенов на глубине.
  * creative_ru   — короткий креатив на высокой T: ошибки/повторы/англ. вставки.
  * reason_ru     — короткая задача на вывод (combine фактов), T=0.

Запуск:
  .venv\\Scripts\\python.exe bench\\kv_prompts.py bench\\suites\\kv\\kv_prompts.json
  .venv\\Scripts\\python.exe bench\\kv_prompts.py <suite.json> --only-kv f16,q4_0

Результат: bench/runs/kv_prompts/<run>/ — compare_<model>.md (читаемый отчёт),
answers/*.txt (сырые ответы), results.json.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv_quality as K  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# грубая эвристика «подозрительных» мест в ответе
# ---------------------------------------------------------------------------
def flag_text(text):
    """Возвращает словарь с признаками порчи текста (оценка на глаз, не точная)."""
    words = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
    rep = 1
    if len(words) >= 8:
        for n in range(8, 2, -1):
            grams = [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]
            if grams:
                rep = max(rep, max(grams.count(g) for g in set(grams)))
    latin_runs = re.findall(r"\b[A-Za-z]{2,}\b", text)
    return {
        "chars": len(text),
        "cyr_frac": K.cyr_frac(text),
        "max_repeat_ngram": rep,
        "latin_words": len(latin_runs),
        "latin_sample": latin_runs[:6],
    }


# ---------------------------------------------------------------------------
def build_messages(prompt, port, corpus):
    """Собирает messages: system + user, с длинным сеном перед заданием."""
    sysmsg = prompt.get("system", "")
    filler_tokens = prompt.get("context_tokens", 0)
    head = prompt.get("needle", "")
    body = prompt.get("user", "")
    if filler_tokens > 0:
        seq, tok = K.assemble_haystack(
            port, filler_tokens, corpus, salt=prompt.get("salt", 7)
        )
        parts = seq[: len(seq) // 2] + [head] + seq[len(seq) // 2 :]
        user = "\n".join(parts) + "\n\n" + body
    else:
        user = (head + "\n\n" + body) if head else body
    msgs = []
    if sysmsg:
        msgs.append({"role": "system", "content": sysmsg})
    msgs.append({"role": "user", "content": user})
    return msgs


def gen_messages(port, messages, n_predict, temperature=0.7, min_p=0.1, seed=1):
    body = {
        "messages": messages,
        "max_tokens": n_predict,
        "temperature": temperature,
        "min_p": min_p,
        "top_p": 0.95,
        "top_k": 0,
        "seed": seed,
        "stream": False,
        "cache_prompt": False,
    }
    t0 = time.time()
    resp = K.http_json(
        f"http://127.0.0.1:{port}/v1/chat/completions", body, timeout=2400
    )
    tim = resp.get("timings") or {}
    msg = (resp.get("choices") or [{}])[0].get("message") or {}
    return {
        "content": msg.get("content") or "",
        "reasoning": msg.get("reasoning_content") or "",
        "wall_s": round(time.time() - t0, 1),
        "prompt_n": tim.get("prompt_n"),
        "tg_t_s": tim.get("predicted_per_second"),
    }


def run_model_kv(server_exe, model, kv, prompts, corpus, out_dir, port):
    cfg_dir = os.path.join(out_dir, f"{model['name']}__{kv}")
    os.makedirs(os.path.join(cfg_dir, "answers"), exist_ok=True)
    log_path = os.path.join(cfg_dir, "server.log")
    if model.get("ctx"):
        ctx = int(model["ctx"])
    else:
        max_ctx = max([p.get("context_tokens", 0) for p in prompts] + [4096])
        ctx = 1 << max(12, int(max_ctx * 1.35).bit_length())
    cli = (
        ["--model", model["model"], "-np", "1", "-c", str(ctx)]
        + model.get("base_args", [])
        + K.KV_ARGS[kv]
    )
    proc, logf = K.start_server(server_exe, {"port": port, "cli": cli}, log_path)
    rec = {"model": model["name"], "kv": kv, "ctx": ctx, "vram_mb": None, "answers": {}}
    try:
        if not K.wait_health(port, proc, timeout=900):
            rec["error"] = "server did not become healthy"
            return rec
        time.sleep(2.0)
        rec["vram_mb"] = K.gpu_mem_mb()
        for p in prompts:
            msgs = build_messages(p, port, corpus)
            r = gen_messages(
                port,
                msgs,
                p.get("n_predict", 350),
                p.get("temperature", 0.7),
                p.get("min_p", 0.1),
                p.get("seed", 1),
            )
            r["flags"] = flag_text(r["content"])
            r["title"] = p["title"]
            r["user"] = p.get("user", "")
            r["system"] = p.get("system", "")
            r["needle"] = p.get("needle", "")
            r["context_tokens"] = p.get("context_tokens", 0)
            with open(
                os.path.join(cfg_dir, "answers", f"{p['id']}.txt"),
                "w",
                encoding="utf-8",
            ) as f:
                f.write(r["content"])
            rec["answers"][p["id"]] = r
            print(
                f"   {p['id']}: {len(r['content'])} симв, "
                f"prompt_n={r['prompt_n']}, TG={r['tg_t_s'] and round(r['tg_t_s'], 1)}, "
                f"cyr={r['flags']['cyr_frac']}, rep={r['flags']['max_repeat_ngram']}, "
                f"lat={r['flags']['latin_words']}"
            )
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"
    finally:
        K.kill_proc(proc)
        logf.close()
        time.sleep(1.5)
    return rec


def write_report(per_model, suite, out_dir):
    for model_name, recs in per_model.items():
        lines = [f"# Сравнение KV-кэша по промптам — {model_name}", ""]
        prompts = suite["prompts"]
        for p in prompts:
            lines += [f"## {p['title']}", ""]
            if p.get("context_tokens"):
                lines += [
                    f"*контекст: ~{p['context_tokens']} токенов сена "
                    f"(деталь вставлена в середину), затем задание.*",
                    "",
                ]
            if p.get("system"):
                lines += ["**System:** " + p["system"], ""]
            if p.get("needle"):
                lines += ["**Деталь в середине:** " + p["needle"], ""]
            lines += ["**Задание:** " + p.get("user", ""), ""]
            for kv in [r["kv"] for r in recs]:
                r = next(x for x in recs if x["kv"] == kv)
                a = r["answers"].get(p["id"], {})
                fl = a.get("flags", {})
                lines += [f"### {K.KV_LABEL.get(kv, kv)}", ""]
                lines += [
                    f"*prompt_n={a.get('prompt_n')}, TG={a.get('tg_t_s') and round(a.get('tg_t_s'), 1)} t/s, "
                    f"cyr={fl.get('cyr_frac')}, повторы(max n-gram)={fl.get('max_repeat_ngram')}, "
                    f"лат.слов={fl.get('latin_words')} {fl.get('latin_sample') or ''}*",
                    "",
                ]
                text = (a.get("content") or "").strip()
                lines += [text if text else "*(пусто)*", "", "---", ""]
        with open(
            os.path.join(out_dir, f"compare_{model_name}.md"), "w", encoding="utf-8"
        ) as f:
            f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description="Промптовое сравнение KV-кэшей")
    ap.add_argument("suite")
    ap.add_argument("--only-model", default=None)
    ap.add_argument("--only-kv", default=None)
    ap.add_argument("--only-prompt", default=None)
    ap.add_argument("--port", type=int, default=9981)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    suite = K.expand_obj(json.load(open(a.suite, encoding="utf-8")))
    server_exe = suite["server"]
    kvs = [x.strip() for x in a.only_kv.split(",")] if a.only_kv else suite["kvs"]
    prompts = suite["prompts"]
    if a.only_prompt:
        prompts = [p for p in prompts if p["id"].startswith(a.only_prompt)]
    corpus_path = suite.get("filler")
    if isinstance(corpus_path, str) and not os.path.isabs(corpus_path):
        corpus_path = os.path.join(K.ROOT, corpus_path)
    corpus = K.load_corpus(corpus_path)

    models = suite["models"]
    if a.only_model:
        models = [m for m in models if m["name"].startswith(a.only_model)]

    run_name = suite.get("name", "kv_prompts")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = a.out or os.path.join(K.ROOT, "runs", "kv_prompts", f"{run_name}-{stamp}")
    os.makedirs(out_dir, exist_ok=True)
    print(f"Промптовый стенд -> {os.path.relpath(out_dir, K.ROOT)}")

    per_model = {}
    results = []
    i = 0
    for model in models:
        per_model[model["name"]] = []
        for kv in kvs:
            i += 1
            print(f"\n[{model['name']}] KV={kv}")
            rec = run_model_kv(
                server_exe, model, kv, prompts, corpus, out_dir, a.port + (i % 3)
            )
            if rec.get("error"):
                print(f"   ОШИБКА: {rec['error']}")
            per_model[model["name"]].append(rec)
            results.append(rec)
            time.sleep(6)

    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    write_report(per_model, {"prompts": prompts}, out_dir)
    print(f"\nОтчёт: {out_dir}\\compare_*.md")


if __name__ == "__main__":
    main()
