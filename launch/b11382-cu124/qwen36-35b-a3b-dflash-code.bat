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
rem  Qwen3.6-35B-A3B — b11382: DFlash + ngram-mod (редактор кода), c=131072
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\unsloth\Qwen3.6-35B-A3B-MTP-GGUF\Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf"
set "DRAFT=%LLAMA_DIR%\qwen36-35b-a3b-dflash-Q6_K.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Qwen3.6-35B-A3B-code" ^
  -np 1 -c 131072 ^
  -fa on --fit on --load-mode none -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-dflash,ngram-mod --spec-draft-n-max 6 --spec-draft-ngl all ^
  -md "%DRAFT%" ^
  --reasoning-budget 8192 ^
  --jinja --temp 0.6
pause
