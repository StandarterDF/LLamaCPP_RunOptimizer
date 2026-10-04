@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..\..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem ------------------------------------------------------------------
rem ============================================================================
rem  Gemma-4-26B-A4B StyleTune V2 (IQ4_XS, MoE) — лучший конфиг на сборке b11382.
rem  Замеры: простой ~138 t/s, повтор-код ~125, regex-код ~84 (VRAM ~15.1-15.6 GB).
rem  MoE-эксперты НЕ выгружать на CPU (-ncmoe даёт -32...-43%).
rem  Для длинного контекста заменить -c 65536 на 131072 (около 110 t/s на повтор-коде).
rem ============================================================================

"%LLAMA_SERVER%" ^
  -m "%MODEL%" ^
  --host 0.0.0.0 --port 9931 --alias "Gemma-4-26B-A4B" ^
  --fit on -fa on --load-mode none -t 14 -tb 14 -b 2048 -ub 512 ^
  -np 1 -c 65536 ^
  -ctk q4_0 -ctv q4_0 ^
  --chat-template-file "%TEMPLATE%" ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.5 ^
  -md "%DRAFT%" ^
  -ctxcp 16 -cms 512 --reasoning-budget 1024 ^
  --temp 0.6 --min-p 0.1
pause
