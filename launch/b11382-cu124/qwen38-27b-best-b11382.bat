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
rem  Qwen3.8-27B (unsloth UD-IQ2_XXS, 8.39 GB) — b11382. Аналог swift-best.
rem  Dense 27B, Qwen3.5-архитектура: 64 слоя, гибрид linear/full attention (1:3),
rem  GQA 24/4, встроенная MTP-голова (mtp_num_hidden_layers=1) -> draft-mtp, без -md.
rem  MTP nm5 pmin0.5, c=81920, KV q4_0. Сэмплинг и --reasoning-preserve — как у Swift;
rem  для «сухого» чата/кода при нужде понизить temp (0.6-0.7).
rem  Vision (mmproj-F16.gguf в той же папке) не включён; при нужде добавить
rem  --mmproj "<MODELS_DIR>\unsloth\Qwen3.8-27B-GGUF\mmproj-F16.gguf" --no-mmproj-offload.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\unsloth\Qwen3.8-27B-GGUF\Qwen3.8-27B-UD-IQ2_XXS.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Qwen3.8-27B" ^
  --parallel 1 -c 81920 ^
  -fa on --fit on --load-mode none ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.5 ^
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 --presence-penalty 0.0 --repeat-penalty 1.0 ^
  --reasoning-preserve
pause
