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
rem  Gemma-4-26B-A4B Boulesis v2.1 (SubMaroon, mradermacher i1-IQ4_XS, MoE) — RP, NoThink.
rem  Мерж: QK task-arithmetic + LoRA + прививка головы StyleTune (как у Goetia-26B).
rem  Рабочий режим — NoThink: русский Чисто 100 %, TG 55 t/s, 15.3 ГБ VRAM.
rem  RP-скрин (2 сцены, 3 сида, 2 судьи): gemma 4.48 / Qwen 3.56 (NoThink).
rem  Лучший из измеренных нами 26B-A4B-мёржей и на уровне базовой Gemma-26B-it;
rem  слабые места — «литературщина»/клише, 4 абзаца вместо 2-3, ошибка памяти
rem  («не бросала скрипку»). Вердикт по RP — по согласованию с пользователем.
rem  Спекуляции нет: у Gemma-4-26B-A4B нет MTP-головы (на RP она и не окупается).
rem  Контекст 51200 (измеренный; 65536 при 14.3 ГБ модели уже впритык по VRAM).
rem  Подробности: docs\quality\rp-quality-eval.md §5.16, docs\models.md.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Boulesis-v2.1-26B-A4B-i1-GGUF\Boulesis-v2.1-26B-A4B.i1-IQ4_XS.gguf"
set "TEMPLATE=%LLAMA_DIR%\gemma4.jinja"
"%SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "Boulesis-v2.1-26B-A4B-nothink" ^
  --fit on -fa on --load-mode none -t 14 -tb 14 -b 2048 -ub 512 ^
  -np 1 -c 51200 ^
  -ctk q4_0 -ctv q4_0 ^
  --jinja --chat-template-file "%TEMPLATE%" ^
  --reasoning off --reasoning-budget 0 ^
  --temp 0.6 --min-p 0.1 --top-k 0 --top-p 0.95
pause