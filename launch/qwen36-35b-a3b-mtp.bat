@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem ------------------------------------------------------------------
rem ============================================================================
rem  Qwen3.6-35B-A3B MTP (UD-Q2_K_XL, MoE) — лучший конфиг по итогам замеров
rem  (MODELS_TUNING.md, серия c):
rem    реальный чат ~105 t/s (+16% к исходному конфигу с nmax2/163k);
rem    VRAM ~14.2 GB, PP ~1844 t/s.
rem  Контекст 131072 быстрее 163840 и оставляет запас VRAM.
rem  Vision включён: --no-mmproj-offload выносит проектор на CPU; в серии c
rem  это не влияло на скорость. Точная комбинация (131k + vision) напрямую
rem  не замерялась: для чистого текста строки mmproj можно удалить.
rem ============================================================================

"%LLAMA_SERVER%" ^
  -m "%MODEL%" ^
  --host 0.0.0.0 --port 9931 --alias "Qwen3.6-35B-A3B" ^
  -np 1 -c 131072 ^
  -fa on --fit on --no-mmap -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.5 ^
  --mmproj "%MMPROJ%" --no-mmproj-offload --image-min-tokens 1024 ^
  --reasoning-budget 8192 ^
  --jinja --temp 0.6
pause
