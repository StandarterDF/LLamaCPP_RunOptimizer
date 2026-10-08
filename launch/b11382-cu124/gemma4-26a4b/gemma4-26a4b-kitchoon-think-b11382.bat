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
rem  Gemma-4-26B-A4B Kitchoon (SubMaroon; mradermacher i1-IQ4_XS, MoE) — RP, Think.
rem  Тот же NoThink-конфиг, включён reasoning (budget 1024, effort low).
rem  РЕЗУЛЬТАТЫ think: ❌ НЕПРИГОДЕН — во всех 6 ответах английский reasoning/план
rem  («Kira Sokolova (17, 11 "B"…)», «*Drafting P1:*») утекает в видимый текст, русская реплика
rem  обрывается; Чисто 0 %, EN-стоп 158/1k, Cyr 42 %, панель 2.09. Системная утечка канала,
rem  не разовый сбой. Рабочий режим — только -nothink (и он слабый).
rem  Спекуляции нет. Контекст 51200. Подробности: docs\quality\rp-quality-eval.md §5.17.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Kitchoon-26B-A4B-i1-GGUF\Kitchoon-26B-A4B.i1-IQ4_XS.gguf"
set "TEMPLATE=%LLAMA_DIR%\gemma4.jinja"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Kitchoon-26B-A4B-think" ^
  --fit on -fa on --load-mode none -t 14 -tb 14 -b 2048 -ub 512 ^
  -np 1 -c 51200 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja --chat-template-file "%TEMPLATE%" --chat-template-kwargs "{\"enable_thinking\":true}" ^
  --reasoning on --reasoning-effort low --reasoning-budget 1024 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
