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
rem  Gemma-4-31B Giftige-Blume-v1-StyleSwap (Casual-Autopsy, i1-IQ3_XXS, dense) — RP, NoThink.
rem  StyleSwap: Giftige-Blume-v1 + StyleTune (tensor swap). Своей base НЕТ, привит StyleTune.
rem  Наш RP-прогон: Чисто 78%, Cyr 97.5%, EN-стоп 4.89 (англ. вставки!), TG 23.3 t/s.
rem  RP-балл (2 судьи, полный набор): Gemma 3.64 · Qwen 2.64 — худший из проверенных; для RU НЕ берём.
rem  Риск: англ. вставки, как у StyleTune-31B (RU 17-0%). Проверять русский отдельно.
rem  Подробности: docs\models.md, docs\quality\rp-quality-eval.md.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Giftige-Blume-31B-v1-StyleSwap-i1-GGUF\Giftige-Blume-31B-v1-StyleSwap.i1-IQ3_XXS.gguf"
set "DRAFT=%MODELS_DIR%\mradermacher\Gemma-4-Queen-31B-it-uncensored-heretic-i1-GGUF\gemma-4-31B-it-assistant.Q4_K_M.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9932 --alias "Giftige-Blume-StyleSwap-31B-nothink" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.75 ^
  -md "%DRAFT%" ^
  --jinja --reasoning off --reasoning-budget 0 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
