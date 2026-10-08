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
rem  Gemma-4-26B-A4B Kitchoon (SubMaroon; mradermacher i1-IQ4_XS, MoE) — RP, NoThink.
rem  Линия происхождения: gemma-4-26B-A4B-it -> Gryphe/Pantheon-Reasoning-26B-A4B-1.1
rem  -> Vortex5/...-heretic -> SubMaroon/Kitchoon-26B-A4B. Модель с vision (mmproj в
rem  static-репе), здесь текстовый RP-запуск. Рабочий режим — NoThink.
rem  РЕЗУЛЬТАТЫ (RP-скрин, 2 сцены, 3 сида, панель 4 судей): панель 2.72 (NoThink 3.25 / Think 2.09);
rem  локально gemma 3.88 / Qwen 3.17 (NoThink). Чисто 83 %, TG 55 t/s, 15.8 ГБ VRAM.
rem  ❌ НЕ апгрейд — слабейший из измеренных 26B-мёржей (ниже Goetia 3.55, DTV2 3.51, GLM-Flash 3.28):
rem  провал памяти (2.25 — 3/3 сида приняли ложную «Питер» вместо Твери), характер смягчён,
rem  шаблоны («Винил — это аргумент»), BPE-склейка «дождrains». Для RP не берём.
rem  Спекуляции нет: у Gemma-4-26B-A4B нет MTP-головы. Контекст 51200 (при 14.3 ГБ впритык).
rem  Подробности: docs\quality\rp-quality-eval.md §5.17, docs\models.md.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Kitchoon-26B-A4B-i1-GGUF\Kitchoon-26B-A4B.i1-IQ4_XS.gguf"
set "TEMPLATE=%LLAMA_DIR%\gemma4.jinja"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Kitchoon-26B-A4B-nothink" ^
  --fit on -fa on --load-mode none -t 14 -tb 14 -b 2048 -ub 512 ^
  -np 1 -c 51200 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja --chat-template-file "%TEMPLATE%" ^
  --reasoning off --reasoning-budget 0 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause
