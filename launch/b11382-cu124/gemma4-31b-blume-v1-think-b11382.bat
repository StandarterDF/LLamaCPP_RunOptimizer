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
rem  Gemma-4-31B Giftige-Blume-v1 (Blazed-Forge, i1-IQ3_XXS, dense) — RP, Thinking.
rem  3-фазный merge; финал della_linear на gemma-4-31B-it (вес 0.70-0.75), у доноров embed/lm_head=0.
rem  CaliperBench V3: Combined RP 69.3 (№1), RP 74.7 / ERP 67.7 / DarkRP 69.3.
rem  Think без лимита (--reasoning-budget -1, --reasoning-effort default) — проверено:
rem  пустых 2/18 (было 4/18 при бюджете 1024), но качество то же (Gemma 4.36 / Qwen 3.41 ≈ NoThink), повторы хуже.
rem  RP-балл судей (Think, бюджет 1024): Gemma 4.53 (N=8) · Qwen 3.26 (N=13). Рабочий режим — NoThink.
rem  Подробности: docs\models.md, docs\quality\rp-quality-eval.md.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Gemma-4-Giftige-Blume-31B-v1-i1-GGUF\Gemma-4-Giftige-Blume-31B-v1.i1-IQ3_XXS.gguf"
set "DRAFT=%MODELS_DIR%\mradermacher\Gemma-4-Queen-31B-it-uncensored-heretic-i1-GGUF\gemma-4-31B-it-assistant.Q4_K_M.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9937 --alias "Giftige-Blume-31B-v1-think" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.75 ^
  -md "%DRAFT%" ^
  --jinja --reasoning on --reasoning-effort default --reasoning-budget -1 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
