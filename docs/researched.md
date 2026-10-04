# Реестр проверенного (не повторять)

Единый список всего, что уже проверено в этом проекте, с вердиктом и ссылкой на детали. **Перед новым
исследованием — свериться здесь.** Обновляется при каждом новом замере.

Обозначения: ✅ оставляем/используем · ❌ проверено и отвергнуто · ⏸ помечено, но не измерялось на нашем стенде.

Стенд: RTX 4060 Ti 16 ГБ, Ryzen 7 5700X, 32 ГБ, Windows. Сборки: **b11382** (основная,
`downloads\llama-b11382-cu124`) и **b10472** (старая, `GitTest\llama.cpp`). Все TG — на реалистичном
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
| Синтетическая приёмка (`--spec-synth-*`) | ⏸ только бенчмаркинг | `docs\speculative.md` |
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
| DRY / min-p / XTC / dynatemp / mirostat | ⏸ рекомендации сообщества (качество RP), **не измеряли** | `context-infinite-chat.md` §6 |

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
- DRY/XTC/min-p — реальный эффект на наших моделях.
- `--fit-target`, `--no-host`, `-kvu/--kv-unified`, `--lookup-cache-static/dynamic`.
- Новые PR: #27210 (adaptive MTP), #27173 (draft chain), #28702 (FFN-фьюжн PP), #29807 (SSM-копии), #27248 (CUDA KV q4_1/…).

## 9. Логи моделей (там все серии замеров)

- `docs\swift-1.5-27b.md`, `docs\gemma-4-31b.md`, `docs\gemma-4-26b-a4b.md`, `docs\qwen36-35b-a3b.md`
- `docs\gemma-4-31b-rp-merges.md` (Split-Untied-31B, G4-MeroMero-v2-31B-heretic)
- Кросс-модельные: `docs\speculation-research.md`, `docs\context-infinite-chat.md`
- Сырые данные: `bench\runs\results.jsonl`, наборы — `bench\suites\` (`real_*`, `probe_*`, `tune_*`, `audit_*`)
