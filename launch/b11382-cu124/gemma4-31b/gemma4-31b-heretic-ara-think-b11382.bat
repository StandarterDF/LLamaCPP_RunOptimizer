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
rem  Gemma-4-31B-it-heretic-ARA (i1-IQ3_XXS, dense) — RP, Think.
rem  База + abliteration Heretic (ARA), НЕ RP-тюн. RP-скрин: Gemma 4.52 / Qwen 3.58.
rem  Think здесь РАБОЧИЙ: канал <channel|> закрывается (редкость для Gemma-31B).
rem  Мышление: --reasoning on --reasoning-effort low --reasoning-budget 1024.
rem  Сэмплинг RU-safe (как в RP-оценке): temp 0.6, min-p 0.1, top-k off, top-p 0.95.
rem  Спекуляция: общий Gemma-4-31B MTP-assistant (nmax5 pmin0.75), c=51200, KV q4_0.
rem  Русский: «Чисто» 100 %, но строгий судья ловит опечатки (рус 3.17) и «литературщину».
rem  Разбор: docs\quality\base-models-rp-eval.md §4.3.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\gemma-4-31b-it-heretic-ara-i1-GGUF\gemma-4-31b-it-heretic-ara.i1-IQ3_XXS.gguf"
set "DRAFT=%MODELS_DIR%\mradermacher\Gemma-4-Queen-31B-it-uncensored-heretic-i1-GGUF\gemma-4-31B-it-assistant.Q4_K_M.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Gemma-4-31B-heretic-ara-think" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.75 ^
  -md "%DRAFT%" ^
  --jinja --chat-template-file "%LLAMA_DIR%\gemma4.jinja" ^
  --reasoning on --reasoning-effort low --reasoning-budget 1024 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
