#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Бенчмарк llama-server для исследования лучшего запуска Swift-1.5-Qwen3.8-27B (IQ2_S-mtp)
на существующем билде <папка llama.cpp> (build 10472).

Только стандартная библиотека. Запуск:
  .venv\\Scripts\\python.exe bench\\bench.py bench\\suites\\baseline.json

Пути в suite.json можно задавать плейсхолдерами ${LLAMA_SERVER}, ${LLAMA_DIR},
${MODELS_DIR}, ${PROJECT_DIR} — они раскрываются из bench/env.local.json (образец: env.example.json).

Каждый тест:
  1) поднимает свой llama-server на отдельном порту, лог пишется в bench/runs/<name>.log;
  2) ждёт /health, замеряет время загрузки и занятую VRAM;
  3) читает /props (наличие chat template, n_ctx);
  4) шлёт 2 запроса /completion (короткий промпт -> генерация; длинный промпт -> PP на глубине);
  5) гасит сервер, пишет результат в bench/runs/results.jsonl.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(ROOT, "runs")
os.makedirs(RUNS, exist_ok=True)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ENV_LOCAL = os.path.join(ROOT, "env.local.json")
SANITIZE_KEYS = ("LLAMA_SERVER", "LLAMA_DIR", "MODELS_DIR", "PROJECT_DIR")


def _load_env():
    """Пути для подстановки и санитизации: bench/env.local.json + переменные окружения."""
    env_map = dict(os.environ)
    local = {}
    try:
        with open(ENV_LOCAL, encoding="utf-8") as f:
            local = json.load(f)
    except Exception:
        local = {}
    env_map.update(local)
    pairs = [(local[k], f"<{k}>") for k in SANITIZE_KEYS if local.get(k)]
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    return env_map, pairs


ENV_MAP, SANITIZE_PAIRS = _load_env()


def expand_str(text: str) -> str:
    return re.sub(
        r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}",
        lambda m: str(ENV_MAP.get(m.group(1), m.group(0))),
        text,
    )


def expand_obj(obj):
    if isinstance(obj, str):
        return expand_str(obj)
    if isinstance(obj, list):
        return [expand_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: expand_obj(v) for k, v in obj.items()}
    return obj


def sanitize(text: str) -> str:
    """Заменяет личные пути на плейсхолдеры перед записью артефактов."""
    for src, dst in SANITIZE_PAIRS:
        text = text.replace(src, dst)
    return text


SEED_TEXT = (
    "The server processes the incoming request and produces a response. "
    "A distributed system consists of many components that communicate over "
    "the network. Memory bandwidth limits the speed of token generation on a "
    "single GPU. Speculative decoding uses a small draft model to propose "
    "several tokens that the main model verifies in parallel. Quantization "
    "reduces the size of the weights while trying to keep the quality of the "
    "output. The quick brown fox jumps over the lazy dog near the river bank. "
)


def make_prompt(target_tokens: int) -> str:
    """Легаси: повторяющийся англ. текст для стресс-теста. Для честных замеров НЕ использовать —
    он даёт ~100 % принятия спекуляции и завышает TG. Реалистичные промпты — в requests_real.json."""
    words = SEED_TEXT.split()
    need_words = max(8, int(target_tokens / 1.3))
    out = []
    while len(out) < need_words:
        out.extend(words)
    return " ".join(out[:need_words])


FILLER_PARAS = (
    "The history of cartography stretches back thousands of years, from Babylonian clay tablets "
    "to satellite imagery. Early maps were as much about power and belief as about geography, "
    "often placing the ruler's city at the centre of the world. "
    "Coffee spread from the Ethiopian highlands to Yemen and then to the Ottoman Empire, where "
    "the first coffeehouses became places of conversation, music and gossip. "
    "Coral reefs occupy less than one percent of the ocean floor yet support roughly a quarter of "
    "all marine species; warming water causes them to expel their symbiotic algae and bleach. "
    "The Voyager probes, launched in 1977, are now beyond the heliosphere, carrying a golden record "
    "with greetings in dozens of languages and images of human life. "
    "Modern cryptography rests on problems believed to be hard, such as factoring large integers "
    "or computing discrete logarithms, and the arrival of quantum computers threatens both. "
    "The bicycle gave workers cheap transport and gave women mobility independent of men, and its "
    "workshops trained the craftsmen who later built the first aircraft. "
    "Sleep is not a single uniform state; the brain cycles through light, deep and REM stages, "
    "and each stage appears to serve different functions for memory and repair. "
    "Volcanic ash preserves a record of past eruptions in layers of sediment, letting geologists "
    "date ancient events and estimate how often a region is likely to erupt again. "
)


def make_filler(target_tokens: int) -> str:
    """Длинный плейсхолдер-контекст для замера PP/TG на глубине. Текст разнообразный, но цикличный —
    годится только для измерения скорости на глубине, не для оценки качества."""
    words = FILLER_PARAS.split()
    need_words = max(8, int(target_tokens / 1.3))
    out = []
    while len(out) < need_words:
        out.extend(words)
    return " ".join(out[:need_words])


def http_json(url: str, payload=None, timeout=30):
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers=headers, method="POST" if data else "GET"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def http_ok(url: str, timeout=3):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def gpu_mem_mb():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return int(out.stdout.strip().splitlines()[0])
    except Exception:
        return -1


def kill_proc(proc):
    if proc is None or proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=15)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
        try:
            proc.wait(timeout=10)
        except Exception:
            pass


LOG_PATTERNS = [
    "load time",
    "model size",
    " KV ",
    "kv cache",
    "n_ctx",
    "CUDA0 model buffer",
    "CUDA0 compute buffer",
    "offloaded",
    "draft",
    "n_layer",
    "graph",
    "MTP",
    "fit",
    "tensor",
    "context size",
]


def log_digest(path):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except Exception:
        return []
    hits = [
        ln.rstrip()
        for ln in text.splitlines()
        if any(p.lower() in ln.lower() for p in LOG_PATTERNS)
    ]
    return hits[-60:]


def run_test(name, port, server_exe, args, reqs, timeout_load=600, timeout_req=900):
    cmd = [server_exe, "--host", "127.0.0.1", "--port", str(port), "--no-webui"] + args
    log_path = os.path.join(RUNS, f"{name}.log")
    logf = open(log_path, "w", encoding="utf-8", errors="replace")

    rec = {
        "name": name,
        "time": datetime.now().isoformat(timespec="seconds"),
        "args": [sanitize(x) for x in args],
        "log": os.path.relpath(log_path, ROOT),
        "load_s": None,
        "vram_before_mb": gpu_mem_mb(),
        "vram_after_load_mb": None,
        "vram_after_req_mb": None,
        "props": {},
        "runs": {},
        "error": None,
        "log_digest": [],
    }
    proc = None
    try:
        t0 = time.time()
        proc = subprocess.Popen(
            cmd, cwd=os.path.dirname(server_exe), stdout=logf, stderr=subprocess.STDOUT
        )
        ok = False
        while time.time() - t0 < timeout_load:
            if http_ok(f"http://127.0.0.1:{port}/health"):
                ok = True
                break
            if proc.poll() is not None:
                break
            time.sleep(1.0)
        rec["load_s"] = round(time.time() - t0, 1)
        if not ok:
            rec["error"] = "server did not become healthy"
        else:
            time.sleep(2.0)
            rec["vram_after_load_mb"] = gpu_mem_mb()
            try:
                props = http_json(f"http://127.0.0.1:{port}/props")
                rec["props"] = {
                    "n_ctx": props.get("default_generation_settings", {}).get("n_ctx"),
                    "chat_template": bool(props.get("chat_template")),
                }
            except Exception as e:
                rec["props"] = {"error": str(e)}

            for rq0 in reqs:
                rq = dict(rq0)
                tag = rq.pop("tag")
                filler = rq.pop("filler", None)
                filler_text = make_filler(filler) if filler else ""
                is_chat = "messages" in rq
                body = {
                    "temperature": rq.pop("temperature", 1.0),
                    "top_p": rq.pop("top_p", 0.95),
                    "top_k": rq.pop("top_k", 20),
                    "min_p": rq.pop("min_p", 0.0),
                    "presence_penalty": rq.pop("presence_penalty", 0.0),
                    "repeat_penalty": rq.pop("repeat_penalty", 1.0),
                    "seed": rq.pop("seed", 42),
                    "cache_prompt": rq.pop("cache_prompt", False),
                    "stream": False,
                }
                if is_chat:
                    msgs = [dict(m) for m in rq.pop("messages")]
                    if filler_text:
                        for m in msgs:
                            if m.get("role") == "user":
                                m["content"] = (
                                    filler_text + "\n\n" + (m.get("content") or "")
                                )
                                break
                    body["messages"] = msgs
                    body["max_tokens"] = rq.pop("n_predict")
                    url = f"http://127.0.0.1:{port}/v1/chat/completions"
                else:
                    if "prompt" in rq:
                        base_prompt = rq.pop("prompt")
                    else:
                        base_prompt = make_prompt(rq.pop("target"))
                    body["prompt"] = (
                        (filler_text + "\n\n" + base_prompt)
                        if filler_text
                        else base_prompt
                    )
                    body["n_predict"] = rq.pop("n_predict")
                    url = f"http://127.0.0.1:{port}/completion"
                body.update(rq)
                t1 = time.time()
                try:
                    resp = http_json(url, body, timeout=timeout_req)
                    t = resp.get("timings", {}) or {}
                    out = {
                        "wall_s": round(time.time() - t1, 1),
                        "prompt_n": t.get("prompt_n"),
                        "pp_t_s": t.get("prompt_per_second"),
                        "predicted_n": t.get("predicted_n"),
                        "tg_t_s": t.get("predicted_per_second"),
                        "draft_n": t.get("draft_n"),
                        "draft_n_accepted": t.get("draft_n_accepted"),
                        "stop_type": (resp.get("stop_type") or "")[:20],
                    }
                    if t.get("draft_n"):
                        out["accept_%"] = round(
                            100.0 * (t.get("draft_n_accepted") or 0) / t["draft_n"], 1
                        )
                    if is_chat:
                        msg = (resp.get("choices") or [{}])[0].get("message") or {}
                        out["content_head"] = (msg.get("content") or "")[:160]
                        out["reasoning_head"] = (msg.get("reasoning_content") or "")[
                            :160
                        ]
                        out["usage"] = resp.get("usage")
                        ans_path = os.path.join(RUNS, f"{name}-{tag}-answer.txt")
                        with open(ans_path, "w", encoding="utf-8") as af:
                            af.write("=== reasoning_content ===\n")
                            af.write(msg.get("reasoning_content") or "")
                            af.write("\n=== content ===\n")
                            af.write(msg.get("content") or "")
                        out["answer_file"] = os.path.relpath(ans_path, ROOT)
                    rec["runs"][tag] = out
                except Exception as e:
                    rec["runs"][tag] = {"error": f"{type(e).__name__}: {e}"}
                rec["vram_after_req_mb"] = gpu_mem_mb()
        rec["log_digest"] = [sanitize(x) for x in log_digest(log_path)]
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"
    finally:
        kill_proc(proc)
        logf.close()
        if SANITIZE_PAIRS:
            try:
                text = open(log_path, encoding="utf-8", errors="replace").read()
                open(log_path, "w", encoding="utf-8").write(sanitize(text))
            except Exception:
                pass
        time.sleep(2.0)
    return rec


def fmt(rec):
    if rec.get("error"):
        return f"  ОШИБКА: {rec['error']}"
    lines = []
    lines.append(
        f"  загрузка {rec['load_s']} c | VRAM после загрузки {rec['vram_after_load_mb']} MiB"
    )
    for tag, r in rec["runs"].items():
        if not isinstance(r, dict) or r.get("tg_t_s") is None:
            continue
        acc = f" | принято {r['accept_%']}%" if r.get("accept_%") is not None else ""
        lines.append(
            f"  [{tag}] TG {r['tg_t_s']:.2f} t/s | PP {r['pp_t_s']:.0f} t/s | промпт {r['prompt_n']} tok, ген {r['predicted_n']} tok{acc}"
        )
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("suite", help="JSON-файл набора тестов")
    ap.add_argument(
        "--only", default=None, help="выполнить только тесты с этим префиксом имени"
    )
    ap.add_argument("--base-port", type=int, default=9941)
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="показать раскрытые пути/аргументы тестов и выйти (без запуска сервера)",
    )
    a = ap.parse_args()

    suite = expand_obj(json.load(open(a.suite, encoding="utf-8")))
    server_exe = suite["server"]
    model = suite["model"]
    common = suite.get("common", [])
    reqs = suite.get("requests", "requests_real.json")
    if isinstance(reqs, str):
        with open(os.path.join(ROOT, reqs), encoding="utf-8") as f:
            reqs = json.load(f)

    results_path = os.path.join(RUNS, "results.jsonl")
    tests = suite["tests"]
    if a.only:
        tests = [t for t in tests if t["name"].startswith(a.only)]

    if a.dry_run:
        print(f"server: {server_exe}")
        print(f"model : {model}")
        for t in tests:
            args = ["--model", model] + common + t.get("args", [])
            print(f"  {t['name']}: {' '.join(args)}")
        return

    for i, t in enumerate(tests):
        name = t["name"]
        port = a.base_port + i
        args = ["--model", model] + common + t.get("args", [])
        print(f"[{i + 1}/{len(tests)}] {name}")
        rec = run_test(name, port, server_exe, args, t.get("requests", reqs))
        print(fmt(rec))
        with open(results_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"\nРезультаты: {results_path}")


if __name__ == "__main__":
    main()
