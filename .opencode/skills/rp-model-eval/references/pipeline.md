# RP Model Eval — методика и устройство харнесса

Полная справка к скилу `rp-model-eval`. Все пути — от корня проекта `GGUFLauncher`.

## 1. Что измеряем и зачем

«Чисто %» и скорость не показывают «ум» модели в роли. Для этого — **«мнимая история»**:
карточка персонажа + первое сообщение за персонажа + уже сыгранные ходы; финальный ход игрока
требует одновременно продолжить сцену, вспомнить факт и принять решение. Реплики игрока — живые,
с небрежностями.

Два набора сценариев (`bench\quality\prompts\`):

| Набор | Файл | Сцены | Когда |
| --- | --- | --- | --- |
| Базовый | `scenarios_rp.json` | `school`, `seduction` | скрин любой модели |
| Полный | `scenarios_rp_full.json` | + `tactics`, `mystery`, `group`, `everyday` | только лидеры |

`school` — память (Кира из Твери, не из Питера) + характер (музыка/скрипка — триггер) + инициатива.
`seduction` — память (кот Тыква, закрытие смены в 10:00) + подтекст/границы.

## 2. Конвейер

```
run_eval.py
 ├─ пишет quality\suites\suite_rp_eval_<name>_<mode>.json
 ├─ bench\rp_quality.py <suite> --out runs\rp_eval_<name>_<mode>   (поднимает и гасит сервер)
 │    └─ /apply-template → /completion (нативный, все сэмплеры), пишет metrics.jsonl, raw\, raw_full\
 ├─ СУДЬИ (панель 4, по одному ответы — одни и те же):
 │    ├─ bench\quality\rp_judge.py <run_dirs> --model <gemma> …    (локальный сервер судьи)
 │    ├─ bench\quality\rp_judge.py <run_dirs> --model <qwen>  --spec
 │    ├─ bench\quality\api_judge.py <run_dirs> --model deepseek-flash …   (облако, параллельно)
 │    └─ bench\quality\api_judge.py <run_dirs> --model deepseek-v4-pro …
 └─ bench\quality\judge_score.py <judge_out…>                   (парсит оси 1–5: по судье и по панели)
```

Один `llama-server` за раз: генерация и **локальное** судейство занимают GPU. Облачные судьи
(`api_judge.py`) сервер не поднимают — GPU не нужен, ключ `DEEPSEEK_API_KEY` в `.env`.

## 2a. Логирование

`run_eval.py` пишет единый лог `logs\rp_eval_<name>_<stamp>.log`: фазы, поток вывода `rp_quality.py`
(по каждой генерации), вывод всех четырёх судей и сводки `judge_score.py`. Плюс технические логи:
`bench\quality\runs\rp_eval_<name>_<mode>\server.log` и `bench\quality\runs\rp_judge_<judge>_<name>\run.log`
(последний — только у локальных судей; облачные `dsflash`/`dsv4pro` сервера не поднимают).

> PowerShell: путь модели передавать в **одинарных** кавычках — `${MODELS_DIR}` в двойных кавычках
> раскроется как пустая переменная PowerShell и путь сломается.

## 3. Suite-файл (формат)

```json
{
  "name": "rp_eval_<name>_<mode>",
  "server": "${PROJECT_DIR}/downloads/llama-b11382-cu124/llama-server.exe",
  "model": "${MODELS_DIR}/...gguf",
  "base_args": ["-np","1","-c","51200","-fa","on","--fit","on","--load-mode","none",
                "-t","12","-tb","12","-ctk","q4_0","-ctv","q4_0",
                "--spec-type","draft-mtp","--spec-draft-n-max","5","--spec-draft-n-min","1",
                "--spec-draft-p-min","0.75","--jinja","--reasoning","off","--reasoning-budget","0"],
  "prompts": "quality/prompts/scenarios_rp.json",
  "n_predict": 500,
  "seeds": [11, 22, 33],
  "configs": [{"name":"ru_safe","sampling":{"temperature":0.6,"min_p":0.1,"top_k":0,"top_p":0.95}}]
}
```

`run_eval.py` генерирует это сам. `--family gemma` добавляет `--chat-template-file ${LLAMA_DIR}/gemma4.jinja`
и убирает спекуляцию (у gemma-26B нет MTP-головы); `--family qwen` оставляет встроенный шаблон + `draft-mtp`.

Think-режим: `--reasoning on --reasoning-budget 1024` (gemma ещё `--reasoning-effort low`),
`n_predict` 1600. Nothink: `--reasoning off --reasoning-budget 0`, `n_predict` 500.

## 4. Метрики `rp_quality.py`

Объективные (по тексту ответа): Чисто %, Чужой/1k, CJK/1k, EN-стоп, Смеш (BPE-склейки), UKR,
Junk/1k, rep8 (повторы), TTR150 (лексическое разнообразие), Cyr %, TG t/s.
`clean` = нет чужих алфавитов, служебных токенов, BPE-склеек, англ. служебных слов, повторов ≥5 %.

`strip_channels()` вырезает `thinking`: блоки `<|channel>…<channel|>` и ` thinking…</think>`,
оставляя только видимую реплику (сырой текст целиком — в `raw_full\`).

## 5. Судьи: панель из 4

Штатная оценка — четыре судьи; **баллы сравнивать только внутри одного судьи** (шкалы разные).

| Судья | Канал | Модель | Примечание |
| --- | --- | --- | --- |
| `gemma` | `rp_judge.py` (локально) | gemma-4-26B-A4B-it-UD-IQ3_XXS | мягче, ~4.4; внешний `gemma4.jinja` |
| `qwen` | `rp_judge.py` (локально) | Qwen3.6-35B-A3B-MXFP4_MOE | строже, ~3.3; `--spec` |
| `dsflash` | `api_judge.py` (облако) | `deepseek-flash` | `thinking=disabled`; ключ `.env` |
| `dsv4pro` | `api_judge.py` (облако) | `deepseek-v4-pro` | `thinking=disabled`; ключ `.env` |

Рубрика одинаковая (`ум · память · персонаж · инструкция · инициатива · русский · проза · повторы` +
проблемы с цитатами), промпт и сборка транскрипта у `api_judge.py` переиспользуются из `rp_judge.py`,
поэтому парсинг `judge_score.py` идентичен. Отличия облачных: запросы идут параллельно
(`--judge-concurrency`), сервер не поднимается, `run.log` не пишется.

`judge_score.py` принимает **несколько каталогов судей** и объединяет их оценки — это и есть
«среднее по 4 судьям» (единая цифра панели, сопоставимая с `docs\quality\rp-ranking.md`).
`run_eval.py` печатает и разбивку по каждому судье, и итоговую объединённую сводку.

## 6. Экономика прогонов

- Скрин (2 сцены): 2 × 3 сида × 2 режима = **12 генераций** на модель, плюс судейство.
- Полный набор: 6 × 3 × 2 = **36 генераций** на модель.
- Полный набор — только для лидеров скрина.
- Судейство: 2 локальных судьи — GPU-время (сервер поднимается дважды); 2 облачных — деньги за API
  (единицы запросов на модель: 12 ответов / батч 3 = 4 запроса на режим).

## 7. Ограничения (честно фиксировать)

- Судьи — LLM, не человек: 26B мягче, Qwen строже, облачные DeepSeek — свой уровень; расхождение шкал ~1 балл.
- **Баллы сравнивать только внутри одного судьи**; «среднее по 4 судьям» — отдельная (панельная) цифра.
- Самооценка при совпадении оцениваемой модели и судьи (gemma-26B / Qwen3.6 / DeepSeek-строки).
- Облачные судьи без ключа `.env` недоступны — `run_eval.py` падает с ошибкой (не подменяет панель).
- Think у части моделей ломается (незакрытый канал / утечка черновика) → ответ пустой/неотделим.
- Оценки качества RP и любые рейтинги — только после согласования с пользователем (`AGENTS.md`).
