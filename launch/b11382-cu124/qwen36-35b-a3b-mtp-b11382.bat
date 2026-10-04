@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..\..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem ============================================================================
rem  Qwen3.6-35B-A3B (Q2_K_XL) — b11382: MTP nm5 pmin0.5, c=131072, vision на CPU
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\unsloth\Qwen3.6-35B-A3B-MTP-GGUF\Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf"
set "MMPROJ=%MODELS_DIR%\unsloth\Qwen3.6-35B-A3B-MTP-GGUF\mmproj-F16.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --host 0.0.0.0 --port 9931 --alias "Qwen3.6-35B-A3B" ^
  -np 1 -c 131072 ^
  -fa on --fit on --load-mode none -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.5 ^
  --mmproj "%MMPROJ%" --no-mmproj-offload --image-min-tokens 1024 ^
  --reasoning-budget 8192 ^
  --jinja --temp 0.6
pause
