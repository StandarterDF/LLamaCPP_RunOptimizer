# bench\quality — оценка качества RP

Харнесс «мнимая история + LLM-судья»: модель отыгрывает сценарий (карточка персонажа, ходы),
судьи ставят баллы по осям, итог — витрина [docs\quality\rp-ranking.md](../../docs/quality/rp-ranking.md).
Методика — [docs\quality\rp-quality-eval.md](../../docs/quality/rp-quality-eval.md); автоматизация —
скил rp-model-eval ([.opencode\skills\rp-model-eval\SKILL.md](../../.opencode/skills/rp-model-eval/SKILL.md)).

## Пайплайн

1. [rp_quality.py](rp_quality.py) — прогон модели: сценарии → ответы (`runs\<прогон>\raw\`, `raw_full\`) + `metrics.jsonl`.
2. Наборы для прогона — [suites](suites/README.md) (генерируются из [prompts](prompts/README.md)).
3. Судьи: [rp_judge.py](rp_judge.py) — локальные (llama-server), [api_judge.py](api_judge.py) — облачные (DeepSeek API).
4. Агрегация: [panel_score.py](panel_score.py) — панель 4 судей; [judge_table.py](judge_table.py),
   [judge_score.py](judge_score.py), [aggregate.py](aggregate.py) — сводки и разбор.
5. Выводы — в `docs\quality\...` и реестры ([docs\models.md](../../docs/models.md), [docs\researched.md](../../docs/researched.md)).

## Скрипты

| Файл | О чём |
| --- | --- |
| [rp_quality.py](rp_quality.py) | Основной харнесс прогона (сценарии, сэмплинги, разбор «мусора» и кириллицы). |
| [rp_judge.py](rp_judge.py) | Локальное судейство через llama-server (gemma-4-26B, Qwen3.6-35B). |
| [api_judge.py](api_judge.py) | Облачное судейство через API (DeepSeek-Flash/Pro); ключ — `DEEPSEEK_API_KEY` в `.env`. |
| [judge_pack.py](judge_pack.py) | Упаковка ответов в пакеты для судей. |
| [judge_score.py](judge_score.py) | Разбор ответов судей и баллы. |
| [judge_table.py](judge_table.py) | Сводка: per (модель, режим) → среднее по каждому судье и общее. |
| [panel_score.py](panel_score.py) | Панельная агрегация (4 судьи) — числа для витрины. |
| [aggregate.py](aggregate.py) | Сводка `metrics.jsonl` от rp_quality.py по конфигам. |
| [api_rp_eval.py](api_rp_eval.py) | Прогон облачных моделей через API в формат харнесса. |
| [api_metrics_summary.py](api_metrics_summary.py) | Сводка метрик облачных прогонов. |
| [router_eval.py](router_eval.py) | RP-оценка моделей через роутер (один сервер). |
| [inspect_junk.py](inspect_junk.py) | Разбор «мусора» в сохранённых ответах (проблемные токены). |
| [gguf_vocab.py](gguf_vocab.py) | Чтение словаря из GGUF (без загрузки весов): проверки токенизатора и генерация чёрных списков id ([data](data/README.md)). |
| [tokenizer_profile.py](tokenizer_profile.py) | Быстрый статический профиль GGUF-токенизатора под русский. |

## Папки

| Папка | О чём |
| --- | --- |
| [corpus](corpus/README.md) | Чистый русский корпус для PPL/токенизаторных проверок. |
| [data](data/README.md) | Данные для анализа ответов (чёрный список токенов). |
| [prompts](prompts/README.md) | Сценарии RP и RU-промпты. |
| [suites](suites/README.md) | Сгенерированные наборы под конкретную модель/режим. |
| [runs](runs/README.md) | Результаты прогонов и судейства (raw, raw_full, metrics, панель). |
