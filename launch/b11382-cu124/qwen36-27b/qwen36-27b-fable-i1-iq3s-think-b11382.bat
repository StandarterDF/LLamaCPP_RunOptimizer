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
rem  Qwen3.6-27B Fable-Fusion-711 (mradermacher i1-IQ3_S, imatrix, 11.7 ГиБ) - RP, С мышлением.
rem  БЕЗ спекуляции. c=51200, KV q4_0, RU-safe сэмплинг, reasoning-budget 1024.
rem  Здесь think рабочий (панель Think 3.79 - лучший не-Gemma; у IQ2_M дублировал ответ).
rem  Русский 100 %, 18 t/s. Рабочий режим всё равно NoThink (быстрее).
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic-NM-DAU-MTP-i1-GGUF\Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic-NM-DAU-MTP.i1-IQ3_S.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Qwen3.6-27B-Fable-i1-IQ3_S-think" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja ^
  --reasoning on --reasoning-budget 1024 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
