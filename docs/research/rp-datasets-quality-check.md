# Проверка качества RP-датасетов по факту (EN/RU)

Срез: **2026-10-08**. Дополняет первичный обзор [docs\research\rp-datasets-en-ru.md](rp-datasets-en-ru.md) (не пересказ
карточек, а **фактическая проверка**). Источник данных — **HF datasets-server API**
(`/splits`, `/size`, `/rows`, `/info`), HF API метаданных и `resolve/main` (range-запросы) для
репо с отключённым viewer. Методика в 1 строку: тянем реальные строки, считаем дубли/NSFW/длину
ходов эвристикой по сэмплам, читаем README.

## 0. Что реально удалось проверить

| Способ | Датасеты |
| --- | --- |
| **Реальные строки через `/rows`** (viewer работает) | Gryphe/Sonnet3.5, hieunguyenminh/roleplay, agentlans/combined-roleplay (7 конфигов), IlyaGusev/gpt_roleplay_realm (en/ru), Arketov/ru_roleplay_conversation, krplt/ru-fictext-nsfw, rickRossie/bluemoon, sdsr/erp-and-erotica, xywang1/OpenCharacter, march228/factual-…-ru |
| **Строки через дериватив** (оригинал с viewer off) | PygmalionAI/PIPPA → `roleplay4fun/pippa` (parquet-копия deduped) |
| **Реальный файл через `resolve` (range)** | Neph0s/CoSER (книга «A Christmas Carol»), ZenMoore/RoleBench (`role-specific-Sherlock Holmes.jsonl`), fujiiee/roleplay-bot-data (`npc_database.json`, `operations.json`, `runtime_state.json`) |
| **Только README/схема, содержимое не прочитано** | lemonilia/LimaRP (парол. 7z), sinhal/Charcard-Roleplay-ShareGPT-NSFW (LFS jsonl, viewer off), Arketov/ru_roleplay_conversation_chub (LFS parquet, viewer off) |

**Важное ограничение:** range-запросы к **LFS-файлам** (`PIPPA`, `sinhal`, chub-parquet) в этом
окружении падают («socket closed»), а viewer у них отключён на уровне репо. Поэтому PIPPA
проверен по parquet-копии, а `sinhal` и `chub` — **не проверены построчно** (помечено ниже).

---

## 1. Сводная таблица (факт → качество → вердикт)

Оценка — «качество как RP-SFT», 1–5 (шаг 0.5), **по факту просмотренных строк**, а не по репутации.

| Датасет | Строк (факт) | Формат (факт) | Качество | Вердикт |
| --- | ---: | --- | :---: | --- |
| **Gryphe/Sonnet3.5-Charcard-Roleplay** | **9 736** | 1 колонка `conversations` (ShareGPT: system/human/gpt) | **5.0** | **Переводить** (лучший RP-стиль; лицензия unknown) |
| **sinhal/Charcard-Roleplay-ShareGPT-NSFW** | 9 736 (карточка) | ShareGPT JSONL, 164.7 МБ | 5.0* | **Переводить** (CC-BY-4.0; *строки не читались, но имя файла/кол-во/формат = Gryphe) |
| **PygmalionAI/PIPPA** | ~26 000 диалогов (ориг.); **16 832** в deduped-копии | JSONL, кастом: `bot_name`, `conversation[{role,content}]`, `memory`, `examples`, `nsfw` | **3.5** | **Брать + чистить + переводить** (объём, NSFW, персоны; шум/опечатки) |
| **lemonilia/LimaRP** | ~2 000 (карточка) | YAML + build-скрипт в **парольном 7z** | **4.0*** | **Переводить** (эталон human-RP; *не проверено — архив) |
| **Neph0s/CoSER** | 771 книга; SFT-файл **2 119.6 МБ** | JSON (plots/scenario/dialogues) + ShareGPT-файл | **4.0** | **Переводить только диалоги** (проза/память; копирайт книг) |
| **hieunguyenminh/roleplay** | **5 755** | parquet: `name`,`description`,`text` (весь диалог с `<|system|>…<|assistant|>`) | **2.5** | Брать/переводить как добор (синтетика, «интервью»-стиль) |
| **rickRossie/bluemoon_…300k** | **261 071** сообщ. | parquet: `thread_title`,`thread_href`,`message_timestamp`,`message_username`,`message` | **2.5** | Брать после **реконструкции тредов** (сырые посты форума, не диалоги) |
| **sdsr/erp-and-erotica** | **3 876 388** (partial; est. 41 327 511) | parquet: тот же форум-схема, что у bluemoon | **1.5** | **Не брать как SFT** без парсера (сырой HTML со `<script>`/`<div>`) |
| **agentlans/combined-roleplay** | 1 415 390 (21 конфиг) | parquet/jsonl: `conversations[{from,value}]`, `source` | **2.5** | Брать **только RP-конфиги** (см. §3); много не-RP |
| **IlyaGusev/gpt_roleplay_realm** | **en 216 / ru 219** персонажей ×20 диалогов | parquet: `name`,`context`,`greeting`,`example_dialogue`,`dialogues`,`image` | **3.0** | **Брать RU как есть** (чистый русский, но «интервью»-формат) |
| **xywang1/OpenCharacter** | **20 000** персонажей + **306 140** диалогов | jsonl: персона/`question`/`character_answer` | **2.5** | Переводить (одноходовые ответы, не multi-turn RP) |
| **ZenMoore/RoleBench** | 168 093 (карточка) | jsonl: `instruction`,`metrics`,`answer`,`type` | **2.0** | Брать/переводить (инструкции+ответы, не диалоги) |
| **Arketov/ru_roleplay_conversation** | **11 686** | jsonl: `bot`,`user`,`*_persona`,`scenario`,`conv[{role,content}]`,`tags` | **2.0** | **Не как эталон**: сырой MT lima+pippa+bluemoon, ошибки рода/имена |
| **Arketov/ru_roleplay_conversation_chub** | 6 548 (карточка); parquet 413.7 МБ | parquet: `*_en` и `*_ru` поля, `conversation_{en,ru}[{content,is_bot}]` | **н/п** | **Не проверено**; двойные en/ru поля → скорее **параллельный/переводной**, а не чисто RU-native |
| **krplt/ru-fictext-nsfw** | **16 202** | parquet: `title`,`tags`,`text`,`rating` (лайки) | **3.0** (проза) / **1.5** (как диалог) | **Брать для RU-ERP-прозы/стиля** (не диалоги; есть extreme) |
| **fujiiee/roleplay-bot-data** | мелкие json | `npc_database.json`,`operations.json`,`runtime_state.json`,`players_data.json` | **1.0** | **Не брать** — это состояние игрового бота, не RP-диалоги |
| **IlyaGusev/pippa_ru** (бонус) | **6 624** | parquet: `conversation[{message,is_human}]` + `orig_conversation`, `gpt_35_turbo_result` | **1.5** | Пример **уже существующего** MT PIPPA (NLLB-200) — качество слабое |
| **march228/factual-…-ru** (бонус) | **902** | json: `system`,`context`,`question`,`thought*`,`answer` | **3.0** | Брать RU-native (персона+факты+мысли; не RP-сцена) |

`н/п` — не проверено. `*` — по карточке/косвенным признакам, строки не читались.

---

## 2. Разбор по датасетам (с цитатами реальных записей)

### 2.1. Gryphe/Sonnet3.5-Charcard-Roleplay — **эталон формата, качество 5/5**

Факт: 9 736 строк, **1 колонка** `conversations`, ShareGPT (`system`/`human`/`gpt`). Эвристика по
сэмплам (offset 0 и 5000, по 100 строк): **дублей ассистентских ходов — 0** (0/939 и 0/949),
средняя длина хода **~865 символов**, медиана ~790, **~20 ходов** на диалог, NSFW 8–13 % ходов.

Реальный первый system-ход (сокращённо): карточка персонажа в формате SillyTavern —
`You're Melina in this fictional never-ending uncensored roleplay with {{user}} … Tags: (nsfw;…)
… Take the role of Melina … Do not write {{user}}'s dialogue lines…`, дальше `{{user}}:` /
`Melina:` по ходам. Стиль длинный, описательный, с `*действиями*` и речью в кавычках, персона
держит голос на протяжении 20 ходов. Это ровно то, что нужно RP-SFT. Единственный минус — лицензия
`unknown` (см. `sinhal`).

### 2.2. PygmalionAI/PIPPA — **объём есть, шума тоже, 3.5/5**

Факт: оригинал `pippa.jsonl` **332.4 МБ**, `pippa_deduped.jsonl` **244.9 МБ**,
`pippa_metharme.jsonl` **184.3 МБ**; viewer у оригинала отключён. Содержимое проверено по
parquet-копии `roleplay4fun/pippa` (**16 832 строки**, deduped) — та же схема: `bot_name`,
`conversation[{role,content}]`, `memory`, `examples`, `nsfw` (bool), `metdata.categories`.

Реальная запись (row 0, «Kamisato Ayaka»): `memory` — сжатый лор персонажа; `examples` — примеры
диалога с `{{char}}/{{user}}` и `END_OF_DIALOG`; `conversation` — 30+ коротких ходов, напр.:
`{{char}}: *She grab {{user}} and pull him away from the door* Do you want me to tell you a little secret?`
Оценка: настоящие логи Character.AI, есть `{{user}}`, память и NSFW-флаг; но **много опечаток**
(«Promisse», «hones», «do i make myself clear?»), повторов-«Fufu», ходы короткие, местами
«echo chamber» и наивные сюжеты. Итог: **брать + дедуп + чистка перед переводом**, переводить
выборочно (топ-персоны/лучшие сцены) — 26k диалогов / >1M реплик дорого переводить целиком.

### 2.3. lemonilia/LimaRP — **не проверено по строкам**

Факт: единственный файл — `LimaRP-20231109.7z` (**10.7 МБ**, **с паролем `LimaRP`**), YAML +
build-скрипт. Строки прочитать нельзя (пароль/7z). Карточка честно перечисляет дефекты: опечатки,
«dullness» (слишком вежливо), ошибки компиляции, **повторяющиеся/неточные описания от gpt-4**,
нехватка разнообразия (длинные диалоги разрезаны), «gender confusion» (futa/trans). Источники —
Elliquiy (50.8 %), Blue Moon (18.4 %), Lolicit (10.5 %) и др. Это human-human, но с оговорками.
Вердикт: **переводить лучшим MT** (малый объём), но сначала снять пароль и проверить вручную.

### 2.4. sinhal/Charcard-Roleplay-ShareGPT-NSFW — **та же Gryphe-данные, но CC-BY-4.0**

Факт: viewer отключён, единственный файл `sonnet35-charcard-roleplay-sharegpt.jsonl` (**164.7 МБ**).
Карточка: **9 736 диалогов**, ~19.6 ходов, min/max 6/50, source Claude Sonnet 3.5, лицензия
**cc-by-4.0**. Имя файла, число и формат **совпадают** с `Gryphe/Sonnet3.5-Charcard-Roleplay` →
почти наверняка **ре-аплоад того же корпуса** с исправленной лицензией. Построчно не проверялся,
поэтому ставлю 5.0 с пометкой. **Рекомендация: брать именно CC-BY-версию** (снимает риск unknown).

### 2.5. Neph0s/CoSER — **литературные диалоги, 4/5, но копирайт**

Факт: viewer падает (cast error из-за разнородной схемы `full/*.json` vs `train/*`). Проверено
через `resolve` — книга «A Christmas Carol»: структура `plots[].conversation[].dialogues[]` с
`character`+`message`, где мысли/действия в `[...]`, напр.:
`Ebenezer Scrooge: "[I cannot abide this constant interruption…] Bah. Humbug."`,
`Fred: "[He seems as cold as ever…] Christmas, a humbug, Uncle. You don't mean that."`.
SFT-файл `train/sft_conversations_sharegpt.json` = **2 119.6 МБ**; всего 771 книга. Качество
прозы/памяти высокое, multi-turn естественный. Но: (1) это **не ERP** и много нарратива;
(2) среди книг масса **копирайтных** (Harry Potter, Game of Thrones, A Court of Thorns…) — не
только Gutenberg, юридический риск. Вердикт: переводить **только реплики**, брать
public-domain/Gutenberg-часть.

### 2.6. ZenMoore/RoleBench — **инструкции, не диалоги, 2/5**

Факт: viewer падает (`DatasetGenerationCastError`: у файлов разные колонки — где-то есть `type`).
Проверен реальный `instructions-eng/role-specific-Sherlock Holmes.jsonl`:
`{"id":0,"instruction":"Sherlock Holmes, how do you develop your exceptional combat skills?",
"metrics":"Completeness: High…","answer":"My combat skills were developed through…","type":"script_based"}`.
Это **одноходовые вопрос-ответ + метрики**, не multi-turn RP. Стиль «плоский» (синтетика GPT).
Для RP-SFT слабо; годится как instruction/персона-QA.

### 2.7. hieunguyenminh/roleplay — **синтетика, «интервью»-стиль, 2.5/5**

Факт: 5 755 строк, поля `name`/`description`/`text`. Реальный `text` (Sherlock): один system-блок
(описание персонажа) + 3–5 пар `<|user|>…<|assistant|>…</s>`. Средняя длина `text` ~2 150 символов,
NSFW 0 %. Формат чисто структурирован, но это **вопрос-ответ о персонаже**, а не сцена. Годится
как добор/персона-консистентность.

### 2.8. rickRossie/bluemoon_roleplay_chat_data_300k_messages — **сырые посты форума, 2.5/5**

Факт: **261 071 строка**, 6 колонок, **одно сообщение = одна строка** (`thread_title`,
`thread_href`, `message_timestamp`, `message_username`, `message`). Реальные посты с
bluemoonroleplaying.com, напр. `Cerberus` → `Grim nodded and began pushing harder and faster.
"Oh sis you know I'm loving this…"`. NSFW в сэмпле **32 %**, средняя длина ~417 символов.
Это **не готовые диалоги**: нужна реконструкция тредов (по `thread_href`+`timestamp`) и
назначение ролей. После реконструкции — хороший «живой» human-RP (потенциально 3.5/5).

### 2.9. sdsr/erp-and-erotica — **сырой HTML-скрейп, 1.5/5**

Факт: **3 876 388 строк** (флаг `partial:true`, оценка до **41 327 511**), та же 6-колоночная
форум-схема, но источник — **blackdahliaroleplaying.com** и сообщения забиты HTML:
`<script class="js-extraPhrases"…>…</script><div class="bbImageWrapper lazyload…">…`.
Есть и «чистые» прозаические посты (пример «Air And Blood»). Средняя длина ~2 020 символов,
NSFW в сэмпле 17 %. **Это не ERP-диалоги, а дамп форума**; как SFT без парсера/чистки непригодно,
как корпус претрейна — возможно. Вердикт: **не брать как SFT** без серьёзной обработки.

### 2.10. agentlans/combined-roleplay — **микс: RP лишь часть конфигов, 2.5/5**

Факт: 21 конфиг, всего **1 415 390 строк**, схема `conversations[{from,value}]` + `source`.
Что внутри (по реальным строкам и README):

| Конфиг | Строк | Что реально |
| --- | ---: | --- |
| `soda` | 1 155 128 | **социальные диалоги**, не RP (system «You are Priest», разговор про церковь) |
| `multiturn_mix_v3_1k/10k/30k` (+v2) | 1k/10k/30k | микс, есть RP (chai/samantha/dailydialog) |
| `chai_prize_reward_model` | 18 574 | RP-логи chai, но **10.1 % точных дублей** ходов (65/642) и повторы |
| `cakrawala` | 13 000 | синтетический RP, **дублей 0/684**, ~14 ходов, средняя 365 симв. — хороший |
| `RPGPT_PublicDomain` | 3 032 | синтетический RP по персонажам классики (Rochester/Leavenworth), качественно |
| `synthetic_characters` | 17 668 | синтетический RP-карточки (`AlekseyKorshuk`), дублей ~0.7 % |
| `capybara` | 15 996 | **инструкции** (Mozart vs Beethoven), не RP |
| `creative_writing` | 8 808 | **general writing / Q&A**, не RP |
| `dialogsum`, `li2017dailydialog`, `empathetic_dialogues`, `Conversational-Reasoning-Topical-Chat` | 10–19k каждый | **не RP** (суммаризация, бытовые/эмпатичные диалоги, trivia) |
| `samantha` | 5 868 | ассистент-диалоги (AI Samantha), полу-RP |

Вердикт: брать **только** `cakrawala`, `RPGPT_PublicDomain`, `synthetic_characters` и (после дедупа)
`chai_prize_reward_model`; остальное — не RP. Как «готовый микс» для перевода **неудобен** — смешано.

### 2.11. IlyaGusev/gpt_roleplay_realm — **чистый русский, но «интервью», 3/5**

Факт: en **216** / ru **219** строк; в каждой — `name`, `context`, `greeting`, `example_dialogue`,
`topics` (20 тем), `dialogues` (~20 диалогов × `model_name`, `topic`), `image_prompt`, `image`.
RU-пример («Светлячок Фонарик»): `greeting: "Привет, дружок! Я Светлячок Фонарик. Нужна ли тебе моя
помощь?"`, затем реплики `user`/`char` про люциферин и светоциты. Русский **живой и грамотный**
(синтетика GPT-4), но формат — **вопрос-ответ о персонаже**, слабая драматургия. Вердикт:
**брать RU-ветку как есть** (готовый русский), но не ждать от неё глубокого RP.

### 2.12. xywang1/OpenCharacter — **одноходовые ответы, 2.5/5**

Факт: `Synthetic-Character` **20 000** строк (`character_id`,`persona`,`character`), `Synthetic-Dialogue`
**306 140** строк (`question`,`question_source`,`character_answer`). Реальный ответ (Eleanor Whitfield
на «Can brain cells move?») — длинный абзац от лица персонажа, но это **один ход**, не диалог.
Годится для персона-консистентности, не для multi-turn RP.

### 2.13. Arketov/ru_roleplay_conversation — **сырой MT, 2/5**

Факт: **11 686** строк, схема `bot`,`user`,`bot_persona`,`user_persona`,`scenario`,
`conv[{role,content}]`,`tags`. Карточка (304 символа): «lima, pipa и bluemoon. Переведены на
русский, нуждаются в допополнтельной фильтрации… Есть шанс очень редких дубликатов.» В данных
тег `BlueMoon_ru`. Средне: **~100 ходов на строку**, длина хода ~796 символов, дублей в сэмпле 0.
Но качество перевода плохое — реальные дефекты: путаница рода (`Он улыбнулся, его руки обвились
вокруг её талии` при мужском user-персонаже), **галлюцинированное имя** `Шеллей`, кальки
(`выпуклость его брюк прижалась к её промежности`), смешение «Хоука/Карлайл». Вердикт: **не
эталон**; можно как черновик для post-edit, но не как готовый русский.

### 2.14. Arketov/ru_roleplay_conversation_chub — **не проверено; вероятно, перевод**

Факт: viewer отключён, два LFS-parquet (**216.6 + 197.1 МБ** = 413.7 МБ), прочитать не удалось.
Схема из карточки: `user_description_en`/`_ru`, `bot_description_en`/`_ru`, `scenario_en`/`_ru`,
`example_dialogs_en`/`_ru`, `personality_en`/`_ru`, `tavern_personality_en`/`_ru`,
`conversation_en`/`_ru[{content,is_bot}]`. README (1 914 симв., **без слова «перевод»**) — «логи
ролевых игр с chub.ai… нефильтрованный контент». **Ключевое:** наличие **параллельных `_en` и `_ru`
полей** означает, что одна из сторон, скорее всего, **перевод** (chub.ai англоязычен), а не
RU-native. Поэтому тезис обзора «chub — RU-native живой стиль» **не подтверждён** и требует
осторожности. Формат — да, chub-логи (см. §4). Построчная проверка — TODO (нужен доступ к parquet).

### 2.15. krplt/ru-fictext-nsfw — **русская NSFW-проза, не диалоги, 3/5**

Факт: **16 202** строки, поля `title`,`tags`,`text`,`rating` (=**число лайков**, не оценка),
источник — **ficbook.net**, лицензия cc-by-4.0. `text` — цельные рассказы: средняя длина
**~18 900 символов**, медиана ~10 800. Русский живой и грамотный. Пример («Секс и ничего
большего»): диалоги внутри прозы, разговор в аське (`"Привет", — прочитала она в аське`).
**Риск:** теги включают extreme (`Underage`, `Зоофилия`, `Изнасилование`, `BDSM`) — нужен фильтр.
Это **ERP-проза/словарь**, а не multi-turn структура. Вердикт: брать для RU-ERP-стиля, резать
диалоги и фильтровать по тегам.

### 2.16. fujiiee/roleplay-bot-data — **НЕ RP-диалоги (подтверждено), 1/5**

Факт: 40 875 загрузок (обманчиво), но файлы — `npc_database.json`, `operations.json`,
`players_data.json`, `runtime_state.json`, `slot_history.json`. Реально это **состояние игрового
бота** про кланы котов: `npc_database.json` — `{"Ветра":{"Вербовейница":{"age":35,"status":"королева",
"trait":"…"}}}`; `operations.json` — операции с травами (`{"character":"Яблолапка","name":"Золотарник",
"delta":2,"reason":"#сбор_трав"}`); `runtime_state.json` — боевые энкаунтеры с лисами/совами
(`"last_facts":["Лиса попадает по салфетка…"]`). **RP-диалогов нет.** Утверждение обзора
подтверждено: не брать.

---

## 3. Отдельные проверки из задания

### 3.1. PIPPA vs LimaRP vs Sonnet3.5 — кто даёт лучший RP-стиль

| Критерий | PIPPA | LimaRP | Sonnet3.5-Charcard |
| --- | --- | --- | --- |
| Проверено по строкам | ✅ (deduped-копия) | ❌ (7z+пароль) | ✅ |
| Происхождение | Character.AI логи (human-AI) | **human-human** | синтетика Sonnet 3.5 (1 вызов/сцена) |
| Длина хода (факт) | короткая (десятки–сотни симв.) | ~2k-контекст сцены | **~865 симв., ~20 ходов** |
| Дубли (факт) | шум/повторы (опечатки, «Fufu») | разрезанные диалоги, повторы описаний | **0 в сэмпле** |
| NSFW | есть (флаг `nsfw`) | extreme | есть (8–13 % ходов) |
| Формат | `{{char}}/{{user}}` + memory | forum/novel-style, `<FIRST>/<SECOND>` | SillyTavern card + `{{user}}` |
| Стиль | живой, но рваный, наивный | самый «человечный», но вежливый/«dull» | **длинный, связный, держит голос** |

**Вывод:** по RP-стилю для SFT лучший — **Sonnet3.5-Charcard** (современный карточный формат,
длинные связные ходы, единый нарратив, дедуп чистый). **LimaRP** — эталон естественности
(human-human), но объём мал и стиль местами «пресный», а строки не проверены. **PIPPA** — максимум
объёма/персон/NSFW, но самый шумный. Порядок для перевода: **Sonnet3.5 → LimaRP → PIPPA**.

### 3.2. RU-native: `chub` и `krplt` — реально качественный русский?

- **krplt/ru-fictext-nsfw** — **да, русский качественный** (живая проза ficbook.net, грамотные
  диалоги внутри текста), но это **проза, не RP-структура**, и есть extreme-контент. Как «живой
  стиль» — годится; как диалоговый SFT — нет.
- **Arketov/…chub** — **не проверено построчно**; схема с параллельными `_en`/`_ru` указывает на
  **перевод/параллельный корпус**, а не на чистый RU-native. Тезис «chub = RU-native живой стиль»
  **пока не подтверждён**. Нужен доступ к parquet (viewer off).

### 3.3. «Сомнительные/обманчивые» — что на самом деле

- **rickRossie/bluemoon…300k** — **сырые посты форума** (1 сообщение = 1 строка), не диалоги;
  нужна реконструкция тредов. Подтверждено.
- **sdsr/erp-and-erotica** — **ещё сырее**: дамп форума blackdahliaroleplaying.com с HTML-мусором
  (`<script>`, `<div>`), 3.9 Млн строк (не «10M+», флаг partial). Не SFT.
- **agentlans/combined-roleplay** — **микс**: RP лишь часть конфигов (`cakrawala`, `RPGPT`,
  `synthetic_characters`, `chai`); `soda`/`capybara`/`creative_writing`/`dialogsum` — **не RP**.
- **IlyaGusev/gpt_roleplay_realm** — RU-ветка **реально русская и грамотная**, но формат —
  **«интервью»** (Q&A о персонаже), а не иммерсивная сцена; персонажей 219, а не «тысячи».
- **fujiiee/roleplay-bot-data** — подтверждено: **не RP-диалоги**, а состояние игрового бота.

---

## 4. Пригодность к EN→RU переводу (объём, доля диалогов, риски)

- **PIPPA**: огромный объём диалогов и NSFW, но **>1M реплик** — переводить выборочно; риски —
  опечатки/шум (сначала дедуп), `{{char}}`/`{{user}}`, `memory`/`examples` (переводить и их).
- **LimaRP**: малый объём (~2k) → можно дорогой LLM/ensemble; риски — сленг, extreme, futa/trans,
  `<FIRST>/<SECOND>`-плейсхолдеры, «dull»-тон.
- **Sonnet3.5 (sinhal)**: 9 736 сцен, длинные ходы, чистый формат — **идеально для MT**;
  риски — имена (транслитерация), `*действия*`, ERP-термины, `{{user}}`.
- **CoSER**: переводить **только реплики** (не весь нарратив); риски — копирайт книг, литературные
  имена/стиль, объём SFT-файла 2.1 ГБ.
- **bluemoon/sdsr**: сначала **парсинг HTML + реконструкция тредов**, потом перевод; иначе мусор.
- **combined-roleplay**: переводить **только RP-конфиги**, иначе тратите бюджет на `soda`/`capybara`.

---

## 5. Топ-5 для перевода EN→RU (по фактам)

1. **Gryphe/Sonnet3.5-Charcard-Roleplay** (лучше — CC-BY-версия **sinhal/Charcard-Roleplay-ShareGPT-NSFW**).
   9 736 современных карточных сцен, ~20 длинных ходов, **0 дублей** в сэмпле, NSFW. Лучший RP-стиль.
2. **PygmalionAI/PIPPA** (deduped). Максимум объёма/персон/NSFW, `{{user}}`+memory; переводить
   выборочно после дедупа/чистки.
3. **lemonilia/LimaRP**. Human-human эталон естественности, малый объём → дорогой качественный MT
   (сначала снять пароль и проверить).
4. **Neph0s/CoSER** (только диалоги, public-domain/Gutenberg-часть). Литературная проза + память +
   естественный multi-turn.
5. **agentlans/combined-roleplay — RP-конфиги** (`cakrawala`, `RPGPT_PublicDomain`,
   `synthetic_characters`) **или** `hieunguyenminh/roleplay` как чистый добор.

## 6. Топ-3 RU-native (по фактам)

1. **krplt/ru-fictext-nsfw** — реальный крупный **русский** корпус (16 202 рассказа, средняя длина
   ~18.9k симв., ficbook.net); качественный язык; **для ERP-прозы/словаря** (не диалоги; фильтр
   extreme-тегов: Underage/Зоофилия/Изнасилование).
2. **IlyaGusev/gpt_roleplay_realm (ru split)** — **готовый чистый русский** (219 персонажей × 20
   диалогов, cc-by-4.0); брать как есть, но формат — «интервью».
3. **march228/factual-multiagent-roleplay-ft-ru** — **RU-native** персона + факт-grounding + мысли
   (902 примера), живой русский; узкая ниша (факты в роли).

**Отдельно:** `Arketov/ru_roleplay_conversation_chub` мог бы претендовать на 1-е место, но
содержимое **не проверено** (viewer off, LFS-parquet), а параллельные `_en`/`_ru` поля указывают
на **перевод**, а не на native — поэтому в топ не ставлю до построчной проверки.

---

## 7. Итог одной таблицей «брать / брать+чистить / переводить / не брать»

| Решение | Датасеты |
| --- | --- |
| **Переводить EN→RU** | Gryphe/Sonnet3.5, sinhal/Charcard-ShareGPT-NSFW, PygmalionAI/PIPPA, lemonilia/LimaRP, Neph0s/CoSER (диалоги) |
| **Брать + чистить** | rickRossie/bluemoon (реконструкция тредов), agentlans/combined-roleplay (RP-конфиги), Arketov/ru_roleplay_conversation (post-edit MT) |
| **Брать RU как есть (ниша)** | IlyaGusev/gpt_roleplay_realm (ru), krplt/ru-fictext-nsfw (ERP-проза), march228/factual-…-ru |
| **Не брать как RP-SFT** | sdsr/erp-and-erotica (сырой HTML), fujiiee/roleplay-bot-data (состояние бота), ZenMoore/RoleBench (инструкции), xywang1/OpenCharacter (одноходовые ответы) |
| **Не проверено** | Arketov/ru_roleplay_conversation_chub (parquet, viewer off), sinhal (построчно) |

**Главные выводы:** (1) единственный **проверенно чистый** RP-датасет — Sonnet3.5-Charcard
(лучший стиль); (2) PIPPA даёт объём, но требует дедупа/чистки; (3) два «самых русских»
кандидата из обзора — `chub` (вероятно перевод, не проверен) и `krplt` (проза, не диалоги) —
то есть **готового качественного RU-RP-диалогового корпуса по-прежнему нет**.

## 8. Проверка по скачанным файлам (2026-10-09)

Дополняет §1: RP/ERP/DRP-ядро (<250 МБ) **скачано** и прочитано построчно.

- **`lemonilia/LimaRP` — теперь ПРОВЕРЕН** (ранее был запароленный 7z): 2 061 YAML с живыми
  человеческими переписками (Elliquiy/BlueMoon/Lolicit), готовые `persona`/`scenario`; есть OOC,
  `<FIRST>/<SECOND>`, `*_BAD` и extreme-контент. Это **лучший по «живости»** источник, требует чистки.
- **Дубли:** `Gryphe/Sonnet3.5-Charcard` = `sinhal/Charcard-…` (тот же файл 164.7 МБ);
  `athirdpath/DPO_Pairs-Roleplay-Alpaca-NSFW` = `athirdpath/DPO_Pairs-Roleplay-NSFW`;
  `deebosh/NSFW_RP_Format_DPO-ru` = `ResplendentAI/NSFW_RP_Format_DPO` + RU-перевод.
- **Опровергнуто по строкам:** `m0no1/dnd-35` — это не RP, а разметка состояний D&D-движка
  (`HP_UPDATE`, `STATUS`); `hieunguyenminh/roleplay` — энциклопедический Q&A ассистентским тоном,
  а не сцены. Оценки в рейтинге снижены (2 и 3 из 10).
- **Подтверждено:** `beyoru/Aesir-Character-CoT` годен только для think (CoT + `quality_rank`);
  `PocketDoc`×2 — IF/длинный контекст, не персонажи; `krplt/ru-fictext-nsfw` — проза (теги
  `Underage`/`Зоофилия`); `Kingfall` — мультиязычный фанфик без русского; `bluemoon` — сырые посты.
