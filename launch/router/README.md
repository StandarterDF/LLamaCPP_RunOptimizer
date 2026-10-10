# router — один сервер на все модели

Router-режим llama.cpp: `llama-server` держит несколько моделей и переключает их по запросу
(поле `model` в OpenAI-совместимом API). Полное описание — [docs\research\router-mode.md](../../docs/research/router-mode.md).

## Файлы

| Файл | О чём |
| --- | --- |
| `models-preset.ini` | Пресет всех моделей (id → путь, флаги запуска). Генерируется скриптом. |
| `models-preset-rp.ini` | Отдельный пресет для RP-моделей. |
| `build_preset.ps1` | Пересборка `models-preset.ini` из конфигов `launch\...`. |
| `run-router.bat` | Запуск роутера с общим пресетом. |
| `run-rp-router.bat` | Запуск роутера с RP-пресетом. |
| `trim_log.ps1` | Обрезка/чистка логов роутера. |
| `*.local.ini` | Личные локальные переопределения — в git не попадают. |

## Правило

Добавили новую модель или конфиг — сразу добавьте секцию в `models-preset.ini` (и при желании
в `models-preset-rp.ini`), пересоберите пресет (`build_preset.ps1`) и обновите таблицу id
в [docs\research\router-mode.md](../../docs/research/router-mode.md).

## См. также

- [launch\README.md](../README.md) — запуск одиночных конфигов.
- [AGENTS.md](../../AGENTS.md) — правило «новая модель → роутер».
