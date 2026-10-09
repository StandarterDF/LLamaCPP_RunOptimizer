# Router-режим llama.cpp: один сервер на все модели

Как запускать любую модель с уже выверенным конфигом, не открывая отдельный `.bat`
на каждую. Введено 2026-10-08, сборка **b11382** (`0.5.0-dev`).

## Зачем и что это

`llama-server` умеет режим **router**: сервер стартует **без `-m`**, держит список
моделей и по запросу клиента грузит нужную, выгружая предыдущую. Выбор — по имени
модели в поле `model` (POST) или `?model=` (GET). Это ядро llama.cpp, не сторонний
прокси.

В репозитории:

| Файл | Назначение |
| --- | --- |
| `launch\router\run-router.bat` | **универсальный запускатель** — поднимите и пользуйтесь. |
| `launch\router\run-rp-router.bat` | **RP-роутер** — профиль того же запускателя (порт 9932): только проверенные RP-модели. |
| `launch\router\models-preset.ini` | шаблон списка моделей и их конфигов (пути — плейсхолдерами). |
| `launch\router\models-preset-rp.ini` | шаблон RP-набора моделей. |
| `launch\router\build_preset.ps1` | сборка рабочего пресета: раскрывает пути, отсеивает отсутствующие модели. |
| `launch\router\trim_log.ps1` | фильтр консольного вывода: убирает пустые `[pid]`-строки прогресса загрузки. |
| `launch\router\models-preset.local.ini` | **генерируется** при запуске; в git не попадает (личные пути). |

Пошаговые `.bat` в `launch\b11382-cu124\` остаются как есть — router их не заменяет,
а дополняет (тот же движок, только одна модель и без «меню»).

## Быстрый старт

```bat
launch\router\run-router.bat
```

Что произойдёт:

1. пути берутся из `config.local.bat` (как у остальных `.bat`);
2. `build_preset.ps1` собирает `models-preset.local.ini`: подставляет
   `${MODELS_DIR}` / `${LLAMA_DIR}` / `${PROJECT_DIR}` и **выбрасывает секции, чьих
   файлов на этом ПК нет** — в списке остаются только реально доступные модели;
3. поднимается `llama-server --models-preset ... --models-max 1 --host 0.0.0.0 --port 9931`;
4. в консоль печатается список id моделей и адрес.

Порт по умолчанию `9931` (как у большинства `.bat`), меняется переменной
`ROUTER_PORT`. Доп. флаги можно передать аргументами: `run-router.bat --models-max 2`.

Проверка, что сервер жив:

```powershell
curl.exe http://127.0.0.1:9931/v1/models          # список моделей
curl.exe http://127.0.0.1:9931/health             # 503 при загрузке, 200 готов
```

## Имена моделей (id)

Имя секции в `models-preset.ini` = `id` модели в API. Полный список печатает запуск;
основные:

| id | Модель | Профиль |
| --- | --- | --- |
| `qwen36-35b-a3b` | Qwen3.6-35B-A3B Q2_K_XL | чат/код/матем, MTP + mmproj (vision), c=131k |
| `qwen36-35b-a3b-code` | Qwen3.6-35B-A3B | код: DFlash + ngram, c=131k |
| `qwen36-35b-a3b-base-rp-nothink` / `-think` | Qwen3.6-35B-A3B | RP-baseline (не RP-модель) |
| `gemma4-26a4b-styletune` | StyleTune-V2 | чат/код, MTP |
| `gemma4-26a4b-styletune-nothink` | StyleTune-V2 | чат, MTP, no-think |
| `gemma4-26a4b-styletune-rp` | StyleTune-V2 | **RP** (без спекуляции) |
| `gemma4-26a4b-styletune-code` | StyleTune-V2 | код: DFlash + ngram |
| `gemma4-26a4b-base-nothink` / `-think` | Gemma-4-26B-A4B-it | базовый baseline |
| `gemma4-31b-blume-v1` / `-think` | Giftige-Blume-v1 | RP-мерж (31B dense) |
| `gemma4-31b-schattenblume` / `-think` | Schattenblume | RP-мерж |
| `gemma4-31b-dark-thoughts` / `-think` | Dark-Thoughts V2 | RP-эталон |
| `gemma4-31b-glistening` / `-think` | Glistening-Gem v2.1 | RP-мерж |
| `qwen38-27b`, `qwen38-27b-nothink`, `qwen38-27b-base-rp-*` | Qwen3.8-27B | универсальная dense |
| `qwen36-27b-fable-nothink` / `-think` / `-author` | Qwen3.6-27B Fable-Fusion-711 (dense heretic) | RU-общего профиля (панель 3.46), **RP — без спекуляции**; `-author` — сэмплинг автора (3.30) |
| `qwen36-27b-fable-mtp` | Qwen3.6-27B Fable-Fusion-711 | общий/код/чат (MTP: +6–13 % на коде, на RP −4 t/s) |
| `swift-1.5`, `-nothink`, `-agent`, `-131k` | Swift-1.5-Qwen3.8-27B | efficient-reasoning / агенты |
| `dans-pers13` | Dans-PersonalityEngine-24B | чат-компаньон (на стенде файла нет) |

Числа и вердикты по моделям — `docs\models.md`; конфиги построчно повторяют
`.bat` из `launch\b11382-cu124\`.

## RP-роутер (отдельный, порт 9932)

`launch\router\run-rp-router.bat` — тот же движок, но **отдельный набор: только
проверенные RP-модели**. Профиль задаётся переменными (`ROUTER_TEMPLATE`,
`ROUTER_PORT=9932`, `ROUTER_TAG=rp-router`) и вызывает `run-router.bat`; порты не
конфликтуют (9931/9932), логи разведены (`logs\rp-router_*.log`). На 16 ГБ держите
загруженной модель только в одном роутере — две модели в VRAM не влезут.

Состав — по итогам оценки RP LLM-судьёй (полный набор, два судьи; `docs\quality\rp-quality-eval.md`):

| id | Модель | Замер (Gemma / Qwen) | Режим |
| --- | --- | --- | --- |
| `gemma4-31b-blume-v1` (+`-think`) | Giftige-Blume-v1 | 4.33 / 3.35 · лучшая инициатива | NoThink |
| `gemma4-31b-schattenblume` (+`-think`) | Schattenblume | 4.38 / 3.28 | NoThink |
| `gemma4-31b-glistening` (+`-think`) | Glistening-Gem v2.1 | 4.32 / 3.35 · лучшая память | NoThink |
| `gemma4-31b-dark-thoughts` (+`-think`) | Dark-Thoughts V2 | 4.24 / 3.11 · эталон | NoThink |
| `gemma4-26a4b-styletune-rp` (+`-think`) | StyleTune-26B | ~63 t/s, без спекуляции | NoThink |
| `gemma4-26a4b-goetia` (+`-think`) | Goetia-26B-A4B | ~73 t/s, ⚠️ путает сущности | NoThink |

Оговорки:

- **Рабочий режим — NoThink.** Think-варианты оставлены для сравнения: у 31B-мержей
  think часто даёт пустые ответы (незакрытый канал).
- У **Goetia** think в llama.cpp **непригоден** (утечка reasoning) — секция помечена.
- У **StyleTune** think-вариант собран по аналогии с `base-rp-think`; отдельным
  `.bat` он не проверялся.
- Файла **Goetia-26B-A4B** на стенде нет — обе её секции отсеиваются при сборке и
  появятся сами после скачивания.
- Дополнить состав — правкой `models-preset-rp.ini`; отсутствующие файлы
  пропускаются автоматически.

## Использование из клиента

OpenAI-совместимо; ключевое отличие — **обязательное поле `model`**:

```powershell
$body = '{"model":"gemma4-31b-blume-v1","messages":[{"role":"user","content":"Привет"}],"max_tokens":200}'
Invoke-RestMethod http://127.0.0.1:9931/v1/chat/completions -Method Post -Body $body -ContentType 'application/json'
```

- **SillyTavern / OpenWebUI / любые OpenAI-клиенты:** base URL `http://<host>:9931/v1`,
  API key можно пустой; имя модели в клиенте — один из `id` (не обязательно из
  `/v1/models`, но удобно брать оттуда).
- **Web UI:** `http://127.0.0.1:9931/` — выбор модели в интерфейсе.
- Первый запрос к новой модели **грузит её** (десятки секунд) — это нормально,
  `/health` до готовности отдаёт 503.

## Особенности и грабли (проверено)

- **`--models-max 1`** — в VRAM живёт одна модель; следующий запрос к другой
  выгружает текущую (в логе: `loading queued model name=...`). На 16 ГБ это
  обязательное условие, иначе две модели не влезут.
- **`alias` в секции не работает** — router сам управляет именами; id = имя секции.
- **Неизвестный ключ = ошибка парсинга всего файла** (`option '...' not recognized
  in preset '...'`). Опечатка в конфиге валится сразу на старте — это плюс.
- **INI — только UTF-8 без BOM**, иначе `failed to parse server config file`.
  `build_preset.ps1` пишет именно так. Сам `.ps1` при этом хранится **с BOM** —
  иначе Windows PowerShell 5.1 читает русские строки как ANSI и скрипт не парсится.
- **Пустые строки `[pid]` в консоли (исправлено):** при загрузке весов дочерний
  llama-server рисует прогресс одиночными `\r`, а роутер печатает каждый как
  отдельную строку `[pid] ` — лавина пустых строк. `run-router.bat` пропускает
  stdout сервера через `trim_log.ps1`: пустые строки отбрасываются, содержательное
  (загрузка, статистика генерации, ошибки) остаётся. stderr роутера идёт в консоль
  напрямую и пишется в `logs\`.
- **`--models-dir` тут не годится:** роутер сканирует только верхний уровень папки
  и каждый подкаталог считает одной моделью. Модели на стенде лежат глубоко
  (`автор\модель\файл.gguf`) — сканирование дало 0 моделей. Поэтому список задан
  **пресетом** (`--models-preset`) с явными путями, а `mmproj`-файлы и эмбеддинги
  в список не попадают.
- **Пути — только локальные.** Шаблон хранит `${MODELS_DIR}` и т.п.; реальные пути
  появляются лишь в `models-preset.local.ini` (gitignored). Перед коммитом — `python bench\sanitize.py`.
- **Эмбеддинг-модели** (`nomic-embed-text`, `embeddinggemma`) в пресет не включены —
  их удобнее поднимать отдельным процессом с `--embeddings`.

## Проверка (2026-10-08, RTX 4060 Ti 16 ГБ, b11382)

- Сборка пресета: включено **29** моделей (+3 — Qwen3.6-27B Fable no-think/think/author), пропущено 1 (`dans-pers13` — файла нет).
- `GET /v1/models` вернул 26 id; парсинг конфига без ошибок.
- Реальная загрузка и генерация: `qwen36-35b-a3b` — ок (mmproj, MTP); базовый RP —
  ответ за 4 с; переключение на `gemma4-31b-blume-v1` (внешний `model-draft`) —
  загрузка и ответ за 17 с.
- **RP-роутер:** собрано **10** моделей, пропущено 2 (обе Goetia — файла нет);
  `run-rp-router.bat` поднялся на 9932; генерация `gemma4-26a4b-styletune-rp` —
  ролевой ответ на ~55 t/s.
- Логи — `logs\router_*.log` (общий) и `logs\rp-router_*.log` (RP).

## Что осталось не проверено

- Одновременная работа нескольких моделей (`--models-max 2+`) на 16 ГБ — VRAM
  не хватит; на больших картах — эксперимент.
- `load-on-startup` / прогрев модели — не настраивали.
- Эмбеддинги и rerank через router — не проверяли.
- Автоматическое переключение «по задаче» (без указания `model` в запросе) — не
  поддерживается, модель задаёт клиент.

## Ссылки

- Конфиги по одной модели — `launch\b11382-cu124\`.
- Реестр моделей и числа — `docs\models.md`; реестр проверенного — `docs\researched.md`.
- Возможности спекуляции — `docs\research\speculation-research.md`.
