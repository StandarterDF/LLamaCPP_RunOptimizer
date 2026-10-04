@echo off
chcp 65001 >nul
rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul
rem ============================================================================
rem  Gemma-4-26B-A4B StyleTune (IQ4_XS) — старая сборка, БЕЗ мышления (--reasoning off)
rem ============================================================================
set "SERVER=%LLAMA_SERVER%"
set "MODEL=%MODELS_DIR%\mradermacher\Gemma-4-26B-A4B-StyleTune-V2-GGUF\Gemma-4-26B-A4B-StyleTune-V2.IQ4_XS.gguf"
set "DRAFT=%MODELS_DIR%\mradermacher\Gemma-4-26B-A4B-StyleTune-V2-GGUF\gemma-4-26B-A4B-it-assistant.Q4_K_S.gguf"
set "TEMPLATE=%LLAMA_DIR%\gemma4.jinja"
"%SERVER%" ^
  -m "%MODEL%" ^
  --host 0.0.0.0 --port 9931 --alias "Gemma-4-26B-A4B-nothink" ^
  --fit on -fa on --load-mode none -t 14 -tb 14 -b 2048 -ub 512 ^
  -np 1 -c 65536 ^
  -ctk q4_0 -ctv q4_0 ^
  --chat-template-file "%TEMPLATE%" ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.5 ^
  -md "%DRAFT%" ^
  --reasoning off ^
  --temp 0.6 --min-p 0.1
pause
