@echo off
chcp 65001 >nul
rem ============================================================================
rem  run-router.bat — УНИВЕРСАЛЬНЫЙ запускатель llama.cpp в router-режиме.
rem
rem  Один сервер обслуживает ВСЕ модели, что есть на ПК: клиент выбирает модель
rem  по имени (поле "model" в запросе), сервер сам грузит её и выгружает
rem  предыдущую. Отдельный .bat на каждую модель больше не нужен.
rem
rem  Как работает:
rem   1) берёт список моделей и их конфиги из шаблона models-preset.ini;
rem   2) раскрывает пути из config.local.bat и выбрасывает секции, чьих файлов
rem      на этом ПК нет (модели, которых нет, просто не появятся в списке);
rem   3) запускает llama-server с готовым models-preset.local.ini.
rem
rem  Настройки: ROUTER_PORT (по умолчанию 9931). Доп. флаги можно передать
rem  аргументами, напр.: run-router.bat --models-max 2
rem
rem  Пошаговые конфиги отдельных моделей в launch\b11382-cu124\ остаются как есть
rem  (тот же движок, только одна модель). Этот файл их не заменяет, а дополняет.
rem
rem  Профили. Этот же запускатель обслуживает и другие наборы моделей: профиль
rem  задаёт переменные ROUTER_TEMPLATE / ROUTER_PRESET_LOCAL / ROUTER_PORT /
rem  ROUTER_TAG / ROUTER_TITLE и вызывает run-router.bat. Пример — RP-роутер:
rem  launch\router\run-rp-router.bat (порт 9932, только проверенные RP-модели).
rem ============================================================================

rem --- локальные пути (config.local.bat / config.example.bat) ---
for %%I in ("%~dp0..\..") do set "PROJECT_DIR=%%~fI"
call "%PROJECT_DIR%\config.local.bat" 2>nul
call "%PROJECT_DIR%\config.example.bat" 2>nul

rem --- параметры профиля (можно переопределить снаружи, см. run-rp-router.bat) ---
if not defined ROUTER_PORT set "ROUTER_PORT=9931"
if not defined ROUTER_TAG set "ROUTER_TAG=router"
if not defined ROUTER_TITLE set "ROUTER_TITLE=llama-server - router-режим"
if not defined ROUTER_TEMPLATE set "ROUTER_TEMPLATE=%~dp0models-preset.ini"
if not defined ROUTER_PRESET_LOCAL set "ROUTER_PRESET_LOCAL=%~dp0models-preset.local.ini"

rem --- лог запуска: датированный файл под %PROJECT_DIR%\logs\ ---
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmmss"') do set "TS=%%I"
if not defined TS set "TS=run%RANDOM%"
set "LOGDIR=%PROJECT_DIR%\logs"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
set "LOG=%LOGDIR%\%ROUTER_TAG%_%TS%.log"

set "SERVER=%PROJECT_DIR%\downloads\llama-b11382-cu124\llama-server.exe"
set "TEMPLATE=%ROUTER_TEMPLATE%"
set "PRESET=%ROUTER_PRESET_LOCAL%"

if not exist "%SERVER%" (
  echo [ОШИБКА] Не найден llama-server: "%SERVER%"
  echo   Положите сборку b11382 в downloads\llama-b11382-cu124\ или поправьте SERVER в этом .bat.
  pause
  exit /b 1
)
if not exist "%TEMPLATE%" (
  echo [ОШИБКА] Не найден шаблон пресетов: "%TEMPLATE%"
  pause
  exit /b 1
)

rem --- собрать рабочий пресет: раскрыть пути, отсеять модели, которых нет на ПК ---
echo Сборка списка моделей...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_preset.ps1" ^
  -Template "%TEMPLATE%" -Out "%PRESET%" ^
  -ModelsDir "%MODELS_DIR%" -LlamaDir "%LLAMA_DIR%" -ProjectDir "%PROJECT_DIR%"
if errorlevel 1 (
  echo [ОШИБКА] Не удалось собрать пресет.
  pause
  exit /b 1
)

echo.
echo ============================================================
echo  %ROUTER_TITLE%
echo  Адрес:  http://0.0.0.0:%ROUTER_PORT%   (web UI и OpenAI API)
echo  Выбор:  поле "model" в запросе = одно из имён выше
echo  Лог:    "%LOG%"
echo  Живёт одна модель за раз (--models-max 1); переключение — по имени.
echo ============================================================
echo.

rem stdout дочерних моделей проходит через фильтр (убирает пустые [pid]-строки
rem прогресса загрузки); stderr роутера идёт в консоль напрямую и пишется в %LOG%.
"%SERVER%" ^
  --models-preset "%PRESET%" ^
  --models-max 1 ^
  --host 0.0.0.0 --port %ROUTER_PORT% ^
  --log-file "%LOG%" ^
  %* ^
  | powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0trim_log.ps1"
pause
