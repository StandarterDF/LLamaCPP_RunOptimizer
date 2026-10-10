# Документация GGUFLauncher

Индекс: что где лежит. Начните с реестров, дальше — по группам.

## Корень [docs](.)

| Файл | О чём |
| --- | --- |
| [docs\researched.md](researched.md) | **Реестр проверенного** — что уже измерялось и с каким вердиктом (не повторять). |
| [docs\models.md](models.md) | **Реестр моделей** — протестированные (баллы, скорости) и кандидаты на будущее. |

## Модели — [docs\models](models)

| Файл | О чём |
| --- | --- |
| [docs\models\gemma-4-26b-a4b.md](models/gemma-4-26b-a4b.md) | Gemma-4-26B-A4B: скорость, спекуляция, RP-скрин. |
| [docs\models\gemma-4-31b.md](models/gemma-4-31b.md) | Gemma-4-31B (Dark Thoughts и др.): серии замеров, конфиги. |
| [docs\models\gemma-4-31b-rp-merges.md](models/gemma-4-31b-rp-merges.md) | RP-мержи Gemma-4-31B (Split-Untied; MeroMero удалён). |
| [docs\models\qwen36-35b-a3b.md](models/qwen36-35b-a3b.md) | Qwen3.6-35B-A3B: скорость, DFlash/ngram, RP-скрин. |
| [docs\models\swift-1.5-27b.md](models/swift-1.5-27b.md) | Swift-1.5-Qwen3.8-27B: все серии замеров. |
| [docs\models\swift-1.5-27b-launch.md](models/swift-1.5-27b-launch.md) | Swift-1.5: практическая инструкция и итоговый конфиг. |

## Качество RP — [docs\quality](quality)

| Файл | О чём |
| --- | --- |
| [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) | Методика и результаты оценки RP LLM-судьёй («мнимая история»); штатная панель — **4 судьи** (2 локальных + 2 облачных DeepSeek). |
| [docs\quality\rp-ranking.md](quality/rp-ranking.md) | **Витрина выбора** RP-модели: 2 таблицы (Think/NoThink), среднее по 4 судьям, колонка Type (Local/Cloud). |
| [docs\quality\sampling-quality.md](quality/sampling-quality.md) | Сэмплинг и качество русского текста (температура, top-k, min-p, грамматика). |
| [docs\quality\base-models-rp-eval.md](quality/base-models-rp-eval.md) | Базовые instruct-модели на RP (Gemma-4-26B-it, Qwen3.6, Qwen3.8). |
| [docs\quality\cloud-api-rp-eval.md](quality/cloud-api-rp-eval.md) | Облачные API-модели (DeepSeek, GLM) на RP: 12 моделей × 4 судьи. |
| [docs\quality\en-rp-eval.md](quality/en-rp-eval.md) | Английский RP-скрин: EN vs RU на тех же моделях, 4 судьи; в EN работает think, 0 кириллицы. |

## Внешний ресёрч и кросс-темы — [docs\research](research)

| Файл | О чём |
| --- | --- |
| [docs\research\speculation-research.md](research/speculation-research.md) | Методы спекуляции, внешние спекуляторы, сравнение сборок. |
| [docs\research\context-infinite-chat.md](research/context-infinite-chat.md) | Длинные сессии, «бесконечный» контекст, SillyTavern. |
| [docs\research\rp-model-candidates.md](research/rp-model-candidates.md) | Внешние RP-кандидаты Gemma 4 и русский (сообщество, HF). |
| [docs\research\caliperbench-2026-10.md](research/caliperbench-2026-10.md) | CaliperBench: RP-рейтинг Gemma 4, правило «что держит русский». |
| [docs\research\why-ru-models.md](research/why-ru-models.md) | Почему одни модели держат русский, а другие рассыпаются (PPL, провенанс). |
| [docs\research\euroeval-2026-10.md](research/euroeval-2026-10.md) | EuroEval: славянские прокси-языки для оценки русского. |
| [docs\research\kv-cache-quantization.md](research/kv-cache-quantization.md) | **Квантование KV-кэша** (f16/q8_0/q4_0): промптовые сравнения, NIAH, PPL, бюджет VRAM; картинки — [docs\images](images). |
| [docs\research\kv-cache-external.md](research/kv-cache-external.md) | **Внешние данные про влияние KV-кэша**: tool/JSON, код, KL-дивергенция (Gemma vs Qwen), attention sinks, многотирн. |
| [docs\research\context-memory-model.md](research/context-memory-model.md) | **Память контекста**: эмпирическая формула VRAM→макс. ctx, KV по архитектурам, инструмент [bench\vram_model.py](../bench/vram_model.py). |
| [docs\research\router-mode.md](research/router-mode.md) | Router-режим llama.cpp: один сервер на все модели ([launch\router](../launch/router)). |
| [docs\research\rp-datasets-en-ru.md](research/rp-datasets-en-ru.md) | Датасеты RP/DRP/ERP (EN и RU): пул для SFT и перевода EN→RU, пайплайн MT. |
| [docs\research\rp-datasets-quality-check.md](research/rp-datasets-quality-check.md) | Проверка тех же датасетов **по факту** (реальные строки HF): дубли, формат, качество, вердикты. |
| [docs\research\gemma4-rp-training-data.md](research/gemma4-rp-training-data.md) | На чём обучались наши Gemma-4 RP-мержи/файнтюны и современные Gemma-4 RP (доноры, датасеты). |

Инструменты, конфиги и правила — [bench](../bench), [launch](../launch), [AGENTS.md](../AGENTS.md) в корне репозитория.

## Картинки — [docs\images](images)

Только **графики по реальным замерам** (генераторы: [bench\plot_kv.py](../bench/plot_kv.py) — KV-кэш и
канарейка; [bench\make_charts.py](../bench/make_charts.py) — RP-рейтинг, спекуляция, кэш промпта):

| Файл | О чём |
| --- | --- |
| `chart_rp_ranking.png` | RP-балл моделей (Non-Think/Think, Local/Cloud) |
| `chart_speculation_models.png` | без спекуляции vs MTP по моделям |
| `chart_speculation_tasks.png` | Qwen3.6: где спекуляция окупается (RP/чат/код/матем/сумма) |
| `chart_cache_prompt.png` | кэш префикса: пересчёт токенов и время на ход |
| `kv_*.png` | KV-кэш: память, бюджет VRAM, NIAH, скорость, PPL, канарейка |

Вставлены в [docs\research\kv-cache-quantization.md](research/kv-cache-quantization.md), [docs\research\speculation-research.md](research/speculation-research.md),
[docs\quality\rp-ranking.md](quality/rp-ranking.md), [docs\research\context-infinite-chat.md](research/context-infinite-chat.md), README. Встраивать
можно в любой `.md` ссылкой `images\<файл>.png` (из [docs](.)) или `docs/images\<файл>.png` (из корня).
