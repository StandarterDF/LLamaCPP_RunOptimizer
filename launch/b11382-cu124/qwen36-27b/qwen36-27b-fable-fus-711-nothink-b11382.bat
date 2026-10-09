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
rem  Qwen3.6-27B Fable-Fusion-711 (DavidAU, NEO-MAX MTP, IQ2_M, 11.3 GB, dense) - RP, БЕЗ мышления.
rem  c=51200, KV q4_0, RU-safe сэмплинг, БЕЗ спекуляции (оптимум для RP).
rem  ЗАМЕР (requests_real.json): на RP MTP ЗАМЕДЛЯЕТ - 13.5 t/s с MTP (принятие 68-85 %)
rem  против 17.8 без спекуляции; nmax8 хуже (10-14). MTP даёт +6-13 % только на коде/
rem  математике - для них отдельный ...-mtp-b11382.bat. Качество от спекуляции не зависит.
rem  RP-скрин (панель 4 судей): русский 100 %, память 3.9; слабые оси - персонаж 2.96,
rem  инициатива 3.0 (пассивна), повторы 2.7. Панель Non-Think 3.46. Think дублирует ответ.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\DavidAU\Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic-NM-DAU-NEO-MAX-MTP-GGUF\Qwen3.6-27B-Fable-Fus-711-UnHeretic-NM-DAU-NEO-MAX-NEO-MTP-IQ2_M.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Qwen3.6-27B-Fable-Fus-711-nothink" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja ^
  --reasoning off --reasoning-budget 0 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
