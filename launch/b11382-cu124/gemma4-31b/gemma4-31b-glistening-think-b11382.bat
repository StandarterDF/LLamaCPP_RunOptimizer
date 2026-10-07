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
rem  Gemma-4-31B Glistening-Gem-v2.1 (sophosympatheia, i1-IQ3_XXS, dense) — RP, Thinking.
rem  Якорный merge: MeroMero-v2 + Artemis-v1 + Ortenzya-heretic + base gemma-4-31B-it.
rem  Оговорка: в нашем прогоне think давал ПУСТЫЕ ответы (0 символов) — незакрытый <channel|> (7 из 18).
rem  RP-балл (2 судьи): Gemma 3.60 · Qwen 3.02 (N=5/11) — неполноценно. Использовать nothink-конфиг.
rem  Подробности: docs\models.md, docs\quality\rp-quality-eval.md.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Glistening-Gem-31B-v2.1-i1-GGUF\Glistening-Gem-31B-v2.1.i1-IQ3_XXS.gguf"
set "DRAFT=%MODELS_DIR%\mradermacher\Gemma-4-Queen-31B-it-uncensored-heretic-i1-GGUF\gemma-4-31B-it-assistant.Q4_K_M.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9935 --alias "Glistening-Gem-31B-v2.1-think" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.75 ^
  -md "%DRAFT%" ^
  --jinja --reasoning on --reasoning-effort low --reasoning-budget 1024 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
