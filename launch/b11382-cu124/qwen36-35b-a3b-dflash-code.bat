@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..\..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem ------------------------------------------------------------------
rem ============================================================================
rem  Qwen3.6-35B-A3B — ПРОФИЛЬ «РЕДАКТОР КОДА» (DFlash + ngram-mod), сборка b11382.
rem  Замеры (c=131072): повтор-код 185.8 t/s (+27% к MTP), код 131.7 (+30%),
rem  простой промпт 135.5 (-8% к MTP). Принятие 47/72/46%.
rem  Драфт qwen36-35b-a3b-dflash-Q6_K.gguf лежит в папке существующего билда llama.cpp.
rem  Использовать, когда работа в основном — правки/рефакторинг кода с копированием.
rem  Для обычного чата лучше qwen36-35b-a3b-mtp-b11382.bat (MTP).
rem ============================================================================

"%LLAMA_SERVER%" ^
  -m "%MODEL%" ^
  --host 0.0.0.0 --port 9931 --alias "Qwen3.6-35B-A3B-code" ^
  -np 1 -c 131072 ^
  -fa on --fit on --load-mode none -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-dflash,ngram-mod --spec-draft-n-max 6 --spec-draft-ngl all ^
  -md "%DRAFT%" ^
  --reasoning-budget 8192 ^
  --jinja --temp 0.6
pause
