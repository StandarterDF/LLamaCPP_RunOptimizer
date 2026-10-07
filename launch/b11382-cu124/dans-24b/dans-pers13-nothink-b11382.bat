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
rem  Dans-PersonalityEngine-V1.3.0-24b (PocketDoc, bartowski IQ4_XS, dense) —
rem  база Mistral-Small-3.1. НЕ reasoner и НЕ character-RP-модель: это
rem  «personality/chat»-файнтюн (50+ датасетов), на наших RP-сценах слаб
rem  (Qwen-судья 2.54 — ниже базовых; персонаж 1.5, «быстрое согласие»).
rem  Зато РУССКИЙ держит чисто (Чисто 100 %, Cyr 100 %), хотя в карточке ru нет,
rem  и хорошо идёт как чат-компаньон. MTP-головы нет — спекуляция не включена.
rem  TG ~18.9 t/s (dense 24B). Подробности: docs\quality\rp-quality-eval.md §5.14.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\bartowski\PocketDoc_Dans-PersonalityEngine-V1.3.0-24b-GGUF\PocketDoc_Dans-PersonalityEngine-V1.3.0-24b-IQ4_XS.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Dans-Pers-24B" ^
  --fit on -fa on --load-mode none -t 14 -tb 14 -b 2048 -ub 512 ^
  -np 1 -c 32768 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja ^
  --reasoning off --reasoning-budget 0 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
