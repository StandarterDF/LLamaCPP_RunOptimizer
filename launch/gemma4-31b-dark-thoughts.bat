@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem ============================================================================
rem  Gemma-4-31B Dark-Thoughts (IQ3_XXS) — MTP-assistant nm5 pmin0.75, c=51200, без thinking
rem ============================================================================
set "SERVER=%LLAMA_SERVER%"
set "MODEL=%MODELS_DIR%\mradermacher\Gemma-4-Dark-Thoughts-V2-31B-i1-GGUF\Gemma-4-Dark-Thoughts-V2-31B.i1-IQ3_XXS.gguf"
set "DRAFT=%MODELS_DIR%\mradermacher\Gemma-4-Queen-31B-it-uncensored-heretic-i1-GGUF\gemma-4-31B-it-assistant.Q4_K_M.gguf"
"%SERVER%" ^
  -m "%MODEL%" ^
  --host 0.0.0.0 --port 9931 --alias "Gemma-4-31B-Dark" ^
  -np 1 -c 51200 ^
  -fa on --fit on --load-mode none ^
  -t 12 -tb 12 ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.75 ^
  -md "%DRAFT%" ^
  --jinja --reasoning off ^
  --temp 0.6 --min-p 0.1
pause
