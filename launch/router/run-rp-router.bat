@echo off
chcp 65001 >nul
rem ============================================================================
rem  run-rp-router.bat — RP-роутер: только проверенные RP-модели.
rem
rem  Тонкая обёртка над run-router.bat: переключает профиль на models-preset-rp.ini,
rem  свой порт (9932) и свой лог, чтобы не конфликтовать с общим роутером.
rem
rem  Состав (ядро — Gemma-4-31B-мержи + быстрые MoE StyleTune/Goetia), обоснование
rem  и режимы — в launch\router\models-preset-rp.ini и docs\research\router-mode.md.
rem  Клиент выбирает модель по имени (поле "model"), как в общем роутере.
rem ============================================================================

set "ROUTER_TEMPLATE=%~dp0models-preset-rp.ini"
set "ROUTER_PRESET_LOCAL=%~dp0models-preset-rp.local.ini"
if not defined ROUTER_PORT set "ROUTER_PORT=9932"
set "ROUTER_TAG=rp-router"
set "ROUTER_TITLE=llama-server - RP-роутер (проверенные RP-модели)"

call "%~dp0run-router.bat" %*
