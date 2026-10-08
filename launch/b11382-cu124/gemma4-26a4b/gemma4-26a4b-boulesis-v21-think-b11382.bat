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
rem  Gemma-4-26B-A4B Boulesis v2.1 (SubMaroon, mradermacher i1-IQ4_XS, MoE) — RP, Think.
rem  Think У ХОЖИТ, но хуже NoThink: gemma 4.27 против 4.48, Qwen 3.67 против 3.56;
rem  слабее персонаж (3.33) и проза (3.50), и модель подмешивает «мысли в кавычках» —
rem  пояснения игроку вместо переживаний. Для работы берите -nothink (55 t/s, Чисто 100 %).
rem  ОГОВОРКА: в 1 из 6 ответов (seduction, сид 33) наружу утек черновик-разметка
rem  («*Drafting idea:*», «*Check against rules:*», «*Text:*») и смесь EN/RU в строке —
rem  strip_channels это не чистит (нет тега канала). Русский в think: 86.6 %, TG 59.5 t/s.
rem  Контекст 51200 (измеренный). Подробности: docs\quality\rp-quality-eval.md §5.16.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Boulesis-v2.1-26B-A4B-i1-GGUF\Boulesis-v2.1-26B-A4B.i1-IQ4_XS.gguf"
set "TEMPLATE=%LLAMA_DIR%\gemma4.jinja"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Boulesis-v2.1-26B-A4B-think" ^
  --fit on -fa on --load-mode none -t 14 -tb 14 -b 2048 -ub 512 ^
  -np 1 -c 51200 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja --chat-template-file "%TEMPLATE%" --chat-template-kwargs "{\"enable_thinking\":true}" ^
  --reasoning on --reasoning-effort low --reasoning-budget 1024 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause