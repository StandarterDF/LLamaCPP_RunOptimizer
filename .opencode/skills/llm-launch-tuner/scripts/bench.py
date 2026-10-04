#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Харнесс бенчмарка llama-server (универсальный, только стандартная библиотека).

Назначение: для каждого теста из suite-JSON поднять свой llama-server, дождаться готовности,
замерить время загрузки и VRAM, прогнать набор запросов (сырой текст и/или чат через шаблон),
сохранить тайминги в results.jsonl и логи сервера рядом.

Запуск:
  python bench.py suite.json [--only ПРЕФИКС] [--base-port 9941] [--out-dir runs]

Формат suite.json:
{
  "server": "C:/llama.cpp/llama-server.exe",
  "model":  "D:/models/model.gguf",
  "common": ["-np", "1"],                    // общие аргументы для всех тестов
  "requests": [                              // запросы по умолчанию
    { "tag": "short", "target": 1000, "n_predict": 128 },
    { "tag": "long",  "target": 8000, "n_predict": 32 },
    { "tag": "chat",  "n_predict": 320,
      "messages": [{"role":"user","content":"..."}] }
  ],
  "tests": [
    { "name": "01_base", "args": ["-c","81920","-fa","on"] },
    { "name": "02_alt",  "args": ["-c","65536"],
      "requests": [ ... ]                    // опционально: свои запросы для теста
  ]
}

Примечания:
- port и --host 127.0.0.1/--no-webui добавляются автоматически.
- VRAM берётся из nvidia-smi; если его нет — пишется -1 (не критично).
- Все файлы пишутся только в --out-dir.
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

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SANITIZE_KEYS = ("LLAMA_SERVER", "LLAMA_DIR", "MODELS_DIR", "PROJECT_DIR")


def _load_env():
    """Плейсхолдеры ${...} и санитизация: env.local.json рядом со скриптом или в cwd."""
    env_map = dict(os.environ)
    local = {}
    for path in (
        os.path.join(os.getcwd(), "env.local.json"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "env.local.json"),
    ):
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    local = json.load(f)
                break
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
    words = SEED_TEXT.split()
    need = max(8, int(target_tokens / 1.3))
    out = []
    while len(out) < need:
        out.extend(words)
    return " ".join(out[:need])


def http_json(url: str, payload=None, timeout=30):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST" if data else "GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def http_ok(url: str, timeout=3) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def gpu_mem_mb() -> int:
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


LOG_PATTERNS = [
    "load time",
    "model size",
    " KV ",
    "kv cache",
    "n_ctx",
    "CUDA0",
    "offloaded",
    "draft",
    "n_layer",
    "graph",
    "fit",
    "context size",
    "error",
]


def log_digest(path):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except Exception:
        return []
    return [
        ln.rstrip()
        for ln in text.splitlines()
        if any(p.lower() in ln.lower() for p in LOG_PATTERNS)
    ][-60:]


def run_test(
    name, port, server_exe, args, reqs, runs_dir, timeout_load=600, timeout_req=900
):
    os.makedirs(runs_dir, exist_ok=True)
    cmd = [server_exe, "--host", "127.0.0.1", "--port", str(port), "--no-webui"] + args
    log_path = os.path.join(runs_dir, f"{name}.log")
    logf = open(log_path, "w", encoding="utf-8", errors="replace")
    rec = {
        "name": name,
        "time": datetime.now().isoformat(timespec="seconds"),
        "args": [sanitize(x) for x in args],
        "log": os.path.relpath(log_path, runs_dir),
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
                    "n_ctx": (props.get("default_generation_settings") or {}).get(
                        "n_ctx"
                    ),
                    "chat_template": bool(props.get("chat_template")),
                }
            except Exception as e:
                rec["props"] = {"error": str(e)}

            for rq0 in reqs:
                rq = dict(rq0)
                tag = rq.pop("tag")
                is_chat = "messages" in rq
                body = {
                    "temperature": rq.pop("temperature", 1.0),
                    "top_p": rq.pop("top_p", 0.95),
                    "top_k": rq.pop("top_k", 20),
                    "min_p": rq.pop("min_p", 0.0),
                    "presence_penalty": rq.pop("presence_penalty", 0.0),
                    "repeat_penalty": rq.pop("repeat_penalty", 1.0),
                    "seed": rq.pop("seed", 42),
                    "cache_prompt": False,
                    "stream": False,
                }
                if is_chat:
                    body["messages"] = rq.pop("messages")
                    body["max_tokens"] = rq.pop("n_predict")
                    url = f"http://127.0.0.1:{port}/v1/chat/completions"
                else:
                    body["prompt"] = make_prompt(rq.pop("target"))
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
                        ans_path = os.path.join(runs_dir, f"{name}-{tag}-answer.txt")
                        with open(ans_path, "w", encoding="utf-8") as af:
                            af.write("=== reasoning_content ===\n")
                            af.write(msg.get("reasoning_content") or "")
                            af.write("\n=== content ===\n")
                            af.write(msg.get("content") or "")
                        out["answer_file"] = os.path.relpath(ans_path, runs_dir)
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
    lines = [
        f"  загрузка {rec['load_s']} c | VRAM после загрузки {rec['vram_after_load_mb']} MiB"
    ]
    for tag, r in rec["runs"].items():
        if not isinstance(r, dict) or r.get("tg_t_s") is None:
            continue
        acc = f" | принято {r['accept_%']}%" if r.get("accept_%") is not None else ""
        lines.append(
            f"  [{tag}] TG {r['tg_t_s']:.2f} t/s | PP {r['pp_t_s']:.0f} t/s | "
            f"промпт {r['prompt_n']} tok, ген {r['predicted_n']} tok{acc}"
        )
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Бенчмарк llama-server по suite-JSON")
    ap.add_argument("suite", help="JSON-файл набора тестов")
    ap.add_argument(
        "--only", default=None, help="выполнить только тесты с этим префиксом имени"
    )
    ap.add_argument("--base-port", type=int, default=9941)
    ap.add_argument("--out-dir", default="runs", help="папка для результатов и логов")
    a = ap.parse_args()

    suite = expand_obj(json.load(open(a.suite, encoding="utf-8")))
    server_exe = suite["server"]
    model = suite["model"]
    common = suite.get("common", [])
    reqs = suite.get(
        "requests",
        [
            # Быстрый режим по умолчанию; для финальной валидации увеличьте (3 задачи, промпт ~12k).
            {"tag": "short", "target": 1000, "n_predict": 128},
            {"tag": "long", "target": 8000, "n_predict": 32},
        ],
    )
    tests = suite["tests"]
    if a.only:
        tests = [t for t in tests if t["name"].startswith(a.only)]

    results_path = os.path.join(a.out_dir, "results.jsonl")
    os.makedirs(a.out_dir, exist_ok=True)
    for i, t in enumerate(tests):
        name = t["name"]
        port = a.base_port + i
        args = ["--model", model] + common + t.get("args", [])
        print(f"[{i + 1}/{len(tests)}] {name}")
        rec = run_test(name, port, server_exe, args, t.get("requests", reqs), a.out_dir)
        print(fmt(rec))
        with open(results_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"\nРезультаты: {results_path}")


if __name__ == "__main__":
    main()
