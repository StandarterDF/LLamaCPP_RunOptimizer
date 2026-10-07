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
rem  Gemma-4-26B-A4B G4-MeroMero it-uncensored-heretic (llmfan46, mradermacher
rem  i1-IQ4_XS, MoE) — RP, Thinking. Аналог ...-nothink-..., но с мышлением.
rem  ВНИМАНИЕ: на нашем стенде think в llama.cpp НЕПРИГОДЕН — модель не закрывает
rem  канал, наружу течёт англ. reasoning/черновики, ответы обрываются (Чисто 17 %,
rem  junk ~81/1k, EN-стоп ~70). Рабочий режим — nothink (см. ...-nothink-...).
rem  Конфиг оставлен для полноты и проверки в других сборках. Подробности:
rem  docs\quality\rp-quality-eval.md §5.13.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\G4-MeroMero-26B-A4B-it-uncensored-heretic-i1-GGUF\G4-MeroMero-26B-A4B-it-uncensored-heretic.i1-IQ4_XS.gguf"
set "TEMPLATE=%LLAMA_DIR%\gemma4.jinja"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "MeroMero-26B-A4B-think" ^
  --fit on -fa on --load-mode none -t 14 -tb 14 -b 2048 -ub 512 ^
  -np 1 -c 65536 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja --chat-template-file "%TEMPLATE%" ^
  --reasoning on --reasoning-effort low --reasoning-budget 1024 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
