@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%i in ("%~dp0..\..\..") do set "PROJECT_DIR=%%~fi"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem --- launch log: dated file under %PROJECT_DIR%\logs\ ---
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmmss"') do set "TS=%%i"
if not defined TS set "TS=run%RANDOM%"
set "LOGDIR=%PROJECT_DIR%\logs"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
set "LOG=%LOGDIR%\%~n0_%TS%.log"
echo Log: %LOG%
rem ============================================================================
rem  Qwen3.6-27B Fable-Fusion-711 (DavidAU, NEO-MAX NEO-MTP, IQ2_M, 11.3 GB, dense) - RP, С мышлением.
rem  ОГРАНИЧЕНИЕ: в seduction-сценах модель дублирует ответ (сначала текст без канала, затем с ним) -
rem  технический брак шаблона/вывода; школьная сцена think отвечает нормально. Панель Think 3.45 (≈ No).
rem  Рабочий режим - nothink (qwen36-27b-fable-fus-711-nothink-b11382.bat).
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\DavidAU\Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic-NM-DAU-NEO-MAX-MTP-GGUF\Qwen3.6-27B-Fable-Fus-711-UnHeretic-NM-DAU-NEO-MAX-NEO-MTP-IQ2_M.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Qwen3.6-27B-Fable-Fus-711-think" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.75 ^
  --reasoning on --reasoning-budget 1024 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
