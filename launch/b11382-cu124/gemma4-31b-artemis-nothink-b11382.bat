@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..\..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem ============================================================================
rem  Artemis-31B-v1.2 (bartowski IQ3_XXS, dense gemma4) — RP, NoThink, русский.
rem  Русский тест (наш набор): 92-96% ответов без англ. вставок/склеек, ~20-22 t/s.
rem  Карточка (temp1.0) и temp0.7+DRY дают 96%; temp0.4 - 92% (чуть хуже).
rem  Контекст 32k: 31B dense IQ3_XXS на 16 ГБ садится почти впритык (~16.0 ГБ
rem  с MTP-драфтом), поэтому больше 32k не ставим без выгрузки слоёв.
rem  Спекуляция: общий Gemma-4-31B MTP-assistant (nmax5 pmin0.75).
rem  Подробности и оговорки: docs\sampling-quality.md.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\bartowski\TheDrummer_Artemis-31B-v1.2-GGUF\TheDrummer_Artemis-31B-v1.2-IQ3_XXS.gguf"
set "DRAFT=%MODELS_DIR%\mradermacher\Gemma-4-Queen-31B-it-uncensored-heretic-i1-GGUF\gemma-4-31B-it-assistant.Q4_K_M.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --host 0.0.0.0 --port 9931 --alias "Artemis-31B-v1.2-nothink" ^
  -np 1 -c 32768 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.75 ^
  -md "%DRAFT%" ^
  --jinja --reasoning off --reasoning-budget 0 ^
  --temp 0.7 --min-p 0.05 --top-k 0 --top-p 1.0 --dry-multiplier 0.8 --dry-base 1.75 --dry-allowed-length 2 --dry-penalty-last-n 256
pause
