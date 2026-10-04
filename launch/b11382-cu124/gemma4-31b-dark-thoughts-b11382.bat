@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..\..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem ------------------------------------------------------------------
rem ============================================================================
rem  Gemma-4-31B Dark-Thoughts V2 (IQ3_XXS) — лучший конфиг на сборке b11382.
rem  Замеры: простой 64 t/s, повтор-код 58, regex-код 45 t/s (VRAM ~15 GB).
rem  Контекст НЕ поднимать выше ~51200 (на 80k скорость падает вдвое).
rem ============================================================================

"%LLAMA_SERVER%" ^
  -m "%MODEL%" ^
  --host 0.0.0.0 --port 9931 --alias "Gemma-4-31B-Dark" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.75 ^
  -md "%DRAFT%" ^
  --jinja --chat-template-kwargs "{\"enable_thinking\":false}" ^
  --temp 0.6 --min-p 0.1
pause
