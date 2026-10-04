@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem ------------------------------------------------------------------
rem ============================================================================
rem  swift-long-131k.bat — профиль длинного контекста (131 072 токена).
rem  На 131k большие MTP-драфты замедляются: используем n-max 3, p-min 0.7.
rem  VRAM ~14.1 ГБ: закрыть лишние GPU-приложения.
rem ============================================================================

"%LLAMA_SERVER%" ^
  -m "%MODEL%" ^
  --host 0.0.0.0 --port 9931 --alias "Swift-1.5-27B-131k" ^
  --parallel 1 -c 131072 ^
  -fa on --fit on --no-mmap ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 3 --spec-draft-n-min 1 --spec-draft-p-min 0.7 ^
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 --presence-penalty 0.0 --repeat-penalty 1.0 ^
  --reasoning-preserve
pause
