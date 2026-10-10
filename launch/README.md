# launch — конфиги запуска моделей

Один `.bat` = один рабочий конфиг `llama-server.exe`: выбранные бенчмарками контекст, KV-кэш,
спекуляция и сэмплинг. Логи каждого запуска пишутся в `logs\` (папка не публикуется; сводка —
[bench\logstats.py](../bench/logstats.py)).

## Содержимое

| Папка | О чём |
| --- | --- |
| [b11382-cu124](b11382-cu124) | Основная сборка llama.cpp **b11382 (CUDA 12.4)** — все актуальные конфиги, разложены по семействам моделей. |
| [router](router) | Router-режим: один сервер обслуживает все модели по `models-preset*.ini`. |

## Как запустить

1. Скопируйте [config.example.bat](../config.example.bat) → `config.local.bat` и укажите свои пути:
   `LLAMA_SERVER` (полный путь к llama-server.exe) и `MODELS_DIR` (папка с GGUF).
2. Запустите нужный `.bat`.
3. Готово, когда в консоли появилось `listening on http://...` — это OpenAI-совместимый API.

Внутри конфигов — только переменные (`%PROJECT_DIR%`, `%LLAMA_SERVER%`, `%MODELS_DIR%`, `%LLAMA_DIR%`);
личных путей в репозитории нет.

## См. также

- [README.md](../README.md) — какую модель выбрать под задачу.
- [docs\models.md](../docs/models.md) — реестр моделей и итоговые конфиги.
- [docs\research\router-mode.md](../docs/research/router-mode.md) — router-режим.
- [AGENTS.md](../AGENTS.md) — правила репозитория (CRLF в `.bat`, роутер, санитайз перед коммитом).
