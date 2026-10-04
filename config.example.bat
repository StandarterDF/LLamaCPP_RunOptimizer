@echo off
rem ============================================================================
rem  config.example.bat — пример локального конфига путей.
rem  Скопируйте этот файл в config.local.bat и укажите свои пути.
rem  config.local.bat НЕ попадает в git (см. .gitignore).
rem
rem  Переменные:
rem    LLAMA_SERVER — полный путь к llama-server.exe (основная сборка)
rem    MODELS_DIR   — папка, где лежат модели (GGUF)
rem    LLAMA_DIR    — папка сборки llama.cpp (шаблоны gemma4.jinja, draft-файлы);
rem                   по умолчанию — папка из LLAMA_SERVER
rem ============================================================================
if not defined LLAMA_SERVER set "LLAMA_SERVER=C:\llama.cpp\llama-server.exe"
if not defined MODELS_DIR set "MODELS_DIR=D:\models"
if not defined LLAMA_DIR for %%I in ("%LLAMA_SERVER%") do set "LLAMA_DIR=%%~dpI"
if defined LLAMA_DIR if "%LLAMA_DIR:~-1%"=="\" set "LLAMA_DIR=%LLAMA_DIR:~0,-1%"
