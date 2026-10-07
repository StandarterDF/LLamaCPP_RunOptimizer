# RP-модели: внешний ресёрч (сообщество и HF), срез 2026-10-05

Сводка по итогам двух Space Bunny-агентов (Playwright по Reddit; fetch по Hugging Face).
Наши собственные замеры — в `docs\quality\sampling-quality.md`. Здесь только **внешние** источники;
где вывод, а не цитата — помечено.

## 0. Методика и ограничения

- Reddit: r/SillyTavernAI (основной), r/LocalLLaMA. Отдельных тредов «best model» модераторы
  больше не допускают — всё сводится в **еженедельный мега-тред** («Megathread: Best Models/API
  discussion week of …», архив с 19.03.2026). Агент прочитал **последний** мега-тред (04.10.2026)
  и 8 тематических тредов; **весь архив недель не пройден**.
- HF: карточки и HF API напрямую, числа (downloads/likes) — на 2026-10-05.
- Русский RP в англоязычных сообществах почти не обсуждается; основное — HF-дискуссии и ру-блоги.

## 1. Общие фавориты r/SillyTavernAI (октябрь 2026)

| Модель | Тип | Почему | Источник |
| --- | --- | --- | --- |
| **Kimi K3** | MoE ~3T | топ-1 пост месяца (1014 pts); почти не отказывает, чинится prefill | [тред](https://www.reddit.com/r/SillyTavernAI/comments/1wu7dqd/kimi_k3/) |
| **Gemma 4 31B / 26B-A4B** | dense / MoE | лучший **локальный** RP: инструкции до ~60k, персонажи, uncensored | [тред](https://www.reddit.com/r/SillyTavernAI/comments/1u5y3p2/what_makes_gemma_4_so_special/) |
| **GLM 4.6 / 4.7** | MoE | фаворит NSFL, «без агрессивного RLHF», лучший coherence | [тред](https://www.reddit.com/r/SillyTavernAI/comments/1wx1bf4/favorite_model_for_nslf/) |
| **DeepSeek V3.2** | MoE | «классика», без thinking-блока, минимальный nudge | [пост](https://www.reddit.com/r/SillyTavernAI/comments/1tbtfcl/) |
| **MiMo V2.6 Pro** | — | лучшая проза «из коробки», дешевле; нужен простой пресет | [тред](https://www.reddit.com/r/SillyTavernAI/comments/1wvr1qs/) |

Критика Gemma 4 (важно): positive bias (тянет светлые исходы), заточка под короткие рассказы.
Практика: только **chat completion** (не text completion), jinja + thinking, а слова-тики лечить
logit-ban, а не файнтюном.

## 1.1. Динамика по недельным мега-тредам (9 недель, 09.08–04.10.2026)

| Неделя | Gemma-4-файнтюны-лидеры | Прочее |
| --- | --- | --- |
| 08-09 | Skyfall-31B v4.2 (12), Queen (11), Glimmer-26B, MeroMero-26B | Muse Glimmer 30B, Qwen 3.8, GLM 5.2, Mistral-24B-фт |
| 08-16 | Orion-26B (16), Skyfall (6), StyleTune (2) | Mistral-24B-фт лидер («still best»), GLM, Qwen 3.8 (критика) |
| 08-23 | Skyfall, Orion, MeroMero; «MoE→31B massive improvement» | Qwen 3.8, GLM 5.2 (деградация), Cydonia-v4.3 |
| 08-30 | **Dark Thoughts v2 (9)**, Queen-QAT (8), Orion | GLM 5.3 (полярно), eqbench/caliperbench |
| 09-06 | Orion (16), Boulesis (15), MeroMero (9), Artemis (12) | Boulesis — «FINALLY good prose» |
| 09-13 | Skyfall (18), Boulesis (12), Artemis (11), StyleTune (8) | Deepseek V4.1 flash, GLM, Kimi 2.5 |
| 09-20 | Skyfall (14), Loki Skotoma v2 (13), Schattenblume, Garnet | Kimi 2.5, Split-Untied-31B (14) |
| 09-27 | Schattenblume-31B (9), MeroMero (4), Reddit: «Dark Thoughts v2 — топ-3 G4 31B» | GLM 5.3/Flash, MiMo 2.6, CaliperBench v3 |
| 10-04 | Artemis-31B v1.2, Dark Thoughts v2, Orion, StyleTune | спрос: «кто из G4-фт держит не-англ.?» → ответ: **Dark Thoughts V2**, остальные нет |

**Выводы:** тема Gemma 4 доминирует все 9 недель, с трендом от MoE 26B к dense 31B; лидеры
ротируются (Skyfall — 3 недели, Orion/Boulesis/Queen/Schattenblume/MeroMero), устойчиво держатся
**MeroMero** и **StyleTune**, к концу периода — **Dark Thoughts V2** и **Artemis-31B-v1.2**.
Из API-моделей во всех неделях присутствует GLM (с жалобами на деградацию), Qwen 3.8 — постоянно,
но с негативом. **Про русский за 9 недель — ровно одна содержательная реплика** (10-04): годен
только Dark Thoughts V2, а Orion/StyleTune/Split-Untied — нет.

Мега-треды (r/SillyTavernAI, `comments/<id>`): 08-09 `1vk3byn`, 08-16 `1vqanqm`, 08-23 `1vwl1iv`,
08-30 `1w2vh8u`, 09-06 `1w9abpf`, 09-13 `1wflsa9`, 09-20 `1wluzky`, 09-27 `1wrxo41`, 10-04 `1wxsier`.

## 2. Файнтюны Gemma 4 под RP (Reddit + HF)

| Модель | База | За что хвалят | Русский | Ссылка |
| --- | --- | --- | --- | --- |
| **Dark Thoughts V2 31B** | Gemma-4-31B | «**follows other languages quite accurately**» — единственный Gemma-4-финтюн, названный годным для не-англ. | ✅ лучший сигнал | [Ateron](https://huggingface.co/Ateron/Gemma-4-Dark-Thoughts-V2-31B) |
| Scotoma-2 31B | Gemma-4-31B | чинит «slop»-тики Gemma; abliteration+DPO; **самая скачиваемая** (224k) | ❓ не проверено | [GGUF](https://huggingface.co/ReadyArt/gemma-4-31B-it-scotoma-2-GGUF) |
| Artemis 31B v1.2 | Gemma-4-31B | «peak» в свежем мега-треде; лидер англ. RP по CaliperBench (RP #9/31B); длинные монологи — минус | ⚠️ наш тест: 92–96 % (редкие BPE-склейки), на русском не выделяется | [TheDrummer](https://huggingface.co/TheDrummer/Artemis-31B-v1.2) |
| G4-MeroMero-v2 31B | Gemma-4-31B | топ-3 RP-финтюнов у iamvikingcore | ❓ | [zerofata](https://huggingface.co/zerofata/G4-MeroMero-v2-31B) |
| Orion 26B-A4B v1.1 | Gemma-4-26B-A4B | 50 likes, GGUF у bartowski | ❌/❓ | [TheDrummer](https://huggingface.co/TheDrummer/Orion-26B-A4B-v1.1) |
| Split-Untied 31B | Gemma-4-31B | — | ❌ «not suitable at all for languages other than English» | `docs\models\gemma-4-31b-rp-merges.md` |

## 3. Русский язык — что реально есть

- **WaifuGemma4-26b-a4b-v1** ([hiwaifu-research](https://huggingface.co/hiwaifu-research/WaifuGemma4-26b-a4b-v1)) —
  главный кандидат: карточка помечает `ru`+`uk`, заявлено **55.3 % побед на русском** (2 959 боёв
  арены), RP/GRPO на Gemma-4-26B-A4B. GGUF: i1-IQ3_XXS 10.55, i1-IQ4_XS 12.96, Q4_K_M 15.64 ГБ.
  Рекомендованный сэмплинг: temp 1.0 / top-p 0.95 / top-k 64; non-thinking (`--reasoning-budget 0`).
  **Наш тест (i1-IQ3_XXS):** **96 %** чистых на карточном пресете (temp 1.0 / min-p 0.03) и ~**85 t/s** —
  самая быстрая из проверенных RP-моделей; но низкая T её **портит** (temp 0.4 и temp 0.7+DRY → 79 %).
- **Gryphe StyleTune** (12B/26B-A4B/31B) — обучается только `lm_head`, мультиязычность базы почти не
  портится; но в карточке `language: en`, и в тредах есть RU-регресс в thinking-режиме.
- **Гемма-эпоха «до Gemma 4»:** `Moraliane/SAINEMO-reMIX` 12B (Mistral) — единственная прямая похвала
  ру-юзеров («не подкидывает английские слова»), но отзывы 2024–2025.
- **Провал:** `secretmoon/YankaGPT-8B-v0.1` (на базе YandexGPT) — сообщество: «хуже, чем tuned NeMo 12B,
  путает сцену, повторяется».

## 4. HF-авторы RP-мержей: кто актуален

| Автор | Актуальность | Gemma 4 | Рекомендованный сэмплинг |
| --- | --- | --- | --- |
| **ReadyArt** | активен | scotoma-2, Melody1437, Serenity, Heimdallr, Dark-Scarlett | `top_p 0.92–0.95`, `temp 0.8–1.0`, без штрафов; Melody/For-Her: +`min_p 0.03` |
| **TheDrummer** | активен | Artemis-31B, Orion-26B-A4B | карточка без чисел; в тредах `temp 0.9–1.0`, `min_p 0.025` |
| **Gryphe** | активен | StyleTune 12B/26B/31B, Pantheon-Reasoning | `temp 1.0`, `min_p 0.05–0.10`, **DRY**; realtime: без repetition penalty |
| mradermacher / Lewdiculous | активны | — | это **квантёры**, не авторы |
| Sao10K, NeverSleep, ChaoticNeutrals, Undi95, Delta-Vector | мертвы в RP | нет | — |
| Смежные с Gemma 4: Ateron, Naphula (Goetia), Vortex5, Darkhn (Animus), zerofata (MeroMero), Nimbz (Gembrain), LatitudeGames (Equinox), AuriAetherwiing (Musica) | активны | да | — |

## 5. Насколько хороши на русском и от чего зависит

### 5.1. Метод модели и RU-свидетельства

| Модель | Метод (по карточке) | Язык | RU-свидетельство |
| --- | --- | --- | --- |
| **WaifuGemma4-26b-a4b-v1** | GRPO + LoRA r256, reward из 1.2M живых голосов | **17 языков, вкл. `ru`,`uk`** | Единственное: борды по 20 языкам, «в основном пишут по-испански и по-русски», **55.3 % побед на RU** |
| **Gemma-4-Dark-Thoughts-V2-31B** | 2-фазный `dare_ties`-мерж 4 англ. RP-моделей | `en` | **наш тест: 96–100 % чистых** (тот же IQ3_XXS); сообщество — лучший для не-англ. |
| Gryphe StyleTune 12/26/31B | обучается **только `lm_head`** (1 из 834 тензоров) | `en` | **наш тест 26B-A4B: 96–100 % чистых, 69 t/s**; автор: «все способности Gemma сохранены» |
| Gryphe Pantheon-Reasoning | **полный** тюн поверх StyleTune, трейсы от DeepSeek 3.2 | `en` | **RU-регресс в thinking:** `thought` на английском, ответ на русском |
| ReadyArt scotoma-2 | abliteration-LoRA + DPO | — | «в других языках это точно есть» (хеджирование) |
| zerofata G4-MeroMero-v2 | SFT→SLERP→GRPO | — | reward-стек содержит guard **«non-Latin characters, joined words»** |
| TheDrummer Artemis/Orion | finetune | нет тега | нет |
| **Split-Untied-31B** (наш) | 8-модельный мерж + StyleSwap с подменой `lm_head` | нет тега | **наш тест: 75 % чистых** (лечится temp0.4/грамматикой); 3 дискуссии про unstable thinking |
| google/gemma-4-31B-it | база | «140 языков» | RU в карточке не назван; ~1.7× токенов против английского |

### 5.2. Факторы (от чего зависит русский)

1. **Метод тюна — сильнейший сигнал.** Англоязычные RP-тюны помечены `language: en` либо без тега;
   WaifuGemma4 честно перечисляет 17 языков. Чем глубже англ. тюн, тем меньше языковой базы:
   StyleTune («минимум трогаем») vs Pantheon-Reasoning (полный тюн) — на втором зафиксирован RU-регресс.
2. **Thinking-канал — отдельный вектор утечки.** У Pantheon-RU `thought` полностью английский,
   а ответ русский → при обучении трейсы давал англоязычный DeepSeek. Гипотеза «thinking хуже для RU»
   подтверждена для Pantheon и **требует проверки** на нашем Split-Untied.
3. **Состав мержа.** В Split-Untied 8 англ. RP-доноров; мержащие авторы мультиязычность не измеряют —
   English-first пайплайн, русский не контролировался (структурный признак).
4. **Abliteration/heretic** оптимизируется по KL к **англоязычным** refusal-промптам → отказ на русском
   «протекает» первым (прямых RU-наблюдений нет).
5. **Квантизация бьёт по не-англ. сильнее** (arXiv 2608.09941 «Multilingual Quantization Tax»;
   EMNLP-2024). У WaifuGemma4 KLD: IQ3_M 0.146 против Q4_K_M 0.069, IQ2_M 0.400 → **наш IQ3_XXS
   и 25 % брака могут частично объясняться именно квантом**, а не только мержем.
6. **iMatrix-калибровка на мультиязычных текстах** (у WaifuGemma4 — на 10 языках) — рабочая заплатка.
7. **Токенизация кириллицы бедна** (Gemini-токенизатор 262k; ~1.7× токенов на русском) — больше мест
   для BPE-склеек, русский «срывается» первым при шуме в логитах.
8. **Сэмплинг.** Google: `T=1.0/top_p=0.95/top_k=64`; RP-авторы: `T≈1.0 + min_p 0.05 + DRY`.
   Влияние T на **язык** публично никто не обсуждает — наш результат (T↓ → брак↓) согласуется с тем,
   что дрейф языка = ошибка сэмплирования, но прямой цитаты нет.
9. **Язык обучающих данных** — единственный фактор с сильным RU-доказательством: только у WaifuGemma4
   русский был реальным распределением, а не тегом.

### 5.3. Как распознать «не умеет в русский» заранее (по карточке)

1. `language: en` или тег языка отсутствует при RP-тюне.
2. Нет ни одного упоминания не-англ. языков и нет multilingual-бенчмарка (C-Eval/C-MMLU и т.п.).
3. Метод трогает слои целиком (SFT/GRPO/full FT) вместо `lm_head`/узких проекций.
4. В донорах мержа есть abliteration/heretic-модели.
5. Данные — синтетика от англоязычных фронтир-моделей (M→F, «Character Engine»).
6. Нет imatrix-калибровки на мультиязычных текстах → на IQ2/IQ3 русский деградирует первым.

## 6. Не проверено / открытые вопросы

- Реальное качество русского ни у одной модели, кроме наших замеров, не измерялось.
- WaifuGemma4 на стенде **проверена** (96 % на карточке, ~85 t/s; низкая T портит) — см. §3 и
  `docs\quality\sampling-quality.md` §5.2.
- **На стенде осталось проверить (если понадобится):** (а) русский на Split-Untied при более высоком
  кванте (отделить вклад квантизации от мержа); (б) thinking vs non-thinking на одном Split-Untied
  (канал reasoning может утекать в английский); (в) StyleTune-26B как контроль: если RU на нём чище,
  причина в глубине мержа.
- Полный архив недельных мега-тредов не обходился — собраны последние 9 недель (см. §1.1).

## 7. Ateron: метод и другие мержи (разбор карточек, 2026-10-06)

**Кто это.** Ateron (`huggingface.co/Ateron`, орг `Blazed-Forge`) — автор Dark-Thoughts V2, нашей
лучшей «умной» русской RP-модели. Делает **только мержи** (никаких SFT/GRPO), на **форке mergekit
от Zerofata** («merges is an addiction» — форк под современные Gemma-4). Обновляется по фидбеку:
«V1 имела проблемы с tool calling и мозгами в длинном RP — починил в V2».

**Что характерно (по YAML из карточек):**
1. **Базовый якорь — всегда `gemma-4-it`**, `tokenizer_source: base`.
2. **Низкая `density` (0.15–0.60) + послойные веса** (свой вес на слои 4/9/…/59): у донора берётся
   только верхняя доля дельт, остальное — база. Это и есть механизм «мозги и язык базы сохраняются,
   характер донора проходит в прореженных слоях».
3. **Две–три фазы: креатив → форма.** Фаза 1 — характер (MeroMero, Dark-Scarlett, Glimmer,
   Gutenberg), фаза 2 — «ум»/полировка (Scotoma v2, Gemopus, Garnet). Методы: `dare_ties`, `ties`,
   `task_arithmetic`, `model_stock`.
4. **Scotoma v2 (ReadyArt) почти всегда** участвует — abliteration+DPO, «чинит Gemma-slop».
5. **`language: en` у всех** — русский не заявлен; он держится как побочный эффект осторожного мержа.

**Почему DTV2 держит русский, а MeroMero V2 в одиночку — нет (гипотеза, требует проверки).**
MeroMero V2 — тяжёлый SFT→SLERP→GRPO: распределение обостряется, мультиязычное подпространство
размывается. В DTV2 его дельты **прорежены (density 0.5)** и смешаны со вторым донором, а сверху
«отполированы» Scotoma → большая часть весов остаётся базой Gemma. Косвенно бьётся с нашим PPL:
DTV2 (мерж) = 66, Artemis (файнтюн) = 983 на одном кванте (`docs\research\why-ru-models.md` §3).

**Другие модели Ateron (Gemma-4):**

| Модель | Дата | Рецепт (кратко) | GGUF | Заметка |
| --- | --- | --- | --- | --- |
| **Dark-Thoughts V2 31B** | 13.08 | dare_ties MeroMero+DarkScarlett → dare_ties Scotoma+Dark-Mero | есть (mradermacher, наш) | эталон; см. §2 |
| **MoonGem 31B** | 04.09 | ties Glimmer+Gutenberg+Gemopus → task_arith Melinoe+MeroMero+Musica → MicroMix | bartowski | 7 родителей, «research» |
| **Dark-Thoughts V1 31B** | 07.08 | та же идея, проще веса | bartowski | V2 её «чинит» |
| **Novelist-Eclipse 31B** | 05.07 | dare_ties (union) + model_stock + StyleTune `lm_head` | bartowski | проза/описания |
| **Writers-31B-V2** | 4 дн. | dare_ties Writer-D/Writer-F/Scotoma, mlp-веса | пока нет | «Less Gemma — more human», фикс нестабильности |
| AssGuard 31B | 16.07 | — | ? | вероятно uncensored/ERP |
| Sketch-Cydonia / Predonia 24B | 2025–03.31 | Mistral-эра | частично | до Gemma-4 |

**Кандидаты на стенд (в порядке приоритета):** MoonGem-31B (другой рецепт, «research») и
Dark-Thoughts V1 (прямое сравнение «поумнела ли V2»); плюс контроль гипотезы — `G4-MeroMero-v2-31B-heretic`
в одиночку против DTV2. Проверять тем же RP-харнессом (`docs\quality\rp-quality-eval.md`).

Источник: карточки и raw-README моделей на HF (`huggingface.co/Ateron/<модель>/raw/main/README.md`),
список моделей — `huggingface.co/Ateron/models`, кванты — поиск HF по `Ateron` + `gguf`.

## 8. Топ мержей Gemma-4 (CaliperBench 2026-10-01 → разбор 2026-10-06)

Разбор дампа `downloads\caliperbench-2026-10-01.json` (590 моделей). Признак мержа — поле
`merge_parents` (список доноров); флаг `is_merge` ненадёжен (`is_finetune` стоит почти у всех).
CaliperBench **англоязычный, язык не измеряет** — это генератор кандидатов, вердикт даёт наш
RP-харнесс (`docs\quality\rp-quality-eval.md`). Жирным — есть GGUF под 16 ГБ (IQ3-класс).

| Модель (автор) | rp_v3¹ | Доноры (кратко) | GGUF | Теория² |
| --- | ---: | --- | --- | --- |
| Merotheon 31B (Casual-Autopsy) | **75.6** | base + Pantheon-Reasoning + MeroMero | ❌ нет | якорь, 3 |
| **Giftige-Blume-StyleSwap 31B** (Casual-Autopsy) | 75.4 | Giftige-Blume + StyleTune (StyleSwap `lm_head`) | ✅ mradermacher | lm_head |
| **Goetia 26B-A4B v1.6** (Naphula) | 72.0 | base + Orion-26B + Pantheon-26B + Boulesis | ✅ mradermacher | якорь, MoE |
| Harmonia 31B (virtuous7373) | 71.7 | base + Fabled + GarnetV2 + 3× heretic | ✅ mradermacher | 8 доноров |
| Prosopon 31B (Nimbz) | 71.1 | base + Pantheon + Gemopus + MeroMero-h. + Storymaxxed + Musica + Dark-Scarlett | ✅ Nimbz/mradermacher | 8 доноров |
| **MoonGem 31B** (Ateron) | 70.8 | Glimmer+Gutenberg+Gemopus+Melinoe+Musica+MeroMero-v2+Scotoma-v2 | ✅ bartowski | 7 доноров |
| **Glistening-Gem 31B v2.1** (sophosympatheia) | 70.2 | MeroMero-v2 + Artemis-v1 + Ortenzya-heretic + **base** | ✅ bartowski | якорь, 4 |
| Split-Untied 31B (Blazed-Forge) | 70.0 | (7) Scotoma…DTV2…Pantheon | ✅ mradermacher | уже тест: 75 % RU |
| **Schattenblume 31B** (Nimbz) | 69.6 | Scotoma-v2 + Giftige-Blume + MeroMero-v2 + **base** | ✅ mradermacher | якорь, 4 |
| Aura Prototype 26B-A4B (EldritchLabs) | 68.3 | Orion-26B + Adversary-26B + Pantheon-26B + fiction-26B | ✅ mradermacher | MoE |
| **Froopert 31B** (Nimbz) | 67.8 | Scotoma-v2 + Melinoe-h. + Dark-Scarlett-v2 + Serenity + Pantheon + base | ✅ bartowski | якорь, 6 |
| Boulesis 26B-A4B (SubMaroon) | 66.2 | heretic-26B + StyleTune-V2 + Pantheon-26B | ✅ mradermacher | MoE |
| *Dark-Thoughts V2 31B (наш эталон)* | *67.4* | *MeroMero-v2 + Dark-Scarlett → Scotoma* | *✅ есть* | *якорь, 2 фазы* |

¹ `rp_score_v3` (новый). ² «якорь» — в донорах есть сама `gemma-4-*-it`; число — сколько доноров.

**Как бьётся с теорией «отклонение от базы».** По донорам видно два лагеря:
- *Якорные с малым числом доноров* (Merotheon, Goetia, Glistening-Gem v2.1, Schattenblume, Froopert) —
  предсказание: русский и связность держат лучше всего; Goetia/Schattenblume повторяют «семью» DTV2.
- *Мульти-донорные (6–8)* (MoonGem, Prosopon, Harmonia, Sphinsikus) — креативнее, но риск по русскому выше.
- *StyleSwap/`lm_head`-прививка* (Giftige-Blume-StyleSwap) — предсказание: язык базы почти не тронут.

**Контр-аргумент, который надо помнить.** CaliperBench ставит Artemis-31B-v1.2 высоко (rp 73.7), а наш
русский RP-прогон показал у него деградацию в кашу (`docs\quality\rp-quality-eval.md` §5). То есть английский
лидерборд и русская связность расходятся — решать только нашим харнессом.

**Рекомендуемая первая волна (есть GGUF, разброс по методу):** Goetia-26B-A4B (быстрый MoE, якорный),
Glistening-Gem-31B-v2.1 (якорный), Schattenblume-31B (та же «семья», что DTV2), **Giftige-Blume-31B-v1
(Blazed-Forge, якорный, топ ERP)** и Giftige-Blume-StyleSwap-31B (StyleSwap) + контроль
`G4-MeroMero-v2-31B-heretic` в одиночку; затем MoonGem-31B как мульти-донорный. Ограничение StyleSwap
и уточнённое правило «что держит русский» — §9.

## 9. Что реально держит русский (проверка правила «годятся только Merge с базой»)

Срез **2026-10-06**. Разобраны: свежий CaliperBench V3+V2 (`downloads\CalibreV3.csv`, `CalibreV2.csv`;
парсер `bench\parse_caliper.py`), метаданные **176 HF-репо** Gemma-4 12/26/31B (`bench\fetch_hf_meta.py`,
классификатор — `bench\caliper_classify.py`) и **mergekit-рецепты** ключевых мержей (чтение карточек HF).

**Гипотеза «подходят только Merge, где есть base; чистый finetune или merge без base ломают русский» —
верна примерно на 80 %, но предиктор тоньше.** Русский держит не тип модели, а сохранность
головы/эмбеддингов и «мелкость» дельт:

1. У доноров **`embed_tokens`/`lm_head` занулены** в рецепте (Schattenblume, Giftige-Blume v1) → язык цел.
2. **Низкая `density` (0.15–0.60) + якорь на base** — метод Ateron (DTV2: `density 0.4–0.6`,
   `base_model: gemma-4-it`) → язык цел, **даже если base нет в HF-тегах**.
3. **Финтюн только по `lm_head`** (StyleTune) → язык цел.
4. **Обучение на русском** (WaifuGemma4, 17 языков) → язык цел.

Ломают: тяжёлые SFT/GRPO, глубокие мульти-донорные мержи, abliteration/heretic-heavy, битые repack.

| Модель | Тип | base в рецепте | Наш замер RU | Комментарий |
| --- | --- | --- | --- | --- |
| Schattenblume 31B | Merge | ✅ (+`embed/lm_head=0`) | 100 % | правило работает |
| Goetia 26B-A4B | Merge | ✅ | 100 % | работает |
| DTV2 31B | Merge | ✅ в YAML (`base_model: Gemma-4-it`) | 96–100 % | в HF-тегах base **нет** — тег врёт |
| Split-Untied 31B | Merge | ✅ | **75 %** | merge+base **не спас** |
| StyleTune-31B | Finetune | — | **17–0 %** | но это битый repack |
| StyleTune-V2 26B | Finetune (`lm_head`) | — | 96–100 % | финтюн удержал |
| Artemis-31B | Finetune | — | 92–96 % | удержал язык (но RP-каша) |
| WaifuGemma4 26B | Finetune (RU в данных) | — | 96 % | удержал |

**Практическое следствие:** HF-теги `base_model` **не показывают** base у Ateron (DTV2/MoonGem задают
`base_model` локальным путём в YAML) — по тегам фильтровать нельзя, **надо читать рецепт**.

### Шорт-лист «подходит» (non-thinking, свежий V3: Merge + якорь на base, без тяжёлого heretic)

| Модель | RP v3 | ERP v3 | base | Рецепт |
| --- | ---: | ---: | --- | --- |
| **Giftige-Blume 31B v1** (Blazed-Forge) | 74.7 | **67.7** | ✅ | 3 фазы; финал `della_linear` на `gemma-4-31B-it` (вес 0.70–0.75), у доноров `embed/lm_head=0` — **проверено** |
| Glistening-Gem 31B v2.1 | **78.6** | 64.4 | ✅ | проверено (base + MeroMero-v2/Artemis/Ortenzya) |
| Schattenblume 31B | 77.6 | 61.2 | ✅ | проверено (уже тест: RU 100 %) |
| Twisted Cyclone 31B | 73.3 | 65.9 | ✅ | по тегам (рецепт не читали) |
| Froopert 31B | 73.3 | 64.1 | ✅ | по тегам |
| Gembrain 31B | 69.7 | 66.3 | ✅ | по тегам (много доноров) |
| Gemsicle 31B | 69.7 | 63.7 | ✅ | по тегам |
| Split-Untied 31B | 74.3 | 66.6 | ✅ | **RU 75 %** — не приоритет |

**Ограничение StyleSwap:** `Giftige-Blume-31B-v1-StyleSwap` — это merge **без собственной base**
(`base_model = [Giftige-Blume-v1, StyleTune]`), прививающий тензоры **StyleTune, который и дал 17–0 %
на русском**. Оставлен как тест механизма, но приоритет ниже `Giftige-Blume-31B-v1`.

### Отсев (почему не берём)

- **Финтюны** (кроме `lm_head`-only / многоязычных): Artemis-31B (язык ок, RP-каша), Equinox-31B,
  Glimmer-RP, Gutenberg, Melinoe-VL, Sphinsikus-Chronist (это финтюн), Orion v1.1 (ERP 17), Melody1437
  (RP 23–37).
- **Heretic-heavy мержи:** Harmonia-31B (ERP 52.7), Goetia-v1.3-heretic, Gembrain-X-Core (18 доноров + H).
- **Мержи без своей base / прививка чужой головы (измерено):** `Giftige-Blume-StyleSwap` — русский
  3.3/2.6, англ. фразы в русском тексте («familiar bitter taste», «That kind of sadness»), ум/персонаж ~5 —
  ломает язык именно прививка головы StyleTune (ср. StyleTune-31B 17–0 %); `MeroMero-StyleSwap` (RP 37),
  `Isometry-RP` (RP 5.7).

Источники: CaliperBench V3/V2 (срез 2026-10-06, `downloads\CalibreV3.csv`); HF-метаданные и рецепты —
`huggingface.co` (карточки моделей); наши замеры — `docs\quality\sampling-quality.md`, `docs\research\why-ru-models.md`.

### ERP/DRP-специалисты и MoonGem (свежий V3, non-think, Gemma-4)

| Модель | ERP | DarkRP | RP | Combined | base | heretic |
| --- | ---: | ---: | ---: | ---: | :-: | :-: |
| **Giftige-Blume 31B v1** (наш чемпион) | 67.7 | **69.3** | 74.7 | **69.3** | ✅ | ⚠️ |
| Twisted Cyclone 31B (Cyclone-Labs) | 65.9 | 68.0 | 73.3 | 67.8 | ✅ | — |
| Gembrain-X 31B (Nimbz) | 61.8 | 68.5 | 74.3 | 67.4 | ✅ | ⚠️ |
| Sphinsikus-Chronist 31B (Blazed-Forge) | 65.6 | 67.4 | 73.7 | 67.8 | ❌ | — |
| Giftige-Blume 31B v2 (Nimbz) | 63.3 | 67.1 | 72.3 | 66.4 | ✅ | ⚠️ |
| Dark-Gemistry 31B (ReadyArt) | 67.8 | 58.8 | 67.0 | 62.9 | ❌ | — |
| Sprinkle-Vanilla 31B (peregrine) | 66.5 | 64.9 | 69.4 | 65.3 | ❌ | — |
| *MoonGem 31B (Ateron)* | *63.1* | *64.5* | *77.1* | *68.0* | *❌* | *—* |

**Вывод:** **Giftige-Blume-v1 — уже №1 по DarkRP и №2–3 по ERP среди всех Gemma-4**; выше по ERP только
StyleTune (68.5, но русский 17–0 %) и Dark-Gemistry (67.8, RP падает до 67). **Чистого апгрейда над ней
по ERP/DRP нет** — остальные кандидаты ниже по всем трём осям (сайдгрейды). **MoonGem — не ERP-игрок**,
а RP-специалист (RP 77.1, но ERP 63.1 / DarkRP 64.5 ниже DTV2).
Рычаги остаются только флейворные: «ум» в семье — Giftige-Blume v2; альтернативный чистый DRP — Twisted
Cyclone; DRP-экстрим — Gembrain-X (heretic, русский — лотерея).

## 10. База без файнтюна: base-31B vs heretic-31B (анализ, 2026-10-07)

**Контекст.** Базовая `Gemma-4-26B-A4B-it` на нашем харнессе идёт вровень с mid-tier мержами
(`docs\quality\base-models-rp-eval.md` §4.2: 3.28 у строгого судьи). Возник вопрос: не лучше ли «просто база» —
и, в частности, `unsloth/gemma-4-31B-it-GGUF` (штатная база 31B dense) и
`mradermacher/gemma-4-31B-it-heretic-GGUF` (расцензуренная/abliterated база 31B).

**Что это за модели.**
- `unsloth/gemma-4-31B-it-GGUF` — кванты **штатной инструкт-базы** 31B dense (30.7B, 60 слоёв,
  256K контекст). Ничего RP-специфичного. Под 16 ГБ: `UD-IQ3_XXS` 11.8 ГБ, `Q3_K_XL` 15.4 (в упор).
- `mradermacher/gemma-4-31B-it-heretic-GGUF` (исходник `coder3101/gemma-4-31B-it-heretic`) — **не тюн**,
  а abliteration той же базы: Heretic v1.2.0, Arbitrary-Rank Ablation (ARA) с row-norm preservation
  (слои 1–59, `preserve_good_behavior_weight 0.84`). Карточка: **KL 0.0434**, отказов **15/100**
  против **99/100** у базы, тег `language: en`. Есть imatrix-репо `...-heretic-i1-GGUF`
  (`i1-IQ3_XXS` 11.25 ГБ — та же полка, что у DTV2).

**Разбор трёх гипотез** (все — не проверены нашим стендом):
1. **«Крутой квант для 26B-A4B».** Влияние кванта на русский у нас первого порядка
   (`docs\research\why-ru-models.md` §3), но RP-качество MoE через `llama-perplexity` не снять. Ожидание — слабый
   плюс. Файл под 16 ГБ с запасом: `UD-IQ4_XS` 12.66 ГБ.
2. **«Просто база 31B».** Объективно сильнее 26B по бенчмаркам и **существенно по длинному контексту**
   (MRCR-128k: 66.4 % против 44.1 %), но dense → **~16.5 t/s без спекуляции, ~23 с MTP** против ~55
   у 26B-A4B. В 16 ГБ живёт на том же `IQ3_XXS`. Самый интересный открытый вопрос.
3. **«Расцензуренная (heretic)».** Слабейшая гипотеза. Отказ у базы Gemma — на вредных промптах, **не на
   RP/ERP** (наш же замер: в соблазне база *спешит согласиться*, а не отказывает). Abliteration
   RP-способностей не добавляет, зато правит веса (KL 0.0434), калиброван на англ. refusal-направлениях
   (риск для русского, `§5.2 п.4`, `§9`) и зажат квантом (Q3_K_S / i1-Q3_K_M).

**План проверки** (при разрешении пользователя; всё в `downloads/`): снять базу-31B и heretic-31B на
**одном** кванте `i1-IQ3_XXS`/`UD-IQ3_XXS` и прогнать RP-скрином (`bench\rp_quality.py`, 2 сцены,
nothink) с драфтом `gemma-4-31B-it-assistant.Q4_K_M.gguf`; лидера — полным набором. Отдельный тест
кванта — base-26B `UD-IQ3_XXS` vs `UD-IQ4_XS`. **Статус: не проверено** (2026-10-07, по решению
пользователя загрузки отложены).
