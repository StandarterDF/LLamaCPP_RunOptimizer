# RP-модели: внешний ресёрч (сообщество и HF), срез 2026-10-05

Сводка по итогам двух Space Bunny-агентов (Playwright по Reddit; fetch по Hugging Face).
Наши собственные замеры — в `docs\sampling-quality.md`. Здесь только **внешние** источники;
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
| Split-Untied 31B | Gemma-4-31B | — | ❌ «not suitable at all for languages other than English» | `docs\gemma-4-31b-rp-merges.md` |

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
  `docs\sampling-quality.md` §5.2.
- **На стенде осталось проверить (если понадобится):** (а) русский на Split-Untied при более высоком
  кванте (отделить вклад квантизации от мержа); (б) thinking vs non-thinking на одном Split-Untied
  (канал reasoning может утекать в английский); (в) StyleTune-26B как контроль: если RU на нём чище,
  причина в глубине мержа.
- Полный архив недельных мега-тредов не обходился — собраны последние 9 недель (см. §1.1).
