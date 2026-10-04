@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..\..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem ------------------------------------------------------------------
rem ============================================================================
rem  Gemma-4-26B-A4B StyleTune V2 — ПРОФИЛЬ «РЕДАКТОР КОДА» (DFlash + ngram-mod).
rem  Замеры (c=32768, сборка b11382): повтор-код 128.5 t/s (=уровень MTP),
rem  код 98.1 (+17% к MTP), простой промпт 76.7 (-44%). Принятие 18/49/32%.
rem  Включать под задачи с копированием кода; для обычного чата —
rem  gemma4-26a4b-styletune-b11382.bat (MTP).
rem ============================================================================

"%LLAMA_SERVER%" ^
  -m "%MODEL%" ^
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
