@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..\..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem ------------------------------------------------------------------
rem ============================================================================
rem  Swift-1.5-Qwen3.8-27B (IQ2_S-mtp) — лучший конфиг на НОВОЙ сборке b11382.
rem  Замеры (реальный чат, 3 задачи): 41.6 t/s (на старой сборке 10472 — 37.7).
rem  Простые продолжения: 68.5 t/s. VRAM ~12.9 GB. Контекст 81920.
rem  В b11382 флаг --no-mmap удалён — используется --load-mode none.
rem ============================================================================

"%LLAMA_SERVER%" ^
  -m "%MODEL%" ^
  --host 0.0.0.0 --port 9931 --alias "Swift-1.5-27B" ^
  --parallel 1 -c 81920 ^
  -fa on --fit on --load-mode none ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.5 ^
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 --presence-penalty 0.0 --repeat-penalty 1.0 ^
  --reasoning-preserve
pause
