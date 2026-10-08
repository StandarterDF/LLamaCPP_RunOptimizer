#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Функциональная канарейка KV-кэша: tool/JSON-вызовы и pass@1 кода.

Идея (по мотивам pjdurden/kv-canary): perplexity и recall могут «молчать», пока
ломается функциональный вывод. Здесь — объективные задачи:
  * tool/JSON: модель должна вернуть JSON-вызов нужного инструмента с нужными
    аргументами. Список инструментов лежит в НАЧАЛЕ длинного (~8k) system-промпта,
    правила-умолчания — в конце; так проверяется и удержание инструментов с глубины,
    и точность аргументов. Считаем: валидный JSON / верная функция / верные аргументы.
  * код: модель пишет маленькую функцию, мы исполняем её с тестом (pass@1).

Один конфиг = модель × тип KV; все кейсы идут через один сервер (system-префикс
кэшируется, cache_prompt=true).

Запуск:
  .venv\\Scripts\\python.exe bench\\kv_canary.py bench\\suites\\kv\\kv_canary.json
  .venv\\Scripts\\python.exe bench\\kv_canary.py <suite.json> --only-kv f16,q4_0

Результат: bench/runs/kv_canary/<run>/results.json + answers/ + отчёт.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv_quality as K  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SYS_INSTR = (
    "Ты — ассистент с инструментами. Когда пользователь просит действие, верни "
    "РОВНО ОДИН JSON-объект и ничего больше: "
    '{"name": "<функция>", "arguments": { ... }}. '
    "Не добавляй пояснений, markdown и текст вокруг JSON."
)


def norm(s):
    return re.sub(r"\s+", " ", str(s).lower().replace("ё", "е")).strip()


def extract_json(text):
    """Достаёт первый сбалансированный {...} из ответа и парсит его."""
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    chunk = text[start : i + 1]
                    try:
                        return json.loads(chunk)
                    except Exception:
                        break
        start = text.find("{", start + 1)
    return None


def parse_tool_call(content):
    obj = extract_json(content)
    if not isinstance(obj, dict):
        return None, None, False
    name = obj.get("name") or obj.get("tool") or obj.get("function")
    if isinstance(name, dict):
        name = name.get("name")
    args = (
        obj.get("arguments")
        if "arguments" in obj
        else obj.get("parameters")
        if "parameters" in obj
        else obj.get("args")
    )
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {}
    if not isinstance(args, dict):
        args = {}
    return name, args, True


def args_match(args, expect):
    for k, want in expect.items():
        if k not in args:
            return False
        got = norm(args[k])
        accepted = want if isinstance(want, list) else [want]
        ok = False
        for a in accepted:
            if isinstance(a, (int, float)):
                try:
                    if float(args[k]) == float(a):
                        ok = True
                except Exception:
                    pass
            elif norm(a) in got:
                ok = True
        if not ok:
            return False
    return True


def chat(port, system, user, n_predict=120, temperature=0.0, seed=1, cache_prompt=True):
    body = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": n_predict,
        "temperature": temperature,
        "top_p": 1.0,
        "top_k": 0,
        "seed": seed,
        "stream": False,
        "cache_prompt": cache_prompt,
    }
    t0 = time.time()
    resp = K.http_json(
        f"http://127.0.0.1:{port}/v1/chat/completions", body, timeout=1200
    )
    tim = resp.get("timings") or {}
    msg = (resp.get("choices") or [{}])[0].get("message") or {}
    return {
        "content": msg.get("content") or "",
        "wall_s": round(time.time() - t0, 1),
        "prompt_n": tim.get("prompt_n"),
        "tg_t_s": tim.get("predicted_per_second"),
    }


def extract_code(text):
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    code = m.group(1) if m else text
    i = code.find("def ")
    if i > 0:
        code = code[i:]
    return code.strip()


def run_code(code, test):
    src = code + "\n\n" + test + "\nprint('PASS')\n"
    with tempfile.NamedTemporaryFile(
        "w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(src)
        path = f.name
    try:
        p = subprocess.run(
            [sys.executable, path], capture_output=True, text=True, timeout=20
        )
        return p.returncode == 0 and "PASS" in (p.stdout or "")
    except Exception:
        return False
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass
    return False


def run_config(server_exe, model, kv, suite, corpus, out_dir, port):
    cfg_dir = os.path.join(out_dir, f"{model['name']}__{kv}")
    os.makedirs(os.path.join(cfg_dir, "answers"), exist_ok=True)
    log_path = os.path.join(cfg_dir, "server.log")
    ctx = int(model.get("ctx", 32768))
    cli = (
        ["--model", model["model"], "-np", "1", "-c", str(ctx)]
        + model.get("base_args", [])
        + K.KV_ARGS[kv]
    )
    proc, logf = K.start_server(server_exe, {"port": port, "cli": cli}, log_path)
    rec = {
        "model": model["name"],
        "kv": kv,
        "ctx": ctx,
        "error": None,
        "vram_mb": None,
        "tools": {},
        "code": {},
        "system_tokens": None,
    }
    try:
        if not K.wait_health(port, proc, timeout=900):
            rec["error"] = "server did not become healthy"
            return rec
        time.sleep(2.0)
        rec["vram_mb"] = K.gpu_mem_mb()
        filler, ftok = K.assemble_haystack(
            port, suite.get("filler_tokens", 8000), corpus, salt=3
        )
        system = (
            SYS_INSTR
            + "\n\n"
            + suite["tools_doc"]
            + "\n\n"
            + "\n".join(filler)
            + "\n\n"
            + suite["rules"]
        )
        rec["system_tokens"] = K.count_tokens(port, system)

        n_valid = n_name = n_args = 0
        for case in suite["cases"]:
            r = chat(port, system, case["user"], n_predict=140)
            name, args, valid = parse_tool_call(r["content"])
            name_ok = norm(name) == norm(case["name"])
            args_ok = valid and name_ok and args_match(args, case.get("args", {}))
            n_valid += bool(valid)
            n_name += bool(name_ok)
            n_args += bool(args_ok)
            r.update(
                {
                    "valid": bool(valid),
                    "name": name,
                    "args": args,
                    "name_ok": bool(name_ok),
                    "args_ok": bool(args_ok),
                    "expect_name": case["name"],
                    "expect_args": case.get("args", {}),
                }
            )
            rec["tools"][case["id"]] = r
            with open(
                os.path.join(cfg_dir, "answers", f"tool_{case['id']}.txt"),
                "w",
                encoding="utf-8",
            ) as f:
                f.write(r["content"])
            print(
                f"   tool {case['id']:12} valid={int(valid)} name={int(name_ok)} "
                f"args={int(args_ok)}  name={name} args={args}"
            )

        n_pass = 0
        for task in suite.get("code_tasks", []):
            r = chat(
                port,
                "Ты пишешь код. Отвечай только кодом функции.",
                task["prompt"],
                n_predict=220,
                cache_prompt=False,
            )
            code = extract_code(r["content"])
            ok = run_code(code, task["test"])
            n_pass += ok
            r.update({"pass": bool(ok), "code": code})
            rec["code"][task["id"]] = r
            with open(
                os.path.join(cfg_dir, "answers", f"code_{task['id']}.py"),
                "w",
                encoding="utf-8",
            ) as f:
                f.write(code)
            print(f"   code {task['id']:12} pass={int(ok)}")

        n = len(suite["cases"])
        m = len(suite.get("code_tasks", [])) or 1
        rec["summary"] = {
            "tools_total": n,
            "json_valid_rate": round(n_valid / n, 3),
            "name_rate": round(n_name / n, 3),
            "functional_rate": round(n_args / n, 3),
            "code_pass_rate": round(n_pass / m, 3),
        }
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"
    finally:
        K.kill_proc(proc)
        logf.close()
        time.sleep(1.5)
    return rec


def main():
    ap = argparse.ArgumentParser(description="Функциональная канарейка KV")
    ap.add_argument("suite")
    ap.add_argument("--only-model", default=None)
    ap.add_argument("--only-kv", default=None)
    ap.add_argument("--port", type=int, default=9991)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    suite = K.expand_obj(json.load(open(a.suite, encoding="utf-8")))
    server_exe = suite["server"]
    kvs = [
        x.strip() for x in (a.only_kv or ",".join(suite["kvs"])).split(",") if x.strip()
    ]
    models = suite["models"]
    if a.only_model:
        models = [m for m in models if m["name"].startswith(a.only_model)]
    corpus_path = suite.get("filler")
    if isinstance(corpus_path, str) and not os.path.isabs(corpus_path):
        corpus_path = os.path.join(K.ROOT, corpus_path)
    corpus = K.load_corpus(corpus_path)

    run_name = suite.get("name", "kv_canary")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = a.out or os.path.join(K.ROOT, "runs", "kv_canary", f"{run_name}-{stamp}")
    os.makedirs(out_dir, exist_ok=True)
    print(f"Канарейка -> {os.path.relpath(out_dir, K.ROOT)}")

    results = []
    i = 0
    for model in models:
        for kv in kvs:
            i += 1
            print(f"\n[{model['name']}] KV={kv}")
            rec = run_config(
                server_exe, model, kv, suite, corpus, out_dir, a.port + (i % 3)
            )
            results.append(rec)
            if rec.get("summary"):
                s = rec["summary"]
                print(
                    f"   ИТОГ: json={s['json_valid_rate']} name={s['name_rate']} "
                    f"functional={s['functional_rate']} code={s['code_pass_rate']}"
                )
            elif rec.get("error"):
                print(f"   ОШИБКА: {rec['error']}")
            time.sleep(5)

    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # сводка f16 -> q8/q4
    print("\n===== СВОДКА =====")
    for model in models:
        base = next(
            (
                r
                for r in results
                if r["model"] == model["name"] and r["kv"] == "f16" and r.get("summary")
            ),
            None,
        )
        for kv in kvs:
            r = next(
                (x for x in results if x["model"] == model["name"] and x["kv"] == kv),
                None,
            )
            if not r or not r.get("summary"):
                continue
            s = r["summary"]
            line = (
                f"{model['name']:20} {kv:8} "
                f"json={s['json_valid_rate']:.2f} name={s['name_rate']:.2f} "
                f"func={s['functional_rate']:.2f} code={s['code_pass_rate']:.2f}"
            )
            if base and kv != "f16":
                bs = base["summary"]
                line += (
                    f"   Δfunc={s['functional_rate'] - bs['functional_rate']:+.2f} "
                    f"Δcode={s['code_pass_rate'] - bs['code_pass_rate']:+.2f}"
                )
            print(line)
    print(f"\nРезультаты: {out_dir}\\results.json")


if __name__ == "__main__":
    main()
