@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..\..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem ============================================================================
rem  G4-MeroMero-v2-31B-heretic (IQ3_XXS, gemma4 dense) — RP, NoThink (--reasoning off).
rem  Сэмплинг по карточке zerofata/G4-MeroMero-v2-31B (heretic — её abliteration):
rem  temp 0.8-1.0, min-p 0.05.
rem  Спекуляция: общий Gemma-4-31B MTP-assistant (nmax5 pmin0.75), c=51200, KV q4_0.
rem ============================================================================
set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "MODEL=%MODELS_DIR%\mradermacher\G4-MeroMero-v2-31B-heretic-i1-GGUF\G4-MeroMero-v2-31B-heretic.i1-IQ3_XXS.gguf"
set "DRAFT=%MODELS_DIR%\mradermacher\Gemma-4-Queen-31B-it-uncensored-heretic-i1-GGUF\gemma-4-31B-it-assistant.Q4_K_M.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --host 0.0.0.0 --port 9931 --alias "MeroMero-v2-31B-heretic-nothink" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.75 ^
  -md "%DRAFT%" ^
  -ctxcp 16 -cms 512 ^
  --jinja --reasoning off ^
  --temp 0.9 --min-p 0.05
pause
