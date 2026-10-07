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
rem  WaifuGemma4-26b-a4b-v1 (i1-IQ3_XXS) — RP, NoThink, русский.
rem  Единственная найденная RU-обученная RP-модель на Gemma 4 (ru/uk).
rem  MoE 26B-A4B, без MTP: без спекуляции 80-90 t/s (на RP у Gemma-26B MTP вредит).
rem  Русский тест: ЛУЧШИЙ пресет — карточка (temp1.0/min-p0.03) = 96% чистых.
rem  Низкая T её ПОРТИТ: temp0.4 = 79%, temp0.7+DRY = 79% (BPE-склейки). Не понижать!
rem  Шаблон встроенный (--jinja) отработал чисто, gemma4.jinja не требуется.
rem  Подробности: docs\quality\sampling-quality.md.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\hiwaifu-research\WaifuGemma4-26b-a4b-v1-i1-GGUF\WaifuGemma4-26b-a4b-v1.i1-IQ3_XXS.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "WaifuGemma4-26B-nothink" ^
  --fit on -fa on --load-mode none -t 14 -tb 14 -b 2048 -ub 512 ^
  -np 1 -c 65536 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja --reasoning off --reasoning-budget 0 ^
  --temp 1.0 --min-p 0.03 --top-k 0 --top-p 1.0 --dry-multiplier 0.8 --dry-penalty-last-n 64
pause
