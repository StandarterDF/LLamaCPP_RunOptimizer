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
rem  Qwen3.6-27B Fable-Fusion-711 (DavidAU, IQ2_M, dense heretic, MTP) - RP, БЕЗ мышления.
rem  АЛЬТЕРНАТИВНЫЙ СЭМПЛИНГ АВТОРА (instruct): temp0.7 / top_p0.80 / top_k20 /
rem  min_p0 / presence_penalty1.5 (карточка модели). Наш замер (панель 4 судей):
rem    - голос резче, повторов меньше, TTR 0.878 -> 0.933, ответы используют детали карточки;
rem    - но ответы короче, "ум" и "инициатива" ниже => панель 3.30 против 3.46 у стандарта.
rem  Дефолт - qwen36-27b-fable-fus-711-nothink-b11382.bat (RU-safe, 3.46). Разбор - §5.18.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\DavidAU\Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic-NM-DAU-NEO-MAX-MTP-GGUF\Qwen3.6-27B-Fable-Fus-711-UnHeretic-NM-DAU-NEO-MAX-NEO-MTP-IQ2_M.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Qwen3.6-27B-Fable-Fus-711-author" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.75 ^
  --reasoning off --reasoning-budget 0 ^
  --temp 0.7 --top-p 0.8 --top-k 20 --min-p 0 --presence-penalty 1.5 --repeat-penalty 1.0
pause
