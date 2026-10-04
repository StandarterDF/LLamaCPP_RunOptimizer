@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..\..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem ============================================================================
rem  Split-Untied-31B (IQ3_XXS, gemma4 dense) — вариант С мышлением.
rem  По карточке: thinking даёт лучший recall, но может ломаться у некоторых
rem  мержей и ухудшать темп ERP. Если ломается — берите ...-rp-b11382.bat.
rem  Сэмплинг: temp 1.0, min-p 0.03, top-k off, top-p 1.0, DRY 0.8.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\Split-Untied-31B-i1-GGUF\Split-Untied-31B.i1-IQ3_XXS.gguf"
set "DRAFT=%MODELS_DIR%\mradermacher\Gemma-4-Queen-31B-it-uncensored-heretic-i1-GGUF\gemma-4-31B-it-assistant.Q4_K_M.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --host 0.0.0.0 --port 9931 --alias "Split-Untied-31B-think" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.75 ^
  -md "%DRAFT%" ^
  -ctxcp 16 -cms 512 ^
  --jinja --reasoning on --reasoning-budget 1024 ^
  --temp 1.0 --min-p 0.03 --top-k 0 --top-p 1.0 --dry-multiplier 0.8
pause
