# bench — инструменты замеров и проверок

Скрипты запускаются интерпретатором из локального `.venv` (пакеты — только туда):
`.venv\Scripts\python.exe bench\<скрипт>.py`. Личные пути — в `env.local.json` по образцу
[env.example.json](env.example.json) (в git не попадает); результаты — в `bench\`, `logs\` и `docs\`.

## Замеры скорости

| Файл | О чём |
| --- | --- |
| [bench.py](bench.py) | Харнесс llama-server: гоняет серии из [suites](suites/README.md), пишет результаты в [runs](runs/README.md). |
| [requests_real.json](requests_real.json) | Реалистичные промпты (RP/чат/код/математика/суммаризация) — TG/PP меряем только на них. |
| [report.py](report.py) | Сводка результатов bench.py в markdown (`bench/runs/summary.md`). |
| [env.example.json](env.example.json) | Образец `env.local.json`: пути и адрес сервера для сценариев bench. |

## Память и VRAM

| Файл | О чём |
| --- | --- |
| [vram_model.py](vram_model.py) | Эмпирическая модель памяти llama.cpp: сколько контекста влезает в 16 ГБ (формулы — [docs\research\context-memory-model.md](../docs/research/context-memory-model.md)). |
| [gguf_info.py](gguf_info.py) | Читалка метаданных GGUF (чистый stdlib) + расчёт размера KV-кэша. |

## KV-кэш

| Файл | О чём |
| --- | --- |
| [kv_quality.py](kv_quality.py) | Харнесс NIAH + PPL по типам KV (f16/q8_0/q4_0). |
| [kv_prompts.py](kv_prompts.py) | Промптовое сравнение KV: одни и те же промпты через f16/q8_0/q4_0. |
| [kv_prompt_checks.py](kv_prompt_checks.py) | Объективная проверка: сработали ли ожидаемые критерии сравнения. |
| [kv_canary.py](kv_canary.py) | Функциональная канарейка: tool/JSON-вызовы и pass@1 кода. |
| [kv_code_seeds.py](kv_code_seeds.py) | Не участились ли срывы в коде под квантованным KV (несколько сэмплов). |
| [kv_pipeline.py](kv_pipeline.py) | Оркестратор KV-серии: ждёт освобождения GPU и прогоняет всё подряд. |
| [plot_kv.py](plot_kv.py) | Графики KV (вычисленные и измеренные) → [docs\images](../docs/images/README.md). |

## Качество RP

- [quality/](quality/README.md) — харнесс, судьи и прогоны; методика — [docs\quality\rp-quality-eval.md](../docs/quality/rp-quality-eval.md).

## Утилиты

| Файл | О чём |
| --- | --- |
| [logstats.py](logstats.py) | Сводка по логам llama-server (папка `logs\` или файл/маска). |
| [check_bats.py](check_bats.py) | Проверка `.bat`-конфигов: раскрывает переменные путей и проверяет, что файлы существуют. |
| [check_links.py](check_links.py) | Проверка ссылок на файлы проекта в `.md`/`.bat`. |
| [sanitize.py](sanitize.py) | Заменяет личные пути плейсхолдерами перед публикацией. |
| [make_charts.py](make_charts.py) | Графики RP-рейтинга, спекуляции и кэша промпта → [docs\images](../docs/images/README.md). |
| [usecase_cache.py](usecase_cache.py) | Многоходовый кейс: сколько токенов реально переиспользует кэш префикса. |
| [fetch_hf_meta.py](fetch_hf_meta.py) | Метаданные моделей с Hugging Face (для реестров и карточек). |
| [caliper_classify.py](caliper_classify.py), [parse_caliper.py](parse_caliper.py) | Разбор выгрузки CaliperBench ([docs\research\caliperbench-2026-10.md](../docs/research/caliperbench-2026-10.md)). |

## Папки

| Папка | О чём |
| --- | --- |
| [help](help/README.md) | Снимок `llama-server --help` (сборка b11382). |
| [quality](quality/README.md) | Оценка качества RP: харнесс, судьи, прогоны. |
| [runs](runs/README.md) | Результаты скоростных серий (`results.jsonl`, `summary.md`, логи). |
| [suites](suites/README.md) | Наборы тестов для bench.py по темам (real, spec, tune, kv, …). |
| [skill-selftest](skill-selftest/README.md) | Самопроверка скила llm-launch-tuner. |

Не публикуются (в `.gitignore`): `translate/`, `final/` — личный датасет-пайплайн; `logs\` — логи
запусков `.bat`.
