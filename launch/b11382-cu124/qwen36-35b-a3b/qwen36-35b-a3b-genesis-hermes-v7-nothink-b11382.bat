@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..\..\..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem --- launch log: dated file under %PROJECT_DIR%\logs\ ---
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmmss"') do set "TS=%%I"
if not defined TS set "TS=run%RANDOM%"
set "LOGDIR=%PROJECT_DIR%\logs"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
set "LOG=%LOGDIR%\%~n0_%TS%.log"
echo Log: %LOG%
rem ============================================================================
rem  Genesis Hermes V7 35B-A3B (mradermacher i1-IQ4_XS, 17.9 ГиБ, MoE Qwen3.6-35B-A3B).
rem  БЕЗ спекуляции: у этого рекванта нет MTP-головы (в оригинале она отдельным APEX-MTP-файлом).
rem  Модель не влезает в 16 ГБ -> --fit on отгружает ~3.7 ГиБ на CPU; c=32768, KV q4_0.
rem  RP-скрин (nothink): RU 100 %, TG 41.6 t/s, но роль слабая — судьи 3.81 (gemma) / 2.90 (Qwen):
rem  персонаж 2.0-2.7, инициатива 2.0-3.3, память 2.7-3.3 — на уровне базы, НЕ апгрейд. См. §5.12.
rem  think у Qwen3.6 в llama.cpp ломается (незакрытый канал) — режим не делаем.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Qwen3.6-35B-A3B-Uncensored-Genesis-Hermes-V7-dequantized-i1-GGUF\Qwen3.6-35B-A3B-Uncensored-Genesis-Hermes-V7-dequantized.i1-IQ4_XS.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9933 --alias "Genesis-Hermes-V7-35B-A3B-nothink" ^
  -np 1 -c 32768 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja ^
  --reasoning off --reasoning-budget 0 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
