# Реестр проверенного (не повторять)

Единый список всего, что уже проверено в этом проекте, с вердиктом и ссылкой на детали. **Перед новым
исследованием — свериться здесь.** Обновляется при каждом новом замере.

Обозначения: ✅ оставляем/используем · ❌ проверено и отвергнуто · ⏸ помечено, но не измерялось на нашем стенде.

Стенд: RTX 4060 Ti 16 ГБ, Ryzen 7 5700X, 32 ГБ, Windows. Сборки: **b11382** (основная,
`downloads\llama-b11382-cu124`) и **b10472** (старая сборка, путь задаётся в `config.local.bat`). Все TG — на реалистичном
датасете `bench\requests_real.json`, если не сказано иное.

---

## 1. Спекулятивное декодирование

| Что проверяли | Вердикт | Детали |
| --- | --- | --- |
| `draft-mtp`, `nmax` 3/5/8, `pmin` 0.5/0.75 | ✅ `nmax5` (для кода 3), `pmin0.5≈0.75`. `nmax8` хуже | `speculation-research.md` §9, §12 |
| Приём `nmax8 pmin0.8` (GitHub #25198) | ❌ MoE −20…−27 %, dense +7 % | `speculation-research.md` §10.1 |
| `ngram-mod` сам по себе | ❌ слабее MTP везде | §11.2 |
| MTP + `ngram-mod` | ❌ не помогает (принятие падает) | §11.2 |
| MTP + `ngram-map-k4v` | ❌ нейтрально на RP | `tune_q36_rp_k4v.json` |
| `ngram-map-k4v` один | ❌ слабее | там же |
| DFlash nmax6 + ngram (Qwen3.6, код) | ✅ +18 % рефакторинг, +44 % новый код | §11.3; `qwen36-35b-a3b-dflash-code.bat` |
| DFlash nmax15 | ❌ слишком глубокий | §11.3 |
| DFlash + ngram на Gemma-26B | ❌ −17 % на реальном коде (⚠ GGUF мог быть с #29802) | `gemma-4-26b-a4b.md` |
| EAGLE-3 (Q4/Q8) | ❌ 1.4–3× медленнее MTP | §9.1 |
| DSpark (Q4/Q8) | ❌ медленнее | §9.2 |
| `draft-mtp-adaptive` (PR #27210) | ⏸ нет ни в одной сборке (open) | `docs\speculation-research.md` §12 |
| Синтетическая приёмка (`--spec-synth-*`) | ⏸ только бенчмаркинг | `docs\speculation-research.md` |
| `-bs` / `--spec-draft-p-split` / `--spec-draft-ngl` | ❌/шум (кроме `-ngld all` в DFlash-профилях) | §10.3 |
| Спекуляция на глубине контекста | ✅ принятие держится 72–80 %; TG падает с длиной | §11.5 |
| Общий MTP-assistant Gemma-4-31B на RP-мержах (Split-Untied, MeroMero v2 heretic) | ✅ работает, ×1.25…2.8; *untied* `lm_head` совместим | `gemma-4-31b-rp-merges.md` |

## 2. KV-кэш и контекст

| Что | Вердикт | Детали |
| --- | --- | --- |
| `q4_0` / `q8_0` / `q8_0 K + q4_0 V` | ✅ `q4_0` (быстрее на 10–16 %) | §11.1 |
| KV `f16`, `q4_1`, `q5_1` | ⏸ не мерили (community-приём под 73k) | `researched.md` §8 |
| `-ctxcp/-cms` (SWA-чекпоинты) | ✅ нужны Gemma-4 для многотирна; 16/512≈128/128 на аппендиксе | `context-infinite-chat.md` §1 |
| `--cache-ram`, `--cache-idle-slots` | ✅-нейтрально на аппендиксе; полезны для больших сессий | там же |
| `--context-shift` | ❌ гасится на Gemma-4/Qwen3.5 (M-RoPE/SWA) | `context-infinite-chat.md` §2 |
| `--cache-reuse` | ❌ `not supported by this context` | там же |
| Промпт > `-c` | ❌ HTTP 400 (сервер не обрезает) | там же |
| `--swa-full` | ❌ нет эффекта на Qwen; на 16 ГБ риск OOM | §10.3, `context-infinite-chat.md` |
| Контекст кратный 2048 (issue #23658) | ✅ наши `-c` уже кратны — в «хорошей» зоне | §12 / отчёт агента |
| Скорость на глубине (Qwen MTP) | 103 t/s @8k → 86 @32k → 73 @64k | §11.5 |
| `cache_prompt: true` в многотирне | ✅ PP 7397 → ~110 | §11.6 |

## 3. Батчи, потоки, загрузка

| Что | Вердикт | Детали |
| --- | --- | --- |
| `-ub` больше дефолта | ❌ только ест VRAM | `gemma-4-26b-a4b.md` |
| `-b/-ub` дефолты | ✅ | там же |
| `-t/-tb` | ❌ на TG не влияют (только CPU-часть) | логи |
| `--no-mmap` → `--load-mode none` | ✅ (в b11382 `--no-mmap` удалён) | §8 |
| `mmap`/`mlock` | ⏸ только время загрузки | — |

## 4. Прочие флаги сервера

| Что | Вердикт | Детали |
| --- | --- | --- |
| `-ncmoe`/`--n-cpu-moe` (выгрузка экспертов) | ❌ −32…−43 % (модель влезает) | §9, отчёт MoE-агента |
| `-np 2` (мультислот) | ❌ −15 %, контекст делится | `probe_q36_vision.json` |
| vision: `--no-mmproj-offload` (CPU) | ✅ бесплатно по TG | там же |
| vision: mmproj на GPU | ❌ −20 % | там же |
| `--poll 100`, `--no-repack` | ❌ шум | §10.3 |
| `--no-op-offload`, `-ot` | ⏸ не нужны (нет выгрузки) | отчёт MoE-агента |
| `--fit on`, `--fit-target` | ✅ дефолт; `--fit-target` не тюнили | — |
| `--reasoning off` / `--reasoning-budget` | ✅ для no-think RP и лимита | `gemma-4-26b-a4b.md` |

## 5. Температура и сэмплинг

| Что | Вердикт | Детали |
| --- | --- | --- |
| `temperature` 0.6–1.0 | ❌ на TG не влияет (±3 %), меняет лишь принятие | §10.2 |
| Понижение `temperature` на русском RP (1.0 → **0.4**) | ✅ брак падает с ~25 % до ~4 %; главный рычаг против англ. вставок и BPE-склеек. Ниже 0.4 смысла нет (0.3 — те же 96 %, но риск зацикливания) | `sampling-quality.md` §3.2 |
| `top-k` (40 и официальный 64) на русском | ❌ хуже: `top-k 40` — 71 % (серия 2); официальный Gemma-4 `top-k 64` — 75 % и единственный конфиг с реальными чужими алфавитами (серия 3) | `sampling-quality.md` §3, §3.2 |
| `min-p` 0.1 / инструкция «по-русски» на русском | ⏸/❌ `min-p 0.1` — 83 % (серия 2), но поверх `temp 0.4` ничего не меняет (96 %, серия 3); инструкция «по-русски» устойчивого эффекта не даёт (83 % против 96 %) | `sampling-quality.md` §3, §3.2 |
| DRY 0.8 (как на карточке) | ✅ не вредит (базовая линия); отдельный вклад в чистоту не выделен | `sampling-quality.md` §2 |
| `temp 0.7` + полный DRY (`base 1.75`, `allowed 2`, `penalty_last_n 256`) | ✅ 100 % чистых на DTV2 и StyleTune-26B — безопасная точка выше карточки (на DTV2 чище карточного temp 1.0: 100 против 96 %) | `sampling-quality.md` §5.5 |
| Рост `temperature` 0.4 → 0.85 (на «здоровой» модели) | ❌/⏸ лексическое разнообразие (TTR150) почти не растёт: 0.829→0.849 (DTV2), 0.844→0.850 (26B); при 0.85 уже артефакты (26B — 92 %) | `sampling-quality.md` §5.5 |
| StyleTune-31B `i1-IQ3_XXS` на русском | ❌ непригоден: массовые англ. инъекции в русские слова (17–0 % чистых); без явного `gemma4.jinja` — цикл `That That`. Те же `i1-IQ3_XXS` у DTV2/Split-Untied работают | `sampling-quality.md` §5.4 |
| `foreign_mass` (`n_probs`) как опережающий признак | ❌/⏸ вышел плоским нулём — не сработал, требует отладки | `sampling-quality.md` §3.2, §5 |
| Выбор модели для русского RP | ✅ **Dark Thoughts V2** (96–100 %), **StyleTune-V2 26B** (96–100 %), **WaifuGemma4 26B** (96 %), **Artemis-31B-v1.2** (92–96 %) держат русский; **Split-Untied** сыпется (75 % при том же IQ3_XXS). Самая быстрая — WaifuGemma4 (~85 t/s) | `sampling-quality.md` §5.2 |
| Низкая T на «здоровых» моделях (зависит от модели!) | ⚠️ Dark Thoughts/StyleTune — не портит; **WaifuGemma4** — портит (temp 0.4 и 0.7+DRY → 79 %, чисто только на карточке temp 1.0 = 96 %) | `sampling-quality.md` §5.2 |
| **Языковая верность ≠ «Чисто %»**: русский PPL | ✅ порядок величин на 31B dense: DTV2 `IQ3_XXS` **66** → тот же DTV2 `IQ2_S` **337** (вклад кванта ×5); Artemis `IQ3_XXS` **983** (англ. тюн ×15). Высокий «Чисто %» ещё не значит хорошее владение русским | `why-ru-models.md` §3 |
| `llama-perplexity` на Gemma-4-**26B-A4B** | ❌ инструмент врёт (25–80 тыс. при связном русском): вероятно, не создаётся `ctx_other` для MoE. PPL 26B-линии на этой сборке не снять | `why-ru-models.md` §3 |
| GBNF-грамматика «только кириллица/цифры/пунктуация» | ✅ детерминированный фикс: 100 % без потери скорости; цена — нет латиницы/эмодзи/кода | `sampling-quality.md` §5.3 |
| `logit_bias` −100 на англ. служебные токены | ❌ не помогает (79 %, токенизация обходит бан) | `sampling-quality.md` §5.3 |
| XTC 0.5/0.1 при `temp 0.7` | ❌ эффекта нет: TTR и чистота без изменений | `sampling-quality.md` §5.5 |
| dynatemp / mirostat / rep. penalty | ⏸ не измеряли | `context-infinite-chat.md` §6 |

## 6. Сборки и версии

| Что | Вердикт | Детали |
| --- | --- | --- |
| b10472 vs b11382 (реалистично) | ≈ ±5–11 %; берём b11382 | §12 |
| «+60 %» от сборки | ❌ это было на повторяющихся промптах | §8 vs §12 |
| b11382 vs релиз v0.5.0 | b11382 **новее** (b11146) | §12 |
| Регрессия принятия #29168 | ✅ нас не задела (модель без выгрузки) | `audit_mtp_b10472/11382.json` |

## 7. Клиент (SillyTavern) — из исследования, на стенде не запускалось

| Что | Вердикт | Детали |
| --- | --- | --- |
| Summarize: `Classic, blocking` | ✅ рекомендуется для llama.cpp; `Raw` — нет | `context-infinite-chat.md` §3 |
| Chat Vectorization | ❌ выключить (ломает кэш префикса) | там же |
| Smart Context | ❌ не поддерживается | там же |
| Memory Books / MessageSummarize | ⏸ клиентское «настоящее» окно | там же |
| constant-лорбук на Depth 3 | ⏸ сохранение характера | там же |
| `Context (tokens)` = промпт − ответ | ✅ `51000` в ST и `-c 51200` конфликтуют → 400 | там же |

## 8. Не проверено (кандидаты на будущее)

- Переконвертировать Gemma-DFlash драфт свежим конвертером (#29802) и перемерить.
- KV `q4_1`/`q5_1` (community-приём под 73k на 16 ГБ).
- Memory Books / MessageSummarize / KoboldCpp / форк M-RoPE shift — вживую.
- gpt-oss-20b + EAGLE-3-спекулятор как альтернативная RP-модель.
- XTC/dynatemp/mirostat — XTC проверен (эффекта нет, §5 `docs\sampling-quality.md`); dynatemp/mirostat вживую не измеряли.
- Многотирновое обеднение: TTR/повторы по всей длинной сессии (20+ ходов), а не по одному ответу.
- Мягкий `logit_bias` (−1.5…−2.5) по англ. якорям «с пробелом» против GBNF (полный −100 не сработал).
- Другой repack/квант StyleTune-31B и Artemis-31B-v1.2 (bartowski IQ3_XXS) на русском.
- `--fit-target`, `--no-host`, `-kvu/--kv-unified`, `--lookup-cache-static/dynamic`.
- Новые PR: #27210 (adaptive MTP), #27173 (draft chain), #28702 (FFN-фьюжн PP), #29807 (SSM-копии), #27248 (CUDA KV q4_1/…).
- **Мержи Ateron** (Gemma-4): MoonGem-31B, Writers-31B-V2, Novelist-Eclipse-31B, Dark-Thoughts V1 —
  проверить (bartowski GGUF есть для части). Контроль гипотезы «мерж лечит файнтюн»:
  `G4-MeroMero-v2-31B-heretic` в одиночку vs DTV2 (тот же донор). См. `docs\rp-model-candidates.md`.

## 9. Логи моделей (там все серии замеров)

- **Реестр моделей (протестированные + на будущее)** — `docs\models.md`
- `docs\swift-1.5-27b.md`, `docs\gemma-4-31b.md`, `docs\gemma-4-26b-a4b.md`, `docs\qwen36-35b-a3b.md`
- `docs\gemma-4-31b-rp-merges.md` (Split-Untied-31B, G4-MeroMero-v2-31B-heretic)
- `docs\base-models-rp-eval.md` (базовые instruct-модели на RP: Gemma-4-26B-A4B-it, Qwen3.6-35B-A3B, Qwen3.8-27B)
- Кросс-модельные: `docs\speculation-research.md`, `docs\context-infinite-chat.md`, `docs\why-ru-models.md`
- Сырые данные: `bench\runs\results.jsonl`, наборы — `bench\suites\` (`real_*`, `probe_*`, `tune_*`, `audit_*`)

## 10. Качество RP (LLM-судья) — 2026-10-06

Методика и результаты — `docs\rp-quality-eval.md`. Сценарии — `bench\quality\scenarios_rp.json`
(«мнимая история»: карточка + первое сообщение + ходы); 3 модели × think/non-think × 2 сценария ×
3 сида; судья — `gemma-4-26B-A4B-it-UD-IQ3_XXS` через `bench\quality\rp_judge.py`. Сырое —
`bench\quality\runs\rp_eval_*`, заключения судьи — `bench\quality\runs\rp_judge_b3\`.

| Что проверяли | Вердикт | Детали |
| --- | --- | --- |
| Artemis-31B-v1.2 (оба режима) на RP | ❌ речевая деградация в бессвязность (циклы «идиотская», «иерархия») при «Чисто %» 100 % | `rp-quality-eval.md` §5.1 |
| DTV2 Think vs NoThink на RP | ✅ Think чище (100 %) и лучше держит факты; NoThink — 83 %, редкая BPE-склейка `неgrом`, быстро сдаётся в соблазне | там же |
| StyleTune-26B на RP | ⚠️ язык/проза/скорость (66 t/s) хороши, но память/контекст слабее; в think утекает reasoning | там же §5, §7 |
| **Schattenblume-31B** (Nimbz) на RP | ✅ **4.55** (вровень с DTV2, Think 4.59 / No 4.52); RU 100 %; слабость — быстро сдаётся в соблазне, самоповторы описаний | `rp-quality-eval.md` §5.3 |
| **Goetia-26B-A4B-v1.6** (Naphula) на RP | ⚠️ **4.23**; быстрый MoE (~73 t/s), но путает сущности и шаблонит | там же §5.3 |
| Goetia-think в llama.cpp (`/completion`) | ❌ не закрывает `<channel|>` → ответ неотделим от reasoning; оценивали только non-think (см. StyleTune-think) | там же §7 |
| **Полный набор (6 сценариев)**: DTV2 vs Schattenblume | ✅ ничья подтверждена: **Schattenblume 4.47 · DTV2 4.39** (в think паритет 4.56/4.55); новые сцены просадили инициативу у обеих (3.0–3.4) | `rp-quality-eval.md` §5.4 |
| **Панель судей**: gemma-4-26B + Qwen3.6-35B (абсолют), space-bunny + deepseek-v4.1-flash (попарно) | ⚠️ вердикт зависит от метода: локальные абсолютные чуть за Schattenblume, оба облачных попарных — за DTV2 (~2:1); разница на грани | `rp-quality-eval.md` §5.5 |
| **Glistening-Gem-31B-v2.1** (полный набор, 2 судьи) | ✅ **NoThink вровень с лидерами**: Gemma 4.32 (Schattenblume 4.38 / DTV2 4.24), Qwen 3.35 (**выше обоих**); лучшая по памяти. Think сломан: 7/18 пустых ответов | `rp-quality-eval.md` §5.6 |
| **Giftige-Blume-StyleSwap-31B** (полный набор, 2 судьи) | ❌ русский 3.3 (Gemma) / 2.6 (Qwen) — англ. вставки (прививка головы StyleTune); для RU не берём | `rp-quality-eval.md` §5.6 |
| Судьи для RP: `gemma-4-26B-A4B` + `Qwen3.6-35B-A3B` MXFP4 | ✅ используем оба (поочерёдно), числа смотреть вместе (26B мягче ~4.4, Qwen строже ~3.3) | `rp-quality-eval.md` §5.6 |
| **Giftige-Blume-v1 31B** (Blazed-Forge) — замена StyleSwap | ✅ **№1 Caliper Combined/DarkRP**; наш RP NoThink: Gemma 4.33 (выше DTV2 4.24, ≈ Schattenblume 4.38) / Qwen **3.35 (#1)**; лучшая **инициатива (4.0)**; RU чистый (Cyr 99.9 %) | `rp-quality-eval.md` §5.7 |
| Giftige-Blume-v1: Think **без лимита** (`--reasoning-budget -1`) | ❌ не раскрывает: ответы той же длины, пустых 2/18 (было 4/18); Qwen 3.41 / Gemma 4.36 ≈ NoThink (3.35 / 4.33), повторы хуже (1.44) — бюджет не был узким местом | `rp-quality-eval.md` §5.7 |
| StyleTune-think: `--chat-template-file` без `enable_thinking` | ❌ модель не закрывает `<channel|>` → англ. план попадает в видимый ответ; харнесс теперь срезает по `<channel|>` | там же §7 |
| Нативный `/completion` + `--reasoning-budget` | ❌ бюджет не применяется (действует в chat-API) | там же §7 |
| **Базовые instruct-модели на RP** (Gemma-4-26B-A4B-it, Qwen3.6-35B-A3B, Qwen3.8-27B), скрин 2 сцены + полный набор (Gemma), оба судьи | ⚠️ Gemma-26B — лучшая из трёх и **пригодный baseline**: nothink 3.56 у строгого судьи на 2 сценах; **полный набор 3.28 (Qwen) — вровень со Schattenblume, выше DTV2**; Qwen3.6 (2.96) и Qwen3.8 (3.21) — на дне | `base-models-rp-eval.md` |
| think у базовых моделей (llama.cpp) | ❌ нестабилен у всех трёх: Gemma-26B — утечка reasoning в канал (видимый ок), Qwen3.6 — незакрытый ` thinking` → пустой ответ (2/6), Qwen3.8 — reasoning простым текстом («Чисто» 33 %) | `base-models-rp-eval.md` §1 |
| RP-файнтюн vs базовая instruct-модель | ⚠️ **не однозначно**: базовая Gemma-26B на полном наборе у строгого судьи вровень со Schattenblume (3.28) и выше DTV2 (3.11); базовые Qwen — на дне | `base-models-rp-eval.md` §4 |

## 11. Отбор кандидатов: CaliperBench + HF (2026-10-06)

Разобран свежий CaliperBench (V3+V2) — `downloads\CalibreV3.csv` / `CalibreV2.csv` (парсер
`bench\parse_caliper.py`); метаданные **176 HF-репо** Gemma-4 12/26/31B — `bench\fetch_hf_meta.py` +
`bench\caliper_classify.py`; прочитаны mergekit-рецепты ключевых мержей. Полный разбор и шорт-лист —
`rp-model-candidates.md` §9.

| Что проверяли | Вердикт | Детали |
| --- | --- | --- |
| Правило «русский держат только Merge с base» | ⚠️ эвристика ~80 %: держит не тип, а **сохранность головы/эмбеддингов и мелкость дельт** (`embed/lm_head=0` у доноров, `density` 0.15–0.6 + якорь на base, `lm_head`-only финтюн, RU в данных) | `rp-model-candidates.md` §9 |
| HF-теги `base_model` как фильтр | ❌ ненадёжны: у Ateron (DTV2/MoonGem) base задаётся в YAML и в тегах не значится — **читать рецепт** | там же |
| Свежий срез (06.10) vs дамп (01.10) | ⚠️ пересчёт v3 от 05.10 (literal errors) сильно сдвинул RP: DTV2 RPv3 67.4 → **77.5**, Artemis ERP 75.9 → **54.9** — старая колонка RP_v3 устарела | `caliperbench-2026-10.md`, `models.md` |
| Топ ERP среди 31B non-think | ✅ `StyleTune 31B` (68.5, но RU-провал) и **`Giftige-Blume 31B v1` Blazed-Forge (67.7, якорный)** | `models.md` «Кандидаты» |
| `Giftige-Blume-StyleSwap` | ⚠️ merge без своей base + прививка StyleTune (RU 17–0 %) — тест механизма, не приоритет по RU | `rp-model-candidates.md` §9 |
| Инструменты парсинга CaliperBench | ✅ `bench\parse_caliper.py`, `bench\fetch_hf_meta.py`, `bench\caliper_classify.py` | — |
