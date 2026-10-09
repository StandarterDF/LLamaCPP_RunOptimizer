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
rem  Qwen3.6-27B Fable-Fusion-711 (mradermacher i1-IQ3_S, imatrix, 11.7 ГиБ) - RP, БЕЗ мышления.
rem  БЕЗ спекуляции (на RP MTP вредит). c=51200, KV q4_0, RU-safe сэмплинг.
rem  Панель 4 судей: No 3.47 · Think 3.79 (лучше IQ2_M: 3.46/3.45; прирост в think).
rem  Русский 100 %, 18 t/s. Контекст при KV q4_0 - до ~125k (см. bench\vram_model.py).
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic-NM-DAU-MTP-i1-GGUF\Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic-NM-DAU-MTP.i1-IQ3_S.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Qwen3.6-27B-Fable-i1-IQ3_S-nothink" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja ^
  --reasoning off --reasoning-budget 0 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
