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
rem  Gemma-4-26B-A4B-it (base instruct, UD-IQ3_XXS) — RP, С мышлением.
rem  ОГРАНИЧЕНИЕ: размышления уходят в канал <|channel> (англ.); видимый ответ — нормальный русский,
rem  но строгий судья читал raw_full и счёл ответы «невалидными» (утёкший reasoning).
rem  Рабочий режим для этой модели — nothink (см. gemma4-26a4b-base-rp-nothink-b11382.bat).
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\unsloth\gemma-4-26B-A4B-it-GGUF\gemma-4-26B-A4B-it-UD-IQ3_XXS.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Gemma-4-26B-A4B-base-rp-think" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja --chat-template-file "%LLAMA_DIR%\gemma4.jinja" ^
  --reasoning on --reasoning-effort low --reasoning-budget 1024 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
