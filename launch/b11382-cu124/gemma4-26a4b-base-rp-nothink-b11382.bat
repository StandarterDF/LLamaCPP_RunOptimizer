@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..\..") do set "PROJECT_DIR=%%~fI"
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
rem  Gemma-4-26B-A4B-it (base instruct, UD-IQ3_XXS, 10.63 GB) — RP baseline, БЕЗ мышления.
rem  Сэмплинг RU-safe temp0.6/min-p0.1/top-k0/top-p0.95; c=51200, KV q4_0, без спекуляции (нет MTP).
rem  RP-скрин (2 сцены, судьи): лучшая из трёх базовых, живая проза и характер, RU 100 %.
rem  Слабости: повторы метафор, скатывание в агрессию, быстро «сдаётся» в соблазне.
rem  ВНИМАНИЕ: её высокий балл у gemma-судьи — самооценка; перекрёстно (Qwen-судья) ниже. См. docs\base-models-rp-eval.md.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\unsloth\gemma-4-26B-A4B-it-GGUF\gemma-4-26B-A4B-it-UD-IQ3_XXS.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Gemma-4-26B-A4B-base-rp-nothink" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja --chat-template-file "%LLAMA_DIR%\gemma4.jinja" ^
  --reasoning off --reasoning-budget 0 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
