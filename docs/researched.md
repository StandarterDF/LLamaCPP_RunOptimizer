# Реестр проверенного (не повторять)

Единый список всего, что уже проверено в этом проекте, с вердиктом и ссылкой на детали. **Перед новым
исследованием — свериться здесь.** Обновляется при каждом новом замере.

Обозначения: ✅ оставляем/используем · ❌ проверено и отвергнуто · ⏸ помечено, но не измерялось на нашем стенде.

Стенд: RTX 4060 Ti 16 ГБ, Ryzen 7 5700X, 32 ГБ, Windows. Сборки: **b11382** (основная,
`downloads\llama-b11382-cu124`) и **b10472** (старая сборка, путь задаётся в `config.local.bat`). Все TG — на реалистичном
датасете [bench\requests_real.json](../bench/requests_real.json), если не сказано иное.

---

## 1. Спекулятивное декодирование

| Что проверяли | Вердикт | Детали |
| --- | --- | --- |
| `draft-mtp`, `nmax` 3/5/8, `pmin` 0.5/0.75 | ✅ `nmax5` (для кода 3), `pmin0.5≈0.75`. `nmax8` хуже | [docs\research\speculation-research.md](research/speculation-research.md) §9, §12 |
| Приём `nmax8 pmin0.8` (GitHub #25198) | ❌ MoE −20…−27 %, dense +7 % | [docs\research\speculation-research.md](research/speculation-research.md) §10.1 |
| `ngram-mod` сам по себе | ❌ слабее MTP везде | §11.2 |
| MTP + `ngram-mod` | ❌ не помогает (принятие падает) | §11.2 |
| MTP + `ngram-map-k4v` | ❌ нейтрально на RP | `tune_q36_rp_k4v.json` |
| `ngram-map-k4v` один | ❌ слабее | там же |
| DFlash nmax6 + ngram (Qwen3.6, код) | ✅ +18 % рефакторинг, +44 % новый код | §11.3; `qwen36-35b-a3b-dflash-code.bat` |
| DFlash nmax15 | ❌ слишком глубокий | §11.3 |
| DFlash + ngram на Gemma-26B | ❌ −17 % на реальном коде (⚠ GGUF мог быть с #29802) | [docs\models\gemma-4-26b-a4b.md](models/gemma-4-26b-a4b.md) |
| EAGLE-3 (Q4/Q8) | ❌ 1.4–3× медленнее MTP | §9.1 |
| DSpark (Q4/Q8) | ❌ медленнее | §9.2 |
| `draft-mtp-adaptive` (PR #27210) | ⏸ нет ни в одной сборке (open) | [docs\research\speculation-research.md](research/speculation-research.md) §12 |
| Синтетическая приёмка (`--spec-synth-*`) | ⏸ только бенчмаркинг | [docs\research\speculation-research.md](research/speculation-research.md) |
| `-bs` / `--spec-draft-p-split` / `--spec-draft-ngl` | ❌/шум (кроме `-ngld all` в DFlash-профилях) | §10.3 |
| Спекуляция на глубине контекста | ✅ принятие держится 72–80 %; TG падает с длиной | §11.5 |
| Общий MTP-assistant Gemma-4-31B на RP-мержах (Split-Untied, MeroMero v2 heretic) | ✅ работает, ×1.25…2.8; *untied* `lm_head` совместим | [docs\models\gemma-4-31b-rp-merges.md](models/gemma-4-31b-rp-merges.md) |
| MTP (NEO-MTP) на Qwen3.6-27B Fable-Fusion-711 (dense IQ2_M): RP vs код | ⚠️ **на RP вредит**: 13.5 t/s с MTP (принятие 68–85 %) против **17.8** без; на коде/математике **+6–13 %** (принятие 88–93 %); `nmax8` хуже (10–14). На RP-моделях проверять MTP отдельно | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.18; [bench\suites\real\real_qwen36_27b_fable.json](../bench/suites/real/real_qwen36_27b_fable.json) |

## 2. KV-кэш и контекст

| Что | Вердикт | Детали |
| --- | --- | --- |
| `q4_0` / `q8_0` / `q8_0 K + q4_0 V` — **качество** (Gemma-4 26B/31B) | ✅ разницы нет до 49k: NIAH идентичен (вплоть до потерянных игл), промпты-память 12k/20k и инструкции 12k прошли у всех типов, PPL в пределах шума; глитчи есть и на f16 | [docs\research\kv-cache-quantization.md](research/kv-cache-quantization.md) |
| KV `q4_0` vs `f16` — **скорость** и память | ⚠️ `f16 ≥ q4_0 > q8_0` — обратно прежней записи «q4_0 быстрее q8_0 на 10–16 %» (на 26B@48k: f16 50.6 vs q8 37.9 t/s); выигрыш `q4_0` — только память: 31B контекст ~26k → ~116k | там же |
| **Эмпирическая модель «VRAM → макс. контекст»** (формула + [bench\vram_model.py](../bench/vram_model.py)) | ✅ сходится с замерами: 31B dense q4_0 **~113k** (проект: ~116k), Qwen3.6-27B i1-IQ3_S **~125k**; накладные O: dense ~640 МиБ, MoE ~0. KV считается точно по архитектуре (SWA/hybrid) | [docs\research\context-memory-model.md](research/context-memory-model.md) |
| KV `f16`, `q4_1`, `q5_1`, `iq4_nl` вживую | ⏸ `f16` измерен; `q4_1`/`q5_1`/`iq4_nl` — только расчёт памяти | [bench\gguf_info.py](../bench/gguf_info.py) |
| KV-кэш: **внешние данные** (tool/JSON, код, KL-дивергенция) | ⚠️ `q8_0` **не** «универсально бесплатен»: KL у Gemma-4 0.108 (dense) / **0.377** (26B-A4B, MoE усиливает), у Qwen3.6 <0.04; под lossy-KV тихо страдают **tool/JSON (содержание, не синтаксис)** и **код (pass@1)**; первые токены — attention sinks; `K≠V` может отключить FlashAttention | [docs\research\kv-cache-external.md](research/kv-cache-external.md) |
| KV-кэш: **наша функциональная канарейка** (tool/JSON + код) | ✅ tool/JSON **12/12** у обеих моделей при f16/q8_0/q4_0 (инструменты с глубины 8k); 26B код 40/40 везде; у 31B **q4_0** — срыв формата (JS вместо Python) на 1 неоднозначной задаче: **33/40** против 36/40 (f16/q8_0), temp 0.7 | [docs\research\kv-cache-quantization.md](research/kv-cache-quantization.md) §4.3 |
| `-ctxcp/-cms` (SWA-чекпоинты) | ✅ нужны Gemma-4 для многотирна; 16/512≈128/128 на аппендиксе | [docs\research\context-infinite-chat.md](research/context-infinite-chat.md) §1 |
| `--cache-ram`, `--cache-idle-slots` | ✅-нейтрально на аппендиксе; полезны для больших сессий | там же |
| `--context-shift` | ❌ гасится на Gemma-4/Qwen3.5 (M-RoPE/SWA) | [docs\research\context-infinite-chat.md](research/context-infinite-chat.md) §2 |
| `--cache-reuse` | ❌ `not supported by this context` | там же |
| Промпт > `-c` | ❌ HTTP 400 (сервер не обрезает) | там же |
| `--swa-full` | ❌ нет эффекта на Qwen; на 16 ГБ риск OOM | §10.3, [docs\research\context-infinite-chat.md](research/context-infinite-chat.md) |
| Контекст кратный 2048 (issue #23658) | ✅ наши `-c` уже кратны — в «хорошей» зоне | §12 / отчёт агента |
| Скорость на глубине (Qwen MTP) | 103 t/s @8k → 86 @32k → 73 @64k | §11.5 |
| `cache_prompt: true` в многотирне | ✅ PP 7397 → ~110 | §11.6 |

## 3. Батчи, потоки, загрузка

| Что | Вердикт | Детали |
| --- | --- | --- |
| `-ub` больше дефолта | ❌ только ест VRAM | [docs\models\gemma-4-26b-a4b.md](models/gemma-4-26b-a4b.md) |
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
| `--reasoning off` / `--reasoning-budget` | ✅ для no-think RP и лимита | [docs\models\gemma-4-26b-a4b.md](models/gemma-4-26b-a4b.md) |

## 5. Температура и сэмплинг

| Что | Вердикт | Детали |
| --- | --- | --- |
| `temperature` 0.6–1.0 | ❌ на TG не влияет (±3 %), меняет лишь принятие | §10.2 |
| Понижение `temperature` на русском RP (1.0 → **0.4**) | ✅ брак падает с ~25 % до ~4 %; главный рычаг против англ. вставок и BPE-склеек. Ниже 0.4 смысла нет (0.3 — те же 96 %, но риск зацикливания) | [docs\quality\sampling-quality.md](quality/sampling-quality.md) §3.2 |
| `top-k` (40 и официальный 64) на русском | ❌ хуже: `top-k 40` — 71 % (серия 2); официальный Gemma-4 `top-k 64` — 75 % и единственный конфиг с реальными чужими алфавитами (серия 3) | [docs\quality\sampling-quality.md](quality/sampling-quality.md) §3, §3.2 |
| `min-p` 0.1 / инструкция «по-русски» на русском | ⏸/❌ `min-p 0.1` — 83 % (серия 2), но поверх `temp 0.4` ничего не меняет (96 %, серия 3); инструкция «по-русски» устойчивого эффекта не даёт (83 % против 96 %) | [docs\quality\sampling-quality.md](quality/sampling-quality.md) §3, §3.2 |
| DRY 0.8 (как на карточке) | ✅ не вредит (базовая линия); отдельный вклад в чистоту не выделен | [docs\quality\sampling-quality.md](quality/sampling-quality.md) §2 |
| `temp 0.7` + полный DRY (`base 1.75`, `allowed 2`, `penalty_last_n 256`) | ✅ 100 % чистых на DTV2 и StyleTune-26B — безопасная точка выше карточки (на DTV2 чище карточного temp 1.0: 100 против 96 %) | [docs\quality\sampling-quality.md](quality/sampling-quality.md) §5.5 |
| Рост `temperature` 0.4 → 0.85 (на «здоровой» модели) | ❌/⏸ лексическое разнообразие (TTR150) почти не растёт: 0.829→0.849 (DTV2), 0.844→0.850 (26B); при 0.85 уже артефакты (26B — 92 %) | [docs\quality\sampling-quality.md](quality/sampling-quality.md) §5.5 |
| StyleTune-31B `i1-IQ3_XXS` на русском | ❌ непригоден: массовые англ. инъекции в русские слова (17–0 % чистых); без явного `gemma4.jinja` — цикл `That That`. Те же `i1-IQ3_XXS` у DTV2/Split-Untied работают | [docs\quality\sampling-quality.md](quality/sampling-quality.md) §5.4 |
| `foreign_mass` (`n_probs`) как опережающий признак | ❌/⏸ вышел плоским нулём — не сработал, требует отладки | [docs\quality\sampling-quality.md](quality/sampling-quality.md) §3.2, §5 |
| Выбор модели для русского RP | ✅ **Dark Thoughts V2** (96–100 %), **StyleTune-V2 26B** (96–100 %), **WaifuGemma4 26B** (96 %), **Artemis-31B-v1.2** (92–96 %) держат русский; **Split-Untied** сыпется (75 % при том же IQ3_XXS). Самая быстрая — WaifuGemma4 (~85 t/s) | [docs\quality\sampling-quality.md](quality/sampling-quality.md) §5.2 |
| Низкая T на «здоровых» моделях (зависит от модели!) | ⚠️ Dark Thoughts/StyleTune — не портит; **WaifuGemma4** — портит (temp 0.4 и 0.7+DRY → 79 %, чисто только на карточке temp 1.0 = 96 %) | [docs\quality\sampling-quality.md](quality/sampling-quality.md) §5.2 |
| **Языковая верность ≠ «Чисто %»**: русский PPL | ✅ порядок величин на 31B dense: DTV2 `IQ3_XXS` **66** → тот же DTV2 `IQ2_S` **337** (вклад кванта ×5); Artemis `IQ3_XXS` **983** (англ. тюн ×15). Высокий «Чисто %» ещё не значит хорошее владение русским | [docs\research\why-ru-models.md](research/why-ru-models.md) §3 |
| `llama-perplexity` на Gemma-4-**26B-A4B** | ❌ инструмент врёт (25–80 тыс. при связном русском): вероятно, не создаётся `ctx_other` для MoE. PPL 26B-линии на этой сборке не снять | [docs\research\why-ru-models.md](research/why-ru-models.md) §3 |
| GBNF-грамматика «только кириллица/цифры/пунктуация» | ✅ детерминированный фикс: 100 % без потери скорости; цена — нет латиницы/эмодзи/кода | [docs\quality\sampling-quality.md](quality/sampling-quality.md) §5.3 |
| `logit_bias` −100 на англ. служебные токены | ❌ не помогает (79 %, токенизация обходит бан) | [docs\quality\sampling-quality.md](quality/sampling-quality.md) §5.3 |
| XTC 0.5/0.1 при `temp 0.7` | ❌ эффекта нет: TTR и чистота без изменений | [docs\quality\sampling-quality.md](quality/sampling-quality.md) §5.5 |
| dynatemp / mirostat / rep. penalty | ⏸ не измеряли | [docs\research\context-infinite-chat.md](research/context-infinite-chat.md) §6 |
| Сэмплинг автора для не-thinking (`temp 0.7 / top_p 0.8 / top_k 20 / min_p 0 / presence_penalty 1.5`) vs наш RU-safe, на Qwen3.6-27B Fable | ⚠️ меняет **профиль, а не потолок**: панель 3.30 против 3.46; TTR 0.878→0.933, голос/повторы лучше, но ответы короче и ниже «ум/инициатива» | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.18 |

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
| Summarize: `Classic, blocking` | ✅ рекомендуется для llama.cpp; `Raw` — нет | [docs\research\context-infinite-chat.md](research/context-infinite-chat.md) §3 |
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
- XTC/dynatemp/mirostat — XTC проверен (эффекта нет, §5 [docs\quality\sampling-quality.md](quality/sampling-quality.md)); dynatemp/mirostat вживую не измеряли.
- Многотирновое обеднение: TTR/повторы по всей длинной сессии (20+ ходов), а не по одному ответу.
- Мягкий `logit_bias` (−1.5…−2.5) по англ. якорям «с пробелом» против GBNF (полный −100 не сработал).
- Другой repack/квант StyleTune-31B и Artemis-31B-v1.2 (bartowski IQ3_XXS) на русском.
- `--fit-target`, `--no-host`, `-kvu/--kv-unified`, `--lookup-cache-static/dynamic`.
- Новые PR: #27210 (adaptive MTP), #27173 (draft chain), #28702 (FFN-фьюжн PP), #29807 (SSM-копии), #27248 (CUDA KV q4_1/…).
- **Мержи Ateron** (Gemma-4): MoonGem-31B, Writers-31B-V2, Novelist-Eclipse-31B, Dark-Thoughts V1 —
  проверить (bartowski GGUF есть для части). Контроль гипотезы «мерж лечит файнтюн»:
  `G4-MeroMero-v2-31B-heretic` в одиночку vs DTV2 (тот же донор). См. [docs\research\rp-model-candidates.md](research/rp-model-candidates.md).
- **«База без файнтюна» (RP-скрин проверен, 2026-10-07):** штатная база 31B
  (`unsloth/gemma-4-31B-it-GGUF`, `UD-IQ3_XXS`) — §10; abliteration того же размера
  (`gemma-4-31b-it-heretic-ARA`, `i1-IQ3_XXS`) — §10. Вывод: **base-31B ≈ heretic-31B** (abliteration
  RP не меняет), обе — baseline. Не мерили: квант base-26B `IQ4_XS` vs `IQ3_XXS`, PPL/скорость base-31B.
  План — [docs\research\rp-model-candidates.md](research/rp-model-candidates.md) §10.
- **RP вне Gemma — Qwen 3.5/3.6/3.8, Mistral, альтернативы (внешний ресёрч, 2026-10-07):** майнинг
  CaliperBench V3 + HF. Qwen3.8-27B-**финтюны** (ReadyArt Serenity/Dark-Scarlett/Heimdallr, ukisai Swift,
  allura-org Anko, darkc0de RICO) и **MoE 35B-A3B** (Anansi, Genesis Hermes V7) образуют новый пул
  кандидатов RP v3 70–78 (§§1–2); Mistral/Ministral по англ. Caliper слабее (≤67), альтернатива —
  Nemotron 3.5 (62). **Отдельная находка — русскоязычный RP-ниш на Mistral** (§2.5): limloop
  Runeweaver/Hydra-RP-RU 12B, Aleteian Pathfinder-RP-12B-RU (анкор Saiga), Naphula Slimaki-Tavern-24B,
  katafiek Katarau-9B-ru-RP (Qwen3.5-9B) — `ru` в языке, обучались на русском. Ни один не проверен нашим
  харнессом. **Swift 1.5 27B (уже был на диске) — скрин сделан: ❌ не RP-модель** (3.42 Gemma / 2.77 Qwen,
  персонаж 2.2 · инициатива 1.9) — он efficient-reasoning, не RP-тюн; вердикт о классе Qwen3.8-RP-финтюнов
  (ReadyArt и др.) им **не закрывается** (§10). Детали, механика RU и план волны —
  [docs\research\qwen-mistral-rp-candidates.md](research/qwen-mistral-rp-candidates.md).

## 9. Логи моделей (там все серии замеров)

- **Реестр моделей (протестированные + на будущее)** — [docs\models.md](models.md)
- [docs\models\swift-1.5-27b.md](models/swift-1.5-27b.md), [docs\models\gemma-4-31b.md](models/gemma-4-31b.md), [docs\models\gemma-4-26b-a4b.md](models/gemma-4-26b-a4b.md), [docs\models\qwen36-35b-a3b.md](models/qwen36-35b-a3b.md)
- [docs\models\gemma-4-31b-rp-merges.md](models/gemma-4-31b-rp-merges.md) (Split-Untied-31B, G4-MeroMero-v2-31B-heretic)
- [docs\quality\base-models-rp-eval.md](quality/base-models-rp-eval.md) (базовые instruct-модели на RP: Gemma-4-26B-A4B-it, Qwen3.6-35B-A3B, Qwen3.8-27B)
- Кросс-модельные: [docs\research\speculation-research.md](research/speculation-research.md), [docs\research\context-infinite-chat.md](research/context-infinite-chat.md), [docs\research\why-ru-models.md](research/why-ru-models.md)
- RP-кандидаты вне Gemma (Qwen 3.5/3.6/3.8, Mistral, альтернативы) — [docs\research\qwen-mistral-rp-candidates.md](research/qwen-mistral-rp-candidates.md)
- Сырые данные: [bench\runs\results.jsonl](../bench/runs/results.jsonl), наборы — [bench\suites](../bench/suites) (`real\`, `probe\`, `tune\`, `audit\`, `spec\`, `once\`)

## 10. Качество RP (LLM-судья) — 2026-10-06

Методика и результаты — [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md). Сценарии — [bench\quality\prompts\scenarios_rp.json](../bench/quality/prompts/scenarios_rp.json)
(«мнимая история»: карточка + первое сообщение + ходы); think/non-think × 2 сценария × 3 сида.
**С 2026-10-08 штатная панель — 4 судьи**: локальные `gemma-4-26B-A4B` и `Qwen3.6-35B-A3B` MXFP4
([bench\quality\rp_judge.py](../bench/quality/rp_judge.py)) + облачные DeepSeek-Flash и DeepSeek-Pro ([bench\quality\api_judge.py](../bench/quality/api_judge.py));
в более старых строках — 1–2 судьи, шкалы между строками не сравнивать. Сырое —
`bench\quality\runs\rp_eval_*`, заключения судей — `bench\quality\runs\rp_judge_*`.

| Что проверяли | Вердикт | Детали |
| --- | --- | --- |
| Artemis-31B-v1.2 (оба режима) на RP | ❌ речевая деградация в бессвязность (циклы «идиотская», «иерархия») при «Чисто %» 100 % | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.1 |
| DTV2 Think vs NoThink на RP | ✅ Think чище (100 %) и лучше держит факты; NoThink — 83 %, редкая BPE-склейка `неgrом`, быстро сдаётся в соблазне | там же |
| StyleTune-26B на RP | ⚠️ язык/проза/скорость (66 t/s) хороши, но память/контекст слабее; в think утекает reasoning | там же §5, §7 |
| **Schattenblume-31B** (Nimbz) на RP | ✅ **4.55** (вровень с DTV2, Think 4.59 / No 4.52); RU 100 %; слабость — быстро сдаётся в соблазне, самоповторы описаний | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.3 |
| **Goetia-26B-A4B-v1.6** (Naphula) на RP | ⚠️ **4.23**; быстрый MoE (~73 t/s), но путает сущности и шаблонит | там же §5.3 |
| Goetia-think в llama.cpp (`/completion`) | ❌ не закрывает `<channel|>` → ответ неотделим от reasoning; оценивали только non-think (см. StyleTune-think) | там же §7 |
| **Полный набор (6 сценариев)**: DTV2 vs Schattenblume | ✅ ничья подтверждена: **Schattenblume 4.47 · DTV2 4.39** (в think паритет 4.56/4.55); новые сцены просадили инициативу у обеих (3.0–3.4) | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.4 |
| **Панель судей**: gemma-4-26B + Qwen3.6-35B (абсолют), space-bunny + deepseek-v4.1-flash (попарно) | ⚠️ вердикт зависит от метода: локальные абсолютные чуть за Schattenblume, оба облачных попарных — за DTV2 (~2:1); разница на грани | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.5 |
| **Glistening-Gem-31B-v2.1** (полный набор, 2 судьи) | ✅ **NoThink вровень с лидерами**: Gemma 4.32 (Schattenblume 4.38 / DTV2 4.24), Qwen 3.35 (**выше обоих**); лучшая по памяти. Think сломан: 7/18 пустых ответов | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.6 |
| **Giftige-Blume-StyleSwap-31B** (полный набор, 2 судьи) | ❌ русский 3.3 (Gemma) / 2.6 (Qwen) — англ. вставки (прививка головы StyleTune); для RU не берём | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.6 |
| Судьи для RP: `gemma-4-26B-A4B` + `Qwen3.6-35B-A3B` MXFP4 | ✅ используем оба (поочерёдно), числа смотреть вместе (26B мягче ~4.4, Qwen строже ~3.3) | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.6 |
| **Giftige-Blume-v1 31B** (Blazed-Forge) — замена StyleSwap | ✅ **№1 Caliper Combined/DarkRP**; наш RP NoThink: Gemma 4.33 (выше DTV2 4.24, ≈ Schattenblume 4.38) / Qwen **3.35 (#1)**; лучшая **инициатива (4.0)**; RU чистый (Cyr 99.9 %) | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.7 |
| Giftige-Blume-v1: Think **без лимита** (`--reasoning-budget -1`) | ❌ не раскрывает: ответы той же длины, пустых 2/18 (было 4/18); Qwen 3.41 / Gemma 4.36 ≈ NoThink (3.35 / 4.33), повторы хуже (1.44) — бюджет не был узким местом | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.7 |
| StyleTune-think: `--chat-template-file` без `enable_thinking` | ❌ модель не закрывает `<channel|>` → англ. план попадает в видимый ответ; харнесс теперь срезает по `<channel|>` | там же §7 |
| Нативный `/completion` + `--reasoning-budget` | ❌ бюджет не применяется (действует в chat-API) | там же §7 |
| **Базовые instruct-модели на RP** (Gemma-4-26B-A4B-it, Qwen3.6-35B-A3B, Qwen3.8-27B), скрин 2 сцены + полный набор (Gemma), оба судьи | ⚠️ Gemma-26B — лучшая из трёх и **пригодный baseline**: nothink 3.56 у строгого судьи на 2 сценах; **полный набор 3.28 (Qwen) — вровень со Schattenblume, выше DTV2**; Qwen3.6 (2.96) и Qwen3.8 (3.21) — на дне | [docs\quality\base-models-rp-eval.md](quality/base-models-rp-eval.md) |
| think у базовых моделей (llama.cpp) | ❌ нестабилен у всех трёх: Gemma-26B — утечка reasoning в канал (видимый ок), Qwen3.6 — незакрытый ` thinking` → пустой ответ (2/6), Qwen3.8 — reasoning простым текстом («Чисто» 33 %) | [docs\quality\base-models-rp-eval.md](quality/base-models-rp-eval.md) §1 |
| RP-файнтюн vs базовая instruct-модель | ⚠️ **не однозначно**: базовая Gemma-26B на полном наборе у строгого судьи вровень со Schattenblume (3.28) и выше DTV2 (3.11); базовые Qwen — на дне | [docs\quality\base-models-rp-eval.md](quality/base-models-rp-eval.md) §4 |
| **Gemma-4-31B-it heretic-ARA** (база + ARA-abliteration), скрин 2 сцены, 2 судьи | ⚠️ **середина, не апгрейд**: 4.44 (Gemma: Think 4.52 / No 4.35) · 3.52 (Qwen: 3.58 / 3.46); память фактов отличная, но голос персонажа слабый (**«fast-track» в соблазне**, литературщина/опечатки в think); **think рабочий**; abliteration RP-способностей не добавляет | [docs\quality\base-models-rp-eval.md](quality/base-models-rp-eval.md) §4.3 |
| **Gemma-4-31B-it (штатная база, без тюна/abliteration)**, скрин 2 сцены, 2 судьи | ⚠️ **baseline, не рабочая RP-модель**: 4.51 (Gemma, родств. судья: No 4.60 / Think 4.38) · 3.45 (Qwen: No 3.38 / Think 3.52); **≈ heretic-ARA** (abliteration RP не меняет); **think рабочий** (6/6 непустых); у строгого судьи персонаж 2.5–2.8, инициатива 2.5–2.7, паттерн-циклы; Чисто 100 %, TG 18.5/18.8 t/s | [docs\quality\base-models-rp-eval.md](quality/base-models-rp-eval.md) §4.4 |
| **Swift-1.5-Qwen3.8-27B** (ukisai), скрин 2 сцены, 2 судьи — **первый не-Gemma** | ❌ **не RP-модель** (efficient-reasoning/кодинг-тюн): 3.42 (Gemma: No 3.85 / Think 2.98) · **2.77** (Qwen: No 2.56 / Think 2.98); персонаж 2.2 · инициатива 1.9 · проза 3.3; память 3.6, рус 4.2; RU 100 % (No) / 83 % (Think, повтор), TG 22.8/30.8 t/s; ниже всех Gemma-RP и базовых Qwen | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.11 |
| **Genesis Hermes V7 35B-A3B** (mradermacher i1-IQ4_XS), скрин 2 сцены, **nothink**, 2 судьи | ❌ **не апгрейд** (Caliper RP 72.4 не подтвердился): **3.81** (gemma) · **2.90** (Qwen, **ниже базы** Qwen3.6 2.96 / Qwen3.8 3.21 / Gemma-26B 3.28); персонаж 2.0–2.7 · инициатива 2.0–3.3 · память 2.7–3.3; RU 100 %, TG 41.6 t/s (MoE, IQ4_XS>16 ГБ → offload, без MTP) | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.12 |
| **G4-MeroMero-26B-A4B-it-uncensored-heretic** (llmfan46/mradermacher i1-IQ4_XS, MoE), скрин 2 сцены, 2 судьи | ❌ **не апгрейд** (Caliper RP 76.6 не подтвердился): **4.46** (gemma) · **3.15** (Qwen, ниже базы Gemma-26B 3.56 и лидеров 3.28–3.35); повторы (1.67) · память-ловушка «Питер» (2/3 сида приняли ложную посылку) · инициатива 2.5 (пассивна в соблазне); RU **100 %**, TG 62 t/s; **think сломан** (Чисто 17 %, утечка reasoning) | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.13 |
| **Dans-PersonalityEngine-V1.3.0-24b** (PocketDoc, база Mistral-Small-3.1, IQ4_XS), скрин 2 сцены, **nothink**, 2 судьи | ⚠️ **русский держит (100 %), но не character-RP**: **3.94** (gemma) · **2.54** (Qwen, **самый низкий**); персонаж 1.5, «быстрое согласие» (подтверждает ложный факт «я с Питера», идёт домой); RU 100 % вопреки `en` в карточке; TG 18.9 t/s (dense); годится как чат-компаньон | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.14 |
| **Boulesis-v2.1-26B-A4B** (SubMaroon / mradermacher i1-IQ4_XS, MoE), скрин 2 сцены, оба режима, **панель 4 судей** (gemma/Qwen/DS-Flash/DS-Pro) | ⚠️ **#2 среди 26B-мёржей на скрине** (в `rp-ranking.md`: **No #8 · Think #10**): **3.67** панель (No 3.74 · Think 3.60); локально gemma 4.48 / Qwen 3.56 (No) — выше Goetia 4.23, MeroMero 4.46/3.15, heretic-ARA 3.52; в панели выше MeroMero 3.70 и всех 31B-лидеров (3.51–3.59), но ниже StyleTune 3.78. RU **100 %**, TG 55 t/s. Минусы: литературщина/клише, «мысли в кавычках», 4 абзаца вместо 2–3, ошибка памяти («не бросала скрипку»), инициатива 2.0–2.67 у строгих судей; **NoThink лучше think**, в think течёт черновик-разметка (Чисто 83 %); полный набор (6 сцен) не гоняли | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.16 |
| **Kitchoon-26B-A4B** (SubMaroon / mradermacher i1-IQ4_XS, MoE; линия gemma-4-26B-it → Pantheon-Reasoning → Vortex5-heretic), скрин 2 сцены, оба режима, **панель 4 судей** | ❌ **не апгрейд, слабейший из 26B-мёржей**: панель **2.72** (No **3.25** · Think **2.09**); локально gemma 3.88 / Qwen **3.17** (No) — ниже базы Gemma-26B (3.56) и Boulesis (3.74). Провал **памяти (2.25)** — 3/3 сида приняли ложную «Питер» (Кира из Твери); характер смягчён, шаблоны («Винил — это аргумент»), BPE-склейка `дождrains`; RU 83 % (No), TG 55 t/s; **think непригоден** (Чисто 0 %, англ. reasoning утекает в видимый ответ). В `rp-ranking.md` не внесён (в «Не берём») | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.17 |
| **Qwen3.6-27B Fable-Fusion-711** (DavidAU heretic NEO-MAX, dense, IQ2_M **11.3 ГБ**, встроенная MTP), скрин 2 сцены, оба режима, **панель 4 судей** | ⚠️ **середина, не апгрейд**: панель **3.46** (No **3.46** · Think **3.45**); локально gemma 4.06 / Qwen 3.10 (No, родств. база) — ниже Gemma-лидеров (StyleTune 3.78, Boulesis 3.74) и 31B-ядра (3.51–3.59). **Русский — лучшая ось**: Чисто/Cyr 100 %, язык 4.1–4.4, память `school` 3.9; слабые — персонаж **2.96** (сглаживает характер), инициатива **3.0** (пассивна: отказ + повтор), повторы **2.7** (однотипные реплики между сидами), POV-ошибки; **think дублирует ответ** (прироста нет). В `rp-ranking.md`: **No #19 · Think #12** | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.18 |
| **Qwen3.6-27B Fable-Fusion-711 i1-IQ3_S** (mradermacher i1, imatrix, 11.7 ГиБ), скрин 2 сцены, оба режима, **панель 4 судей**, **без спец.** | ⚠️→✅ **лучше IQ2_M**: панель **3.63** (No 3.47 · Think **3.79**); весь прирост в **think** (3.45 → 3.79), nothink без изменений. **Квант важнее MTP**: imatrix-IQ3_S лечит дублирование think. В `rp-ranking.md` **No #19 · Think #7** (лучший think среди не-Gemma). Слабые оси прежние (персонаж 2.9, инициатива 2.8); русский/память сильные. ~18 t/s, контекст q4_0 ~125k | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.19 |
| **Kitchoon-V2-26B-A4B** (SubMaroon, официальный gated Q6_K 23.2 ГБ; мерж heretic + StyleTune-V2 + Pantheon-V2 — **не** v1), скрин 2 сцены, оба режима, **панель 4 судей** | ✅→⚠️ **заметный апгрейд над v1 (§5.17: 2.72), но середина 26B-мёржей**: панель **3.62** (No **3.67** · Think 3.58). Локально gemma 4.48/4.19 · Qwen 3.02/3.83 · DS-Flash 3.40/3.04 · DS-Pro 3.77/3.25. В `rp-ranking.md` **No #12 · Think #12**. Русский лучший (Чисто/Cyr 100 %), память восстановлена (3.25 vs v1 2.25); минусы — смягчение характера (Ева сама первой идёт домой), петли жестов между сидами, выдуманный реквизит (полотенце, «чужой» кот, «Маринка»). **Q6_K 23.2 ГБ не влезает в 16 ГБ** → авто-офлоуд экспертов (`--fit on`), TG 26.5/23.1 t/s, загрузка ~6.4 мин; **think не думает** (канал `<channel|>` закрывается мгновенно, ≈ non-think) | [docs\quality\rp-quality-eval.md](quality/rp-quality-eval.md) §5.20 |
| **Облако: DeepSeek (V4.1-Flash/Pro) + GLM 4.5–5.3** (12 моделей), скрин 2 сцены, **4 судьи** (Gemma/Qwen/DS-Flash/DS-Pro) | ✅ **верхний референс**: Gemma 4.06–4.73 (все выше локальных мержей 4.24–4.38); лидеры GLM-5.3 4.73, DeepSeek-Pro 4.71; **судьи расходятся сильно**; **DeepSeek-строки — self-eval** (DS-Flash ставит себя №1); `glm-5.3`/`glm-5.3-flash` форсированный thinking течёт **CJK** в русский (Чисто 67–83 %), остальные 100 %; не локально, reasoning-модели | [docs\quality\cloud-api-rp-eval.md](quality/cloud-api-rp-eval.md); [bench\quality\api_rp_eval.py](../bench/quality/api_rp_eval.py), `api_judge.py` |
| **Английский скрин: EN vs RU** (6 моделей, 2 сцены, nothink/think, 4 судьи — Gemma/Qwen/DS-Flash/DS-Pro, всё через роутер :9931) | ⚠️ **«в EN кардинально умнее» на баллах НЕ подтвердилось**: Δ(EN−RU) = Gemma **+0.46**, DS-Pro **+0.39**, DS-Flash **+0.13**, Qwen **−0.23** (средний ≈ +0.2 — меньше разброса судей). Реальное отличие — **язык/канал**: в EN 0 кириллицы во всех 66 ответах и **think у Gemma-31B-мержей работает** (в RU ломался); ум/память/персонаж близки | [docs\quality\en-rp-eval.md](quality/en-rp-eval.md); [bench\quality\router_eval.py](../bench/quality/router_eval.py) |

## 11. Отбор кандидатов: CaliperBench + HF (2026-10-06)

Разобран свежий CaliperBench (V3+V2) — `downloads\CalibreV3.csv` / `CalibreV2.csv` (парсер
[bench\parse_caliper.py](../bench/parse_caliper.py)); метаданные **176 HF-репо** Gemma-4 12/26/31B — [bench\fetch_hf_meta.py](../bench/fetch_hf_meta.py) +
[bench\caliper_classify.py](../bench/caliper_classify.py); прочитаны mergekit-рецепты ключевых мержей. Полный разбор и шорт-лист —
[docs\research\rp-model-candidates.md](research/rp-model-candidates.md) §9.

| Что проверяли | Вердикт | Детали |
| --- | --- | --- |
| Правило «русский держат только Merge с base» | ⚠️ эвристика ~80 %: держит не тип, а **сохранность головы/эмбеддингов и мелкость дельт** (`embed/lm_head=0` у доноров, `density` 0.15–0.6 + якорь на base, `lm_head`-only финтюн, RU в данных) | [docs\research\rp-model-candidates.md](research/rp-model-candidates.md) §9 |
| HF-теги `base_model` как фильтр | ❌ ненадёжны: у Ateron (DTV2/MoonGem) base задаётся в YAML и в тегах не значится — **читать рецепт** | там же |
| Свежий срез (06.10) vs дамп (01.10) | ⚠️ пересчёт v3 от 05.10 (literal errors) сильно сдвинул RP: DTV2 RPv3 67.4 → **77.5**, Artemis ERP 75.9 → **54.9** — старая колонка RP_v3 устарела | [docs\research\caliperbench-2026-10.md](research/caliperbench-2026-10.md), [docs\models.md](models.md) |
| Топ ERP среди 31B non-think | ✅ `StyleTune 31B` (68.5, но RU-провал) и **`Giftige-Blume 31B v1` Blazed-Forge (67.7, якорный)** | [docs\models.md](models.md) «Кандидаты» |
| `Giftige-Blume-StyleSwap` | ⚠️ merge без своей base + прививка StyleTune (RU 17–0 %) — тест механизма, не приоритет по RU | [docs\research\rp-model-candidates.md](research/rp-model-candidates.md) §9 |
| Инструменты парсинга CaliperBench | ✅ [bench\parse_caliper.py](../bench/parse_caliper.py), [bench\fetch_hf_meta.py](../bench/fetch_hf_meta.py), [bench\caliper_classify.py](../bench/caliper_classify.py) | — |

## 12. Датасеты RP/ERP (EN/RU) и данные обучения (2026-10-08)

| Что | Вердикт | Детали |
| --- | --- | --- |
| Пул датасетов RP/DRP/ERP (EN + RU), под SFT и перевод EN→RU | ✅ собрано ~45 (ссылки проверены по HF API) | [docs\research\rp-datasets-en-ru.md](research/rp-datasets-en-ru.md) |
| Проверка датасетов **по факту** (реальные строки через HF datasets-server) | ⚠️ **единственный проверенно чистый RP-датасет — Sonnet3.5-Charcard** (9 736 сцен, ~20 ходов, 0 дублей, 5/5); PIPPA — объём, но шум (3.5/5); LimaRP — human-эталон, но **не проверена** (архив 7z); CoSER — проза/память (копирайт); `chub` — вероятно **перевод**, не RU-native (не проверен); `krplt` — хороший русский, но **проза**; `bluemoon`/`sdsr` — сырые форумные посты (не SFT), `fujiiee` — состояние бота (не RP); готового RU-RP-диалогового корпуса нет | [docs\research\rp-datasets-quality-check.md](research/rp-datasets-quality-check.md) |
| На чём обучались наши Gemma-4 RP-мержи/файнтюны и современные Gemma-4 RP | ✅ **почти все — мержи** (данных нет; узел данных = доноры), файнтюны — StyleTune (`lm_head`-only), Artemis, MeroMero (SFT+GRPO). Данные живут в узком круге ~10–15 SFT-доноров (MeroMero, Scotoma-2, Musica, Gutenberg, Gemopus, glimmer, StyleTune, Ortenzya); публичные HF-ID почти не раскрыты, **из нашего пула подтверждён только `Gryphe/Sonnet3.5-Charcard`** (в Musica), PIPPA/LimaRP/CoSER в карточках Gemma-4 RP **не встречаются**; uncensoring = Heretic+ARA abliteration (не данные); reasoning-трейсы — синтетика DeepSeek/GLM; **русского обучения нет ни у одной** (`language: en`, искл. Ortenzya `en+jpn`) | [docs\research\gemma4-rp-training-data.md](research/gemma4-rp-training-data.md) |
