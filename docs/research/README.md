# docs\research — внешний ресёрч и кросс-темы

Обзоры внешних источников (HF, бенчмарки, статьи) и темы, не привязанные к одной модели:
спекуляция, контекст, KV-кэш, датасеты. Локальные исследования конкретных моделей —
[docs\models](../models/README.md).

| Файл | О чём |
| --- | --- |
| [speculation-research.md](speculation-research.md) | Методы спекуляции, внешние спекуляторы, сравнение сборок. |
| [context-infinite-chat.md](context-infinite-chat.md) | Длинные сессии, «бесконечный» контекст, кэш префикса, SillyTavern. |
| [context-memory-model.md](context-memory-model.md) | Эмпирическая модель «VRAM → макс. контекст», формулы KV; инструмент [bench\vram_model.py](../../bench/vram_model.py). |
| [kv-cache-quantization.md](kv-cache-quantization.md) | Квантование KV-кэша (f16/q8_0/q4_0): промптовые сравнения, NIAH, PPL, бюджет VRAM. |
| [kv-cache-external.md](kv-cache-external.md) | Внешние данные о влиянии KV: tool/JSON, код, KL-дивергенция, attention sinks, многотирн. |
| [router-mode.md](router-mode.md) | Router-режим llama.cpp: один сервер на все модели ([launch\router](../../launch/router/README.md)). |
| [rp-model-candidates.md](rp-model-candidates.md) | Внешние RP-кандидаты Gemma 4 и русский (сообщество, HF). |
| [qwen-mistral-rp-candidates.md](qwen-mistral-rp-candidates.md) | Внешние RP-кандидаты Qwen/Mistral: обзоры и отбор. |
| [caliperbench-2026-10.md](caliperbench-2026-10.md) | CaliperBench: RP-рейтинг Gemma 4, правило «что держит русский». |
| [euroeval-2026-10.md](euroeval-2026-10.md) | EuroEval: славянские прокси-языки для оценки русского. |
| [why-ru-models.md](why-ru-models.md) | Почему одни модели держат русский, а другие рассыпаются (PPL, провенанс). |
| [gemma4-rp-training-data.md](gemma4-rp-training-data.md) | На чём обучались наши Gemma-4 RP-мержи и современные Gemma-4 RP (доноры, датасеты). |
| [rp-datasets-en-ru.md](rp-datasets-en-ru.md) | Датасеты RP/DRP/ERP (EN и RU): пул для SFT и перевода EN→RU. |
| [rp-datasets-quality-check.md](rp-datasets-quality-check.md) | Проверка тех же датасетов по факту (реальные строки HF): дубли, формат, вердикты. |
