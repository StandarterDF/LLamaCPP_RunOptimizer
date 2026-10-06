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
rem  Gemma-4-26B-A4B Goetia v1.6 (Naphula, i1-IQ3_XXS, MoE) — RP, NoThink.
rem  Мерж moe_della: ~28 доноров микровесами + lm_head/embed (Orion, Pantheon).
rem  Наш RP-балл (LLM-судья): 4.23; русский 100% (RU-safe) / 83% (пресет карточки).
rem  Быстрый MoE ~73 t/s. Без спекуляции (совместимость MTP не проверялась).
rem  Think в llama.cpp /completion НЕпригоден: модель не закрывает канал <channel|>.
rem  Подробности: docs\models.md, docs\rp-quality-eval.md.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Goetia-26B-A4B-v1.6-i1-GGUF\Goetia-26B-A4B-v1.6.i1-IQ3_XXS.gguf"
set "TEMPLATE=%LLAMA_DIR%\gemma4.jinja"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Goetia-26B-A4B-nothink" ^
  --fit on -fa on --load-mode none -t 14 -tb 14 -b 2048 -ub 512 ^
  -np 1 -c 65536 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja --chat-template-file "%TEMPLATE%" ^
  --reasoning off --reasoning-budget 0 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
