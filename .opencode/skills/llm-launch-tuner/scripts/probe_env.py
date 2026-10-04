#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Снимок окружения для подбора конфига запуска LLM. Только стандартная библиотека,
ничего не устанавливает и не меняет в системе.

Запуск:
  python probe_env.py [--llama-server C:/llama.cpp/llama-server.exe] [--model D:/models/m.gguf]

Печатает: ОС, CPU, RAM, GPU (nvidia-smi), версию llama-server, размер и magic модели.
"""

import argparse
import ctypes
import os
import platform
import shutil
import struct
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def ram_gb():
    try:
        if sys.platform == "win32":

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            st = MEMORYSTATUSEX()
            st.dwLength = ctypes.sizeof(st)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
            return round(st.ullTotalPhys / 1e9, 1), round(st.ullAvailPhys / 1e9, 1)
        if sys.platform.startswith("linux"):
            mem = {}
            for line in open("/proc/meminfo"):
                k, v = line.split(":", 1)
                mem[k] = int(v.strip().split()[0])
            return round(mem["MemTotal"] / 1e6, 1), round(mem["MemAvailable"] / 1e6, 1)
        if sys.platform == "darwin":
            total = int(
                subprocess.run(
                    ["sysctl", "-n", "hw.memsize"], capture_output=True, text=True
                ).stdout
            )
            return round(total / 1e9, 1), None
    except Exception:
        pass
    return None, None


def gpu_info():
    if shutil.which("nvidia-smi"):
        try:
            out = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,driver_version,compute_cap",
                    "--format=csv,noheader",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            ).stdout.strip()
            if out:
                return "nvidia-smi:\n    " + out.replace("\n", "\n    ")
        except Exception as e:
            return f"nvidia-smi ошибка: {e}"
    if shutil.which("rocm-smi"):
        try:
            out = subprocess.run(
                ["rocm-smi", "--showproductname", "--showmeminfo", "vram"],
                capture_output=True,
                text=True,
                timeout=15,
            ).stdout.strip()
            return "rocm-smi:\n    " + out[:1200]
        except Exception as e:
            return f"rocm-smi ошибка: {e}"
    return "GPU-утилиты не найдены (nvidia-smi/rocm-smi)"


def llama_version(path):
    if not path:
        path = shutil.which("llama-server") or shutil.which("llama-server.exe") or ""
    if not path or not os.path.exists(path):
        return "llama-server не указан/не найден"
    try:
        r = subprocess.run(
            [path, "--version"], capture_output=True, text=True, timeout=30
        )
        text = ((r.stdout or "") + (r.stderr or "")).strip()
        return f"{path}\n    " + "\n    ".join(text.splitlines()[:4])
    except Exception as e:
        return f"{path}: ошибка запуска: {e}"


def model_info(path):
    if not path:
        return "модель не указана"
    if not os.path.exists(path):
        return f"{path}: файл не найден"
    size_gb = round(os.path.getsize(path) / 1e9, 2)
    try:
        with open(path, "rb") as f:
            magic = f.read(4)
            ver = struct.unpack("<I", f.read(4))[0]
        ok = "GGUF" if magic == b"GGUF" else f"неизвестный magic {magic!r}"
    except Exception as e:
        ok, ver = f"ошибка чтения: {e}", "?"
    return f"{path}\n    размер: {size_gb} GB; формат: {ok}; gguf-версия: {ver}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--llama-server", default=None)
    ap.add_argument("--model", default=None)
    a = ap.parse_args()

    total, avail = ram_gb()
    print("=== ОС ===")
    print(
        f"  {platform.system()} {platform.release()} ({platform.machine()}), Python {platform.python_version()}"
    )
    print("=== CPU ===")
    print(f"  {platform.processor() or '?'} | ядер: {os.cpu_count()}")
    print("=== RAM ===")
    print(f"  всего: {total} GB" + (f", свободно: {avail} GB" if avail else ""))
    print("=== GPU ===")
    print("  " + gpu_info())
    print("=== llama.cpp ===")
    print("  " + llama_version(a.llama_server))
    print("=== Модель ===")
    print("  " + model_info(a.model))
    print(
        "\nДальше: соберите suite.json и запустите scripts/bench.py (см. references/methodology.md)."
    )


if __name__ == "__main__":
    main()
