@echo off
chcp 65001 >nul
rem ============================================================================
rem  Шаблон запуска llama-server (Windows). Замените пути и параметры.
rem  Обоснование конфига должно лежать в LAUNCH.md/FINDINGS.md рядом с этим файлом.
rem  Лог каждого старта: logs\<имя-скрипта>_<дата_время>.log (--log-file ниже).
rem ============================================================================
rem --- launch log: dated file under logs\ next to this script ---
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmmss"') do set "TS=%%I"
if not defined TS set "TS=run%RANDOM%"
set "LOGDIR=%~dp0logs"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
set "LOG=%LOGDIR%\%~n0_%TS%.log"
echo Log: %LOG%
set "LLAMA_SERVER=C:\llama.cpp\llama-server.exe"
set "MODEL=D:\models\REPLACE-ME.gguf"

"%LLAMA_SERVER%" ^
  -m "%MODEL%" ^
  --log-file "%LOG%" ^
  --host 0.0.0.0 --port 9931 --alias "MODEL-ALIAS" ^
  --parallel 1 -c 81920 ^
  -fa on --fit on --no-mmap ^
  -ctk q4_0 -ctv q4_0 ^
  --spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.5 ^
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 --presence-penalty 0.0 --repeat-penalty 1.0 ^
  --reasoning-preserve
pause
