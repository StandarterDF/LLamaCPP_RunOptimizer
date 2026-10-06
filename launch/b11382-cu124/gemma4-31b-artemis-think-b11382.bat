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
rem  Artemis-31B-v1.2 (mradermacher i1-IQ3_XXS, dense gemma4) — RP, Thinking.
rem  Аналог gemma4-31b-artemis-nothink-b11382.bat, но с включённым мышлением.
rem  --reasoning on включает thinking. --reasoning-effort low передаётся шаблону,
rem  НО текущий gemma4.jinja reasoning_effort игнорирует: реальный лимит длины
rem  мышления — флаг --reasoning-budget (по умолчанию -1, без ограничения).
rem  Спекуляция: общий Gemma-4-31B MTP-assistant (nmax5 pmin0.75), c=51200.
rem  Подробности и оговорки: docs\sampling-quality.md.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Artemis-31B-v1.2-i1-GGUF\Artemis-31B-v1.2.i1-IQ3_XXS.gguf"
set "DRAFT=%MODELS_DIR%\mradermacher\Gemma-4-Queen-31B-it-uncensored-heretic-i1-GGUF\gemma-4-31B-it-assistant.Q4_K_M.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Artemis-31B-v1.2-think" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.75 ^
  -md "%DRAFT%" ^
  --jinja --reasoning on --reasoning-effort low ^
  --temp 0.7 --min-p 0.05 --top-k 0 --top-p 1.0 --dry-multiplier 0.8 --dry-base 1.75 --dry-allowed-length 2 --dry-penalty-last-n 256
pause
