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
rem  Gemma-4-26B-A4B — b11382: DFlash + ngram-mod (редактор кода), c=32768
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Gemma-4-26B-A4B-StyleTune-V2-GGUF\Gemma-4-26B-A4B-StyleTune-V2.IQ4_XS.gguf"
set "DRAFT=%PROJECT_DIR%\downloads\speculators\gemma-4-26B-A4B-dflash-Q6_K.gguf"
set "TEMPLATE=%LLAMA_DIR%\gemma4.jinja"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Gemma-4-26B-A4B-code" ^
  --fit on -fa on --load-mode none -t 14 -tb 14 -b 2048 -ub 512 ^
  -np 1 -c 32768 ^
  -ctk q4_0 -ctv q4_0 ^
  --chat-template-file "%TEMPLATE%" ^
  --spec-type draft-dflash,ngram-mod --spec-draft-n-max 6 --spec-draft-ngl all ^
  -md "%DRAFT%" ^
  -ctxcp 16 -cms 512 --reasoning-budget 1024 ^
  --temp 0.6 --min-p 0.1
pause
