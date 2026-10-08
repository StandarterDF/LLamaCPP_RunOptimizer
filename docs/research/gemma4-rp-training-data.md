# На каких данных обучались RP-модели Gemma-4 (EN/RU)

Срез: **2026-10-08**. Задача: выяснить по HF-карточкам и mergekit-рецептам, на какой базе,
каким методом и **на каких данных/донорах** сделаны любимые RP-модели проекта (Gemma-4 31B / 26B-A4B),
и что вообще фигурирует в тюнах Gemma-4 RP (2025–2026).

Опора (не дублируется, только ссылки): `docs\research\rp-model-candidates.md` (донор-граф, Ateron, §9),
`docs\models.md`, `docs\models\gemma-4-31b.md`, `docs\models\gemma-4-31b-rp-merges.md`,
`docs\models\gemma-4-26b-a4b.md`, `docs\research\rp-datasets-en-ru.md`,
`docs\research\rp-datasets-quality-check.md`, `docs\research\why-ru-models.md`,
`docs\research\caliperbench-2026-10.md`.

## 0. Методика и ограничения

- Источник — **HF-карточки напрямую** (`huggingface.co/<repo>/raw/main/README.md`) и HF API
  (`/api/models?author=…`) — снято **08.10.2026**. Все рецепты (`mergekit_config.yml`) и списки
  датасетов — из README/конфигов карточек, не реконструированы.
- **Проверено**: существование репо, `base_model`, метод, доноры, `datasets` из карточек.
  Где README нет (ConicCat Writer-D/F) — помечено «не указано».
- **Не проверено**: фактическое содержимое внутренних/приватных датасетов (`zerofata/pretok`,
  `*.jsonl`), качество доноров, реальные токены. Числа карточек принимаются на веру.
- «Датасеты» у **мержей** не существуют: узел данных — это доноры; данные указываются только у
  **файнтюнов/LoRA/DPO/GRPO**. Поэтому для мержей в графе «доноры/датасеты» стоят доноры.
- Язык: у **всех** разобранных RP-тюнов Gemma-4 тег `language: en` (или отсутствует);
  единственное исключение — `Ortenzya` (`en`+`jpn`). RU-датасетов в карточках Gemma-4 RP **нет**.

## 1. Главные выводы

1. **Почти все «любимые» RP-модели — это мержи, а не SFT.** DTV1/V2, Schattenblume, Glistening-Gem,
   Giftige-Blume, Goetia, MoonGem, Writers-V2, Split-Untied — mergekit (dare_ties / ties /
   task_arithmetic / della_linear / moe_della / model_stock). Файнтюны — только StyleTune,
   Artemis, MeroMero (SFT+GRPO), а также доноры (scotoma-2, Musica, Gutenberg, glimmer, Ortenzya).
2. **Данные «живут» в узком круге доноров.** Реальный корпус RP у Gemma-4 — это ~10–15 SFT-моделей
   (MeroMero, Scotoma, Musica, Gutenberg, Gemopus, glimmer, StyleTune, Ortenzya-heretic, Artemis,
   ReadyArt-семья); мержи бесконечно переупаковывают их. Отсюда «донор-граф» замкнут и повторяется.
3. **Публичных датасетов в карточках почти нет.** Большинство авторов пишут «my data», «narrative
   data», «curated prompts»; конкретные HF-ID указывают **только** Musica (14 наборов), Gutenberg-31B
   (DPO-наборы), MeroMero-26B/ReadyArt (anime-наборы), ConicCat (Gutenberg-SFT/Condor/Sonnet-дистиллы).
   PIPPA / LimaRP / CoSER в карточках Gemma-4 RP **не упоминаются** (это пул из наших датасет-доков).
4. **Подтверждён только один публичный RP-датасет из нашего пула** — `Gryphe/Sonnet3.5-Charcard-Roleplay`
   (в `G4-31B-Musica-v1`). Это прямой мост к `docs\research\rp-datasets-en-ru.md`.
5. **«Анцензуринг» — это abliteration (Heretic + ARA), а не данные.** Scotoma-2 (γ-fold ARA + DPO),
   `trohrbaugh/gemma-4-31b-it-heretic-ara`, `llmfan46/...-heretic` — оптимизированы по англоязычным
   refusal-направлениям (KL 0.012–0.043), а не по RP/ERP-корпусу.
6. **Reasoning-трейсы — синтетика от англоязычных фронтир-моделей**: Pantheon — back-gen DeepSeek 3.2;
   MeroMero v2 — судьи DeepSeek-V4 Flash/Pro и GLM-5.2. Это тот же канал, где у нас зафиксирован
   RU-регресс (`docs\research\why-ru-models.md` §5.2 п.2).
7. **Русский в Gemma-4 RP не обучается** — он держится как побочный эффект осторожного мержа
   (низкая density + якорь на base, `embed/lm_head=0`) либо как следствие RU-данных у отдельных
   моделей (WaifuGemma4, не Gemma-4-RP-мерж). Подробности и наши замеры — §6.

---

## 2. Сводная таблица: модель → база → метод → доноры/датасеты → ссылка

«Метод» — по карточке. «Доноры/датасеты» — то, что реально указано (у мержей — доноры;
у тюнов — датасеты). **Жирным** — обязательные модели задания.

| Модель (автор) | База | Метод | Доноры / датасеты | Ссылка |
| --- | --- | --- | --- | --- |
| **Dark-Thoughts V2 31B** (Ateron) | `gemma-4-it` (локальный путь) | merge: 2× `dare_ties`, density 0.4–0.6, послойные веса | MeroMero-v2 + Dark-Scarlett-v2 → Scotoma-v2 + Dark-Mero-V3 | [Ateron/Gemma-4-Dark-Thoughts-V2-31B](https://huggingface.co/Ateron/Gemma-4-Dark-Thoughts-V2-31B) |
| **Dark-Thoughts V1 31B** (Ateron) | `gemma-4-it` | merge: 2× `dare_ties`, density 0.5 | MeroMero-v2 + Dark-Scarlett-v2 → Scotoma-v2 + DarkMero | [Ateron/Gemma-4-Dark-Thoughts-31B](https://huggingface.co/Ateron/Gemma-4-Dark-Thoughts-31B) |
| **Schattenblume 31B** (Nimbz) | `google/gemma-4-31B-it` | merge: 1× `della_linear`, у доноров `embed/lm_head/vision/norm=0` | Scotoma-2 (d 0.85) + Giftige-Blume-v1 (0.55) + MeroMero-v2 (0.60) | [Nimbz/Schattenblume-31B](https://huggingface.co/Nimbz/Schattenblume-31B) |
| **Glistening-Gem 31B v2.1** (sophosympatheia) | `google/gemma-4-31B-it` (в рецепте — `densenet/Gemma-4-31B-StyleTune-heretic-ara`) | merge: DELLA | MeroMero-v2 + Artemis-31B-v1 + Ortenzya-heretic + stock base | [sophosympatheia/Glistening-Gem-31B-v2.1](https://huggingface.co/sophosympatheia/Glistening-Gem-31B-v2.1) |
| **Giftige-Blume 31B v1** (Blazed-Forge; карточка «by Nimbz») | `google/gemma-4-31B-it` | merge: 3 фазы `model_stock` → `breadcrumbs_ties` → `della_linear`; `embed/lm_head=0` | Equinox-31B, storymaxxed+storymaxxed2, Musica-v1, Ortenzya-heretic, Mero-Artemis-v0.3.1, Sprinkle-Gemma-4-31B, Gemopus-4-31B-it | [Blazed-Forge/Gemma-4-Giftige-Blume-31B-v1](https://huggingface.co/Blazed-Forge/Gemma-4-Giftige-Blume-31B-v1) |
| **Giftige-Blume-StyleSwap 31B** (Casual-Autopsy) | `Blazed-Forge/Giftige-Blume-31B-v1` + `Gryphe/Gemma-4-31B-StyleTune` | merge: tensor swap (StyleSwap `lm_head`) | Giftige-Blume-v1 + StyleTune-31B | [Casual-Autopsy/Giftige-Blume-31B-v1-StyleSwap](https://huggingface.co/Casual-Autopsy/Giftige-Blume-31B-v1-StyleSwap) |
| **StyleTune-V2 26B-A4B** (Gryphe) | `google/gemma-4-26B-A4B-it` | **finetune**: только `lm_head` (1 тензор из 659), 1 эпоха | «та же data, что у Pantheon-Reasoning», без instruct-24k; 100 % narrative — **HF-ID не указаны** | [Gryphe/Gemma-4-26B-A4B-StyleTune-V2](https://huggingface.co/Gryphe/Gemma-4-26B-A4B-StyleTune-V2) |
| **StyleTune 31B** (Gryphe) | `google/gemma-4-31B-it` | **finetune**: только `lm_head` (1 из 834) | то же (Pantheon-данные) | [Gryphe/Gemma-4-31B-StyleTune](https://huggingface.co/Gryphe/Gemma-4-31B-StyleTune) |
| **Goetia 26B-A4B v1.6** (Naphula) | `google/gemma-4-26B-A4B-it` | merge: `moe_della` (mergekit-exp) | ~28 доноров (Orion, Pantheon, Musica, StyleTune-V2, MeroMero-26B, ReadyArt-семья, Boulesis, Gemopus…); **не uncensored** | [Naphula/Goetia-26B-A4B-v1.6](https://huggingface.co/Naphula/Goetia-26B-A4B-v1.6) |
| **Artemis 31B v1.2** (TheDrummer) | `google/gemma-4-31B-it` | **finetune** | данные **не указаны** (только «more data, more sophisticated training») | [TheDrummer/Artemis-31B-v1.2](https://huggingface.co/TheDrummer/Artemis-31B-v1.2) |
| **G4-MeroMero-v2 31B** (zerofata) | `google/gemma-4-31B-it` | **finetune+merge**: SFT→SLERP→GRPO→GRPO→on-policy SFT; LoRA r64 | внутренние `diversity_sft_masked.jsonl`, `rp3_train.jsonl`, `g4_onpolicy_rp_masked.jsonl` (~4k рассказов + RP); судьи DeepSeek-V4 Flash/Pro, GLM-5.2 | [zerofata/G4-MeroMero-v2-31B](https://huggingface.co/zerofata/G4-MeroMero-v2-31B) |
| **Split-Untied 31B** (Blazed-Forge; карточка «by Nimbz») | `google/gemma-4-31B-it` | merge: 2× `della_linear` + StyleSwap; `embed/lm_head=0` | Melinoe-VL-heretic, Glistening-Gem-v2.1/v2.0, MeroMero-v2, Scotoma-2, DTV2, Pantheon-Reasoning-31B-1.1 | [Blazed-Forge/Split-Untied-31B](https://huggingface.co/Blazed-Forge/Split-Untied-31B) |
| **MoonGem 31B** (Ateron) | `ReadyArt/gemma-4-31B-it-scotoma-2` | merge: 3 фазы `ties` → `task_arithmetic` → `task_arithmetic` | Glimmer-rp, Gutenberg, Gemopus, Melinoe-VL, MeroMero-v2, Musica-v1, MicroMix-P1/P2 (7 родителей) | [Ateron/Gemma-4-MoonGem-31B](https://huggingface.co/Ateron/Gemma-4-MoonGem-31B) |
| **Writers 31B V2** (Ateron) | `gemma-4-it` | merge: `dare_ties` (mlp-веса) | ConicCat Writer-D + Writer-F + Scotoma-2 | [Ateron/Gemma-4-Writers-31B-V2](https://huggingface.co/Ateron/Gemma-4-Writers-31B-V2) |

### Доноры (второй уровень — там, где указаны данные)

| Донор | База | Метод | Данные | Ссылка |
| --- | --- | --- | --- | --- |
| **ReadyArt/gemma-4-31B-it-scotoma-2** | `gemma-4-31B-it` | finetune: γ-fold abliteration + **DPO ×3**, 9.3k пар | данные не названы (пары «с тиком/без»); abliteration — Heretic ARA / mmd-rbf (trial-127); **не uncensored** | [карточка](https://huggingface.co/ReadyArt/gemma-4-31B-it-scotoma-2) |
| **ReadyArt/Dark-Scarlett-v2.0-31B** | `nbeerbower/Gemma4-Gutenberg-31B` | finetune: **LoRA r32**, 1 эпоха, только text-слои | синтетика: **12 211 промптов**, «Character/Emotional Engine», M→F, в духе Melody1437 | [карточка](https://huggingface.co/ReadyArt/Dark-Scarlett-v2.0-31B) |
| **ReadyArt/Melody1437-31B** | `gemma-4-31B-it` | finetune (только text-слои) | синтетический **explicit adult ERP**-датасет (Character/Emotional Engine) | [карточка](https://huggingface.co/ReadyArt/Melody1437-31B) |
| **llmfan46/gemma-4-Ortenzya-…-heretic** | `llmfan46/gemma-4-31B-it-uncensored-heretic` | finetune: Heretic v1.2.0 **ARA** (слои 30–48, `attn.o_proj`) → Unsloth SFT | письменный тюн; датасеты не названы; `en`+`jpn`; отказов 9/100 | [карточка](https://huggingface.co/llmfan46/gemma-4-Ortenzya-The-Creative-Wordsmith-31B-it-uncensored-heretic) |
| **trohrbaugh/gemma-4-31b-it-heretic-ara** | `gemma-4-31b-it` | abliteration: Heretic v1.2.0 **ARA**, слои 2–60 | KL **0.0120**, отказов 5/100 (было 98/100) | [карточка](https://huggingface.co/trohrbaugh/gemma-4-31b-it-heretic-ara) |
| **MRockatansky/Gemma-4-31B-storymaxxed** | `trohrbaugh/gemma-4-31b-it-heretic-ara` | finetune: **DPO** LoRA | **5 000+ narrative preference pairs** (длительная проза) | [карточка](https://huggingface.co/MRockatansky/Gemma-4-31B-storymaxxed) |
| **nbeerbower/Gemma4-Gutenberg-31B** | `gemma-4-31B-it` | finetune: **ORPO** (β 0.1), LoRA r64 | `schneewolflabs/Athanorlite-DPO` (14 816 пар) + `jondurbin/gutenberg-dpo-v0.1`, `nbeerbower/gutenberg2-dpo`, `gutenberg-moderne-dpo`, `human-writing-dpo`, `sam-paech/gutenberg3-…` | [карточка](https://huggingface.co/nbeerbower/Gemma4-Gutenberg-31B) |
| **AuriAetherwiing/G4-31B-Musica-v1** | `gemma-4-31B-it` | finetune: LoRA r64, 1 эпоха | **14 публичных наборов** (см. §5): Lilith-v0.3, GLM5-Characters, Instruct-Anime, Anime-AMA-Prose, mimo/doubao-дистиллы, Orion-Deepseek-RP, **Sonnet3.5-Charcard**, ChatGPT-4o-Writing, kimi-*, Novelist-CoT | [карточка](https://huggingface.co/AuriAetherwiing/G4-31B-Musica-v1) |
| **BirdToast/Gemma-4-31B-glimmer-rp-v0.1** | `gemma-4-31B-it` | finetune: **LoRA r16a32** | внутренние `*.jsonl` (5 725 сэмплов, 15.4M токенов): writing_critique, instruct, marvin_style_bible, rp_generation_*, rp_analysis | [карточка](https://huggingface.co/BirdToast/Gemma-4-31B-glimmer-rp-v0.1) |
| **Jackrong/Gemopus-4-31B-it** | `gemma-4-31B-it` | finetune: SFT (Unsloth) | «open-source instruction pairs + multi-turn», **HF-ID не указаны**; `en/zh/ko/ja` | [карточка](https://huggingface.co/Jackrong/Gemopus-4-31B-it) |
| **zerofata/G4-MeroMero-31B** (v1) | `gemma-4-31B-it` | finetune+merge: SFT ~49M ток. → SLERP t=0.5 | `zerofata/pretok`; LoRA r64 | [карточка](https://huggingface.co/zerofata/G4-MeroMero-31B) |
| **zerofata/G4-MeroMero-26B-A4B** | `gemma-4-26B-A4B-it` | finetune+merge: SFT ~35M ток. → linear 0.5 | `zerofata/Instruct-Anime`, `Gemini-3.1-Pro-SmallWiki`, `Gemini-3.1-Pro-GLM5-Characters`, `Roleplay-Anime-Characters`; LoRA r128 + MoE-expert LoRA | [карточка](https://huggingface.co/zerofata/G4-MeroMero-26B-A4B) |
| **sophosympatheia/Mero-Artemis-31B-v0.3.1** | — | merge (DELLA) | `BeaverAI/Artemis-31B-v1h-GGUF` + `zerofata/G4-MeroMero-31B` (Q8_0-источник) | [карточка](https://huggingface.co/sophosympatheia/Mero-Artemis-31B-v0.3.1) |
| **Gryphe/Pantheon-Reasoning-31B-1.1** | `Gryphe/Gemma-4-31B-StyleTune` | finetune (full) | Pantheon-корпус 26 % + general RP 36 % + text-adventure 38 %; **reasoning back-gen DeepSeek 3.2** | [карточка](https://huggingface.co/Gryphe/Pantheon-Reasoning-31B-1.1) |
| **Gryphe/Pantheon-Reasoning-26B-A4B-1.1-V2** | `Gryphe/Gemma-4-26B-A4B-StyleTune-V2` | finetune (full) | те же narrative-данные, что у 31B | [карточка](https://huggingface.co/Gryphe/Pantheon-Reasoning-26B-A4B-1.1-V2) |

---

## 3. Разбор по обязательным моделям (детали)

### 3.1. Dark-Thoughts V1 / V2 31B — Ateron (эталон проекта)

**Метод — только мерж** (никаких SFT/GRPO), на форке mergekit от zerofata. `base_model` задан
**локальным путём** `F:\AI\Merge\Gemma-4-it` (в HF-тегах base не виден — тег врёт, см.
`rp-model-candidates.md` §9).

- **V2** — две фазы `dare_ties`, `density 0.4–0.6`, послойные веса:
  - Фаза 1 «Spark»: `MeroMero-V2` (density 0.50, веса 0.60→0.40 по глубине) + `Dark-Scarlett-V2` (0.50, зеркально);
  - Фаза 2 «Form»: `Scotoma-V2` (0.60, `mlp 0.2 / q 0.5 / k 0.5 / v 0.6 / o 0.8`, слойные `[0.6,0.6,0.7,0.8,0.8]`) + `Dark-Mero-V3` (0.40, `mlp 0.8 / o 0.2`).
- **V1** — та же идея, проще веса (MeroMero 0.7→0.5, Scotoma 0.8→0.5, донор «DarkMero»).
- **Данные**: у мержа нет; доноры — `MeroMero-v2` (SFT+GRPO, см. 3.7), `Dark-Scarlett-v2.0`
  (LoRA r32, 12 211 синтетических ERP-промптов, M→F), `Scotoma-v2` (γ-fold ARA + DPO ×3).
- `language: en`; `tokenizer_source: base`; `dtype: bfloat16`. imatrix/контекст в карточке не указаны.
- Ссылки: [V2](https://huggingface.co/Ateron/Gemma-4-Dark-Thoughts-V2-31B),
  [V1](https://huggingface.co/Ateron/Gemma-4-Dark-Thoughts-31B).

### 3.2. Schattenblume-31B — Nimbz

**Метод** — один проход `della_linear` поверх `google/gemma-4-31B-it`, форк mergekit от zerofata.
Доноры: `scotoma-2` (density 0.85, spine 0.80), `Giftige-Blume-v1` (0.55), `MeroMero-v2` (0.60);
`embed_tokens / lm_head / embed_vision / vision_tower / multi_modal_projector / norm / layer_scalar`
у доноров **занулены** — поэтому язык базы почти не тронут (наш RU-замер 100 %).
В карточке прямо: «three ingredients, plus the base». Данные/датасеты — не указаны.
Ссылка: [Nimbz/Schattenblume-31B](https://huggingface.co/Nimbz/Schattenblume-31B).

### 3.3. Glistening-Gem-31B v2.1 — sophosympatheia

**Метод** — DELLA-мерж. Доноры: `MeroMero-v2`, `TheDrummer/Artemis-31B-v1`,
`llmfan46/...Ortenzya...heretic`, + `google/gemma-4-31B-it`. **Противоречие в карточке**: во вступлении
написано «using stock `gemma-4-31B-it` as a base», а в разделе Merge Details — база
`densenet/Gemma-4-31B-StyleTune-heretic-ara` (это и было причиной провала v2.0 — «exotic base model
that made customizations to the final output layer»). Помечено как расхождение (§7).
v1.0 — DELLA на `gemma-4-31B-it` с `Artemis-31B-v1h-GGUF`, `MeroMero-31B`, `Ortenzya-heretic`.
Артефакты (typo/склейки) автор приписывает вкладу Ortenzya-heretic. `language: en`. Данные — не указаны.
Ссылки: [v2.1](https://huggingface.co/sophosympatheia/Glistening-Gem-31B-v2.1),
[v1.0](https://huggingface.co/sophosympatheia/Glistening-Gem-31B-v1.0).

### 3.4. Giftige-Blume-31B-v1 (Blazed-Forge) и StyleSwap (Casual-Autopsy)

**Giftige-Blume v1** — мерж в **три фазы**:
1. `model_stock` на базе `LatitudeGames/G4-Equinox-31B`: Equinox + `storymaxxed` + `storymaxxed2` + `Musica-v1` («broad RP scenario»);
2. `breadcrumbs_ties` («Heretic RP Engine»): фаза-1 + `Ortenzya-heretic` (density 0.15–0.75 по срезам) + `Mero-Artemis-v0.3.1` (0.40–0.80);
3. `della_linear` на `google/gemma-4-31B-it`: base + `Sprinkle-Gemma-4-31B` + `Gemopus-4-31B-it` + «Heretic-RP-Engine»; у доноров `embed_tokens/lm_head=0`.

Данные не указаны (мерж). Карточка оформлена на репо `Blazed-Forge/...`, но подписана «by Nimbz»,
а GGUF-ссылки ведут на `Nimbz/Gemma-4-Giftige-Blume-31B-v1-GGUF` — **владелец неоднозначен** (§7).
Ссылка: [Blazed-Forge/Gemma-4-Giftige-Blume-31B-v1](https://huggingface.co/Blazed-Forge/Gemma-4-Giftige-Blume-31B-v1).

**Giftige-Blume-StyleSwap** (Casual-Autopsy) — эксперимент «tensor swap»: `base_model` =
`[Blazed-Forge/Gemma-4-Giftige-Blume-31B-v1, Gryphe/Gemma-4-31B-StyleTune]`. Карточка в одну строку,
без рецепта; «secondary experimental model» к `G4-MeroMero-31B-StyleSwap`. Именно прививка головы
StyleTune дала RU 3.3/2.6 у нас (`docs\models.md`). Ссылка:
[Casual-Autopsy/Giftige-Blume-31B-v1-StyleSwap](https://huggingface.co/Casual-Autopsy/Giftige-Blume-31B-v1-StyleSwap).

### 3.5. StyleTune-V2 26B-A4B и StyleTune-31B — Gryphe

**Метод — «style tune»: обучается ровно один тензор `lm_head`** (1 из 659 у 26B; 1 из 834 у 31B),
всё остальное заморожено. Это объясняет сохранность мультиязычности базы.
- V2 26B: **1 эпоха** (V1 делал несколько эпох — «second epoch does all sorts of nasty stuff to MoE»);
  52 % меньше клише; «same Gemma 4 26B-A4B underneath».
- 31B: 60 % меньше клише, «one tensor changed out of 834».
- **Данные**: «the same data I had on me for my last Pantheon Reasoning release, with one notable
  exception — No instruct 24k set. 100 % narrative data». Конкретные HF-ID **не указаны**; из
  карточки Pantheon-Reasoning известен состав (Pantheon-корпус + general RP + text-adventure, см. 3.12).
- `language: en` (но мультиязычность базы почти не тронута — наш RU-замер 96–100 %).
Ссылки: [26B-V2](https://huggingface.co/Gryphe/Gemma-4-26B-A4B-StyleTune-V2),
[31B](https://huggingface.co/Gryphe/Gemma-4-31B-StyleTune).

### 3.6. Goetia-26B-A4B v1.6 — Naphula

**Метод** — `moe_della` (форк `mergekit-exp` от EldritchLabs) на `google/gemma-4-26B-A4B-it`.
**~28 доноров** (самый широкий из разобранных): Orion-26B-v1, Pantheon-Reasoning-26B-A4B-1.1-V2,
StyleTune-V2, MeroMero-26B, Gutenberg-26B, Gemopus-26B, Musica-26B, Animus-V14.1-FFT, Sonnet-3.7-дистилл,
Claude-Opus-дистиллы, вся ReadyArt-семья (Dark-Scarlett, For-Her-Darkside, Heimdallr, Melody1437,
Omega-Evolution, Serenity), Boulesis, Esmeralda, Xenon, fiction-bf16, gem4_26B_adapter, G4-26B-SFT-6.
У большинства `lm_head/embed_tokens=0`; у Orion/Pantheon/StyleTune-V2 `lm_head/embed_tokens=0.5` (голова/эмбеддинги).
Вторая фаза — `moe_della` Orion + Pantheon. Карточка прямо: **«not currently uncensored. There are refusals»**.
Данные — не указаны (мерж). Ссылка: [Naphula/Goetia-26B-A4B-v1.6](https://huggingface.co/Naphula/Goetia-26B-A4B-v1.6).

### 3.7. G4-MeroMero-v2-31B — zerofata (единственный «полный» пайплайн)

**Метод**: `SFT → Merge(SLERP) → GRPO → GRPO → on-policy SFT`, обучение на Axolotl, **LoRA r64**
(target: `mlp|self_attn.(up|down|gate|q|k|v|o)_proj`), последний ход.
1. **Diversity SFT** — ~4 000 коротких рассказов (человеческие + синтетика фронтир-моделей), отобранных
   по narrative-промптам и «аттракторам»; плюс обычные creative-instruct и RP-данные. Затем **SLERP t=0.5**
   обратно в instruct.
2. **Creative GRPO** (think off), 300 шагов; reward — LLM-судья diversity/coherence, attractor-пенальти,
   narrative-rate, «degeneracy guards» (**проверка non-Latin символов и склеек**).
3. **RP Logic GRPO** (think on), 100 шагов; судья — **DeepSeek-V4 Flash** с рубрикой.
4. **On-policy multi-outcome SFT** — ~3 300 собственных сэмплов, критика **GLM-5.2**, ре-генерация
   **DeepSeek-V4-Pro**; ~60 % с thinking.
Датасеты — внутренние jsonl (`diversity_sft_masked.jsonl`, `rp3_train.jsonl`, `g4_onpolicy_rp_masked.jsonl`),
публичных HF-ID нет. Опирается на статьи **StoryScope** (arXiv 2604.03136) и «Elias in the Lighthouse, Again?»
(arXiv 2605.26492). Ссылка: [zerofata/G4-MeroMero-v2-31B](https://huggingface.co/zerofata/G4-MeroMero-v2-31B).

### 3.8. Artemis-31B-v1.2 — TheDrummer

**Метод — finetune** (`base_model: google/gemma-4-31B-it`). Карточка — по сути отзывы тестеров
(«writing that doesn't feel like G4», «reasoning that works», handoff на 100k); **никаких данных,
LoRA-rank, датасетов не указано**. Родственные v1/v1.1 — тот же профиль («more data, more sophisticated
training configurations»). Ссылки: [v1.2](https://huggingface.co/TheDrummer/Artemis-31B-v1.2),
[v1](https://huggingface.co/TheDrummer/Artemis-31B-v1).

### 3.9. Split-Untied-31B — Blazed-Forge (карточка «by Nimbz»)

**Метод** — **два прохода `della_linear`** поверх `gemma-4-31B-it` + StyleSwap-прививка
(untied `lm_head`). Фаза 1 бьёт по `q_proj+k_proj` (внимание) и `gate_proj+up_proj` (маршрутизация знаний):
`Melinoe-VL-heretic` (q/k 0.45→0.30, gate/up 0.28→0.18), `Glistening-Gem-v2.1` (q/k 0.14→0.10),
`MeroMero-v2` (gate/up 0.30). У доноров `embed/lm_head/vision/norm=0` (кроме norm/layer_scalar=1.0 по density).
В HF-тегах базы — 8 моделей: base, scotoma-2, Melinoe-VL-heretic, Glistening-v2.1/v2.0, MeroMero-v2, DTV2,
Pantheon-Reasoning-31B-1.1. Данные — не указаны. «Experimental, dark lean». Ссылка:
[Blazed-Forge/Split-Untied-31B](https://huggingface.co/Blazed-Forge/Split-Untied-31B).

### 3.10. MoonGem-31B — Ateron

**Метод** — 3 фазы мержа на базе `ReadyArt/gemma-4-31B-it-scotoma-2`:
1. `ties` («Bleed»): `Glimmer-rp` + `Gutenberg` + `Gemopus` (density 0.15, веса 0.10–0.15);
2. `task_arithmetic` («Crimson»): `Melinoe-VL` + `MeroMero-v2` + `Musica-v1` (веса `[0.10,0.10,0.15,0.15,0.10]`);
3. `task_arithmetic` («Blood»): `MicroMix-P1` + `MicroMix-P2` (по 0.5).
7 родителей. Данные — не указаны. Ссылка: [Ateron/Gemma-4-MoonGem-31B](https://huggingface.co/Ateron/Gemma-4-MoonGem-31B).

### 3.11. Writers-31B-V2 — Ateron

**Метод** — `dare_ties` на `gemma-4-it`; доноры `ConicCat/Gemma4-Writer-31B-D`, `ConicCat/Gemma4-Writer-31B-F`,
`ReadyArt/gemma-4-31B-it-scotoma-2`; веса по `mlp.gate/up/down_proj`. Девиз «Less Gemma — more human»,
цель — починить нестабильность обоих ConicCat-тюнов. Данные — не указаны. Ссылка:
[Ateron/Gemma-4-Writers-31B-V2](https://huggingface.co/Ateron/Gemma-4-Writers-31B-V2).
(У самих ConicCat Writer-D/F **README нет** — их данные неизвестны; родственная линия
`ConicCat/Gemma4-GarnetV2/V3` использует датасеты `ConicCat/Gutenberg-SFT`, `ConicCat/Condor-SFT-Filtered`,
`Charcards_*`, `Lamp_P_Preference` — см. §5.)

---

## 4. Донор-граф (кто в кого влит)

Узлы — модели; стрелка «→» = «использована как донор/база». В скобках — тип тюна-корня.
Базовое ядро Gemma-4 RP — левый столбец.

```
База: google/gemma-4-31B-it ──────────────────────────────────────────────┐
                                                                          │
Файнтюны-доноры (данные):                                                 │
  G4-MeroMero-v2-31B        (SFT+GRPO, свои данные) ──┐                   │
  ReadyArt/scotoma-2        (ARA+DPO, 9.3k пар) ──────┤                   │
  ReadyArt/Dark-Scarlett-v2 (LoRA r32, 12.2k ERP) ────┤                   │
  AuriAetherwiing/Musica-v1 (LoRA r64, 14 датасетов) ─┤                   │
  nbeerbower/Gutenberg-31B  (ORPO, DPO-наборы) ───────┤                   │
  Jackrong/Gemopus-31B      (SFT) ────────────────────┤                   │
  BirdToast/glimmer-rp      (LoRA r16a32) ────────────┤                   │
  Gryphe/StyleTune          (lm_head-only) ───────────┤                   │
  llmfan46/Ortenzya-heretic (ARA+SFT) ────────────────┤                   │
  TheDrummer/Artemis-v1     (finetune) ───────────────┤                   │
  bgg1996/Melinoe-VL[-heretic], Equinox-31B, storymaxxed, Sprinkle, Boulesis, Orion…
                                                      │                   │
Мержи-1 (корни):                                      ▼                   ▼
  DTV2 (dare_ties: MeroMero+DarkScarlett → Scotoma)   ← Ateron
  MoonGem (ties: Glimmer+Gutenberg+Gemopus → Melinoe+MeroMero+Musica → MicroMix)
  Schattenblume (della: scotoma-2+Giftige-Blume+MeroMero)
  Giftige-Blume-v1 (model_stock → breadcrumbs_ties → della)
  Goetia-26B (moe_della, ~28 доноров)
  Glistening-Gem (DELLA: MeroMero+Artemis+Ortenzya+base)
  Writers-V2 (dare_ties: Writer-D+Writer-F+scotoma-2)
  Mero-Artemis-v0.3.1 (Artemis-v1h + MeroMero-v1)

Мержи-2 (из мержей):                                   ▼
  Split-Untied (della: Melinoe+Glistening+MeroMero, +DTV2/Scotoma/Pantheon)
  Giftige-Blume-StyleSwap (Giftige-Blume-v1 + StyleTune)
  Split-31B (Nimbz; из Split-Untied-семьи)  … и далее по кругу
```

**Наблюдения:**
- **Ядро повторяется.** `MeroMero-v2` и `scotoma-2` входят почти во все топ-мержи; `Giftige-Blume-v1`,
  `Glistening-Gem`, `DTV2` — во второй эшелон (Split-Untied, StyleSwap).
- **Разделение «креатив → форма»** (Ateron, Nimbz): сначала флейвор-донор (MeroMero/Giftige-Blume/Musica),
  затем «полировщик» (Scotoma-2/Ortenzya-heretic) с занулением головы/эмбеддингов.
- **`embed_tokens`/`lm_head` у доноров зануляются** в della/breadcrumbs-рецептах (Schattenblume,
  Giftige-Blume-v1, Split-Untied) — это и есть механизм сохранения языка базы (наши RU-замеры 100 %).
  StyleSwap-мержи, наоборот, **прививают** чужую голову (StyleTune) → RU-провал (3.3/2.6 у нас).
- **Ateron не указывает base в HF-тегах** (локальный путь `Gemma-4-it`/`Gemma-4-Scotoma-V2`); по тегам
  фильтровать нельзя — только по рецепту (ср. `rp-model-candidates.md` §9).

---

## 5. Датасеты современных Gemma-4 RP (2025–2026)

Собрано из карточек, где датасеты **реально названы**. Разбито по происхождению.

### 5.1. Публичные RP/креатив-датасеты (HF-ID из карточек)

| Датасет | Где использован | Тип | Заметка |
| --- | --- | --- | --- |
| **Gryphe/Sonnet3.5-Charcard-Roleplay** | `G4-31B-Musica-v1` | SFT (char-card) | единственный публичный RP-набор из нашего пула, подтверждённый в Gemma-4-карточке; см. `rp-datasets-en-ru.md` §2, `rp-datasets-quality-check.md` §2.1 |
| `zerofata/Gemini-3.1-Pro-GLM5-Characters` | MeroMero-26B, Musica | SFT (синтетика Gemini+GLM5) | персонажи |
| `zerofata/Instruct-Anime`, `Anime-AMA-Prose`, `Roleplay-Anime-Characters`, `Gemini-3.1-Pro-SmallWiki` | MeroMero-26B | SFT (синтетика) | аниме/вики |
| `EVA-UNIT-01/Lilith-v0.3` | Musica | SFT | RP/персона |
| `allura-forge/mimo-v2-pro-claude-distill-hs3`, `doubao-seed2.0-distill-multiturn-expr-rp` | Musica | дистилл (Mimo/Claude/Doubao) | мультитёрн-RP |
| `Delta-Vector/Orion-Deepseek-V3-RP-Filtered`, `Orion-Deepseek-R1-RP-Filtered` | Musica | SFT (дистилл DeepSeek) | RP |
| `ToastyPigeon/kimi-stories-instruct`, `kimi-rp-v3`, `fujin-filtered-instruct` | Musica | SFT (дистилл Kimi) | истории/RP |
| `Dxniz/Novelist-CoT` | Musica | SFT+CoT | проза |
| `Gryphe/ChatGPT-4o-Writing-Prompts` | Musica | SFT (промпты) | стиль |
| `schneewolflabs/Athanorlite-DPO` (14 816 пар) | Gutenberg-31B | DPO/ORPO | суперсет Gutenberg-«Encore» |
| `jondurbin/gutenberg-dpo-v0.1`, `nbeerbower/gutenberg2-dpo`, `gutenberg-moderne-dpo`, `human-writing-dpo`, `sam-paech/gutenberg3-…` | Gutenberg-31B | DPO | литературная проза / anti-slop |
| `ConicCat/Gutenberg-SFT`, `Condor-SFT-Filtered`, `Charcards_Context_Distill_Gemma4_26BV2`, `Charcards_Delta_Qwen3_5V2`, `Lamp_P_Preference`, `C2_Sonnet_4_5`, `Ao3_Soft_Refusal`, `VSF`, `Mura_Books`, `MiniC2_V3.2`, `AntiRep` | линия ConicCat (Garnet/Writer/Qwen-Writer) | SFT/DPO/CoT | **не подтверждено**, что Writer-D/F их использовали (у них нет README) |

**Не найдено в карточках Gemma-4 RP** (хотя эти наборы — стандарт EN-RP и лежат в нашем пуле):
**PIPPA, LimaRP, CoSER, RoleBench, OpenCharacter, Kingfall-Roleplay**. То есть де-факто-стандарты
сообщества в открытых Gemma-4-тюнах **не декларируются** — либо используются внутренние кураторские
наборы, либо авторы не раскрывают ID. Отдельно: в нашем `rp-datasets-en-ru.md` эти наборы
рекомендованы как пул для перевода/обучения, но это **не** факт их использования в Gemma-4.

### 5.2. Внутренние / нераскрытые наборы

- `zerofata/pretok` (MeroMero-v1, ~49M токенов); MeroMero-v2 — внутренние `*.jsonl`
  (`diversity_sft_masked`, `rp3_train`, `g4_onpolicy_rp_masked`), ~4 000 рассказов + on-policy RP.
- `BirdToast` glimmer — внутренние `writing_critique / instruct / marvin_style_bible / rp_generation_* /
  rp_analysis` (5 725 сэмплов, 15.4M токенов).
- ReadyArt (Melody1437, Dark-Scarlett, Serenity, Heimdallr…) — **синтетика «Character/Emotional Engine»**
  (внутренний генератор), Dark-Scarlett: 12 211 промптов, M→F, «spirit of Melody1437».
- Gryphe StyleTune/Pantheon — «Pantheon-корпус» (10 персон × сотни сценариев) + general RP + text-adventure;
  HF-ID не раскрыты.
- Artemis (TheDrummer), Gemopus (Jackrong), Ateron/Nimbz-мержи — данные/ID не раскрыты.

### 5.3. «Uncensoring»-пайплайны (не данные, а веса)

- **Heretic v1.2.0 + Arbitrary-Rank Ablation (ARA)** — основной инструмент:
  `trohrbaugh/gemma-4-31b-it-heretic-ara` (слои 2–60, **KL 0.0120**, отказов 5/100 против 98/100),
  `llmfan46/gemma-4-31B-it-uncensored-heretic` → `Ortenzya` (слои 30–48, `attn.o_proj`, отказов 9/100).
- **Scotoma-2** (ReadyArt) — не abliteration «в лоб», а **γ-fold** того же heretic-ARA/mmd-rbf-эдита
  через J-Space + **DPO ×3** против «тиков» Gemma (negation/antithesis, em-dash, stacked adjectives);
  карточка прямо: «not uncensored». Абliteration-эдит калиброван по **англоязычным** refusal-направлениям.
- Наш вывод (`docs\research\why-ru-models.md` §5.2 п.4): abliteration RP-способностей не добавляет,
  а оптимизация по EN-refusal «протекает» на русском первым — что косвенно подтверждают KL-числа
  и `language: en` у всех heretic-моделей.

### 5.4. Reasoning-трейсы (синтетика, англоязычные фронтир-модели)

- **Pantheon-Reasoning** (Gryphe): трейсы **back-generated DeepSeek 3.2** («think as a writer planning
  the next response»), валидация судьёй + master-judge (1.1).
- **MeroMero-v2** (zerofata): судьи **DeepSeek-V4 Flash** (RP logic) и **GLM-5.2** (критика),
  ре-генерация **DeepSeek-V4-Pro**.
- **Gemopus** (Jackrong) сознательно **отказался** от «Claude-style CoT» (ссылается на arXiv 2604.06628).
- Прямое следствие для RU: thinking-канал обучается на английском → у нас зафиксирован RU-регресс
  `thought` (Pantheon-RU: трейс на англ., ответ на рус.) — `docs\research\why-ru-models.md` §5.2 п.2.

### 5.5. imatrix

- `zerofata/G4-MeroMero-31B-GGUF` и `...26B-A4B-GGUF` — iMatrix; `Artemis-31B-v1` — bartowski iMatrix.
- Наш рабочий квант — `mradermacher i1` (imatrix) `IQ3_XXS` для 31B (`docs\models.md`).
- В карточках авторов **imatrix-источник калибровки не раскрыт**; у WaifuGemma4 (не Gemma-4-RP-мерж)
  imatrix-калибровка заявлена на 10 языках (`rp-model-candidates.md` §5.2 п.6).

---

## 6. Русский язык в Gemma-4 — как его получают

**Прямого обучения на русском у Gemma-4-RP-мержей нет.** Механизмы, по которым русский всё же держится
(наши замеры — `docs\quality\sampling-quality.md`, `docs\research\why-ru-models.md`, `docs\models.md`):

1. **Мультиязычная база.** `google/gemma-4-31B-it` — 140+ языков в претрейне, 35+ «из коробки»,
   словарь 262K; RU в карточке не назван, кириллица бедна (~1.7× токенов) — `why-ru-models.md` §1.
2. **Осторожный мерж = сохранение языка.** `embed_tokens/lm_head=0` у доноров + низкая `density`
   + якорь на base → язык почти не тронут (Schattenblume, Giftige-Blume-v1 — RU 100 %).
3. **`lm_head`-only тюн** (StyleTune) → базовая мультиязычность цела (RU 96–100 % у 26B).
4. **RU-данные в обучении** — единственный сильный сигнал, но у **не-RP** модели:
   `hiwaifu-research/WaifuGemma4-26b-a4b-v1` (GRPO+LoRA r256, **17 языков, вкл. `ru`/`uk`**, 55.3 % побед
   на RU; RU 96 %, ~85 t/s) — `rp-model-candidates.md` §3, §5.
5. **Что ломает русский**: глубокие мульти-донорные мержи (Split-Untied 75 %), прививка чужой головы
   (StyleSwap 3.3/2.6), тяжёлые SFT/GRPO, heretic-heavy, низкий квант (`IQ2` → PPL ×5).
6. **Перевод EN→RU** — прямой путь к RU-RP, но **в карточках Gemma-4-RP не встречается**: это наш
   пайплайн-рекомендация (`docs\research\rp-datasets-en-ru.md` §6). Публичные RU-наборы (Arketov,
   krplt, IlyaGusev) в Gemma-4-RP-карточках не заявлены.

**Итог по данным:** ни одна из обязательных моделей не обучалась на русском; `language: en` (кроме
Ortenzya `en+jpn`). Русский — побочный эффект базы/метода, а не данных. Единственный найденный
не-английский тег среди всех разобранных — японский у Ortenzya.

---

## 7. Не проверено и противоречия

**Противоречия между карточками / тегами:**
1. **Glistening-Gem v2.1**: вступление — «stock `gemma-4-31B-it` as a base», Merge Details —
   база `densenet/Gemma-4-31B-StyleTune-heretic-ara`. Не сведено.
2. **Ateron**: HF-теги `base_model` неполны/вводят в заблуждение — DTV2 указывает 3 донора, а рецепт
   использует ещё `Dark-Mero-V3`; base задан локальным путём и в тегах отсутствует. MoonGem/Writers —
   то же (base = локальный `Gemma-4-Scotoma-V2`/`Gemma-4-it`). Фильтровать по тегам нельзя.
3. **Giftige-Blume-v1**: репо `Blazed-Forge/...`, подпись «by Nimbz», GGUF — `Nimbz/...`. Владелец/канон
   неоднозначны (в проекте используется Blazed-Forge-репо).
4. **Goetia-v1.6**: карточка честно «not uncensored», хотя RP-сообщество считает его RP-лидером;
   абliteration-версии — отдельно (`Goetia-v1.3-heretic`).

**Не проверено / неизвестно:**
- Внутренние датасеты (`zerofata/pretok`, `*.jsonl`, «Pantheon corpus», ReadyArt-движок) — состав,
  объём, язык, лицензия. Принимаем на веру.
- Данные **Artemis (TheDrummer), Gemopus (Jackrong), ConicCat Writer-D/F** — не раскрыты/нет README.
- Существование/доступность: `ConicCat/Gemma4-Writer-31B-D`/`-F` — репо есть, README нет (404).
  `Ateron/MoonGem-31B` и `Writers-31B-V2` по прямым именам из задания дали 401 — корректные ID:
  `Ateron/Gemma-4-MoonGem-31B`, `Ateron/Gemma-4-Writers-31B-V2` (проверены через HF API).
- Реальное качество/токсичность публичных наборов из §5.1 (кроме Sonnet3.5 — см. `rp-datasets-quality-check.md`).
- imatrix-источники калибровки у авторов.
- **Прямых доказательств, что PIPPA/LimaRP/CoSER использовались в Gemma-4 RP, нет** — это гипотеза
  из общего EN-пула, а не факт.

---

## 8. Источники (URL)

**Обязательные модели (HF):**
- https://huggingface.co/Ateron/Gemma-4-Dark-Thoughts-V2-31B · https://huggingface.co/Ateron/Gemma-4-Dark-Thoughts-31B
- https://huggingface.co/Nimbz/Schattenblume-31B · https://huggingface.co/Nimbz/Schattenblume-31B-GGUF
- https://huggingface.co/sophosympatheia/Glistening-Gem-31B-v2.1 · https://huggingface.co/sophosympatheia/Glistening-Gem-31B-v1.0
- https://huggingface.co/Blazed-Forge/Gemma-4-Giftige-Blume-31B-v1 · https://huggingface.co/Casual-Autopsy/Giftige-Blume-31B-v1-StyleSwap
- https://huggingface.co/Gryphe/Gemma-4-26B-A4B-StyleTune-V2 · https://huggingface.co/Gryphe/Gemma-4-31B-StyleTune
- https://huggingface.co/Naphula/Goetia-26B-A4B-v1.6
- https://huggingface.co/TheDrummer/Artemis-31B-v1.2 · https://huggingface.co/TheDrummer/Artemis-31B-v1
- https://huggingface.co/zerofata/G4-MeroMero-v2-31B · https://huggingface.co/zerofata/G4-MeroMero-31B · https://huggingface.co/zerofata/G4-MeroMero-26B-A4B
- https://huggingface.co/Blazed-Forge/Split-Untied-31B · https://huggingface.co/Ateron/Gemma-4-MoonGem-31B · https://huggingface.co/Ateron/Gemma-4-Writers-31B-V2

**Доноры / источники данных:**
- https://huggingface.co/ReadyArt/gemma-4-31B-it-scotoma-2 · https://huggingface.co/ReadyArt/Dark-Scarlett-v2.0-31B · https://huggingface.co/ReadyArt/Melody1437-31B
- https://huggingface.co/llmfan46/gemma-4-Ortenzya-The-Creative-Wordsmith-31B-it-uncensored-heretic
- https://huggingface.co/trohrbaugh/gemma-4-31b-it-heretic-ara
- https://huggingface.co/MRockatansky/Gemma-4-31B-storymaxxed
- https://huggingface.co/nbeerbower/Gemma4-Gutenberg-31B
- https://huggingface.co/AuriAetherwiing/G4-31B-Musica-v1
- https://huggingface.co/BirdToast/Gemma-4-31B-glimmer-rp-v0.1
- https://huggingface.co/Jackrong/Gemopus-4-31B-it
- https://huggingface.co/sophosympatheia/Mero-Artemis-31B-v0.3.1
- https://huggingface.co/Gryphe/Pantheon-Reasoning-31B-1.1 · https://huggingface.co/Gryphe/Pantheon-Reasoning-26B-A4B-1.1-V2

**HF-датасеты (ID из карточек):** `Gryphe/Sonnet3.5-Charcard-Roleplay`,
`schneewolflabs/Athanorlite-DPO`, `jondurbin/gutenberg-dpo-v0.1`, `nbeerbower/gutenberg2-dpo`,
`nbeerbower/gutenberg-moderne-dpo`, `nbeerbower/human-writing-dpo`, `sam-paech/gutenberg3-…`,
`EVA-UNIT-01/Lilith-v0.3`, `zerofata/Gemini-3.1-Pro-GLM5-Characters`, `zerofata/Instruct-Anime`,
`zerofata/Anime-AMA-Prose`, `zerofata/Roleplay-Anime-Characters`, `zerofata/Gemini-3.1-Pro-SmallWiki`,
`allura-forge/mimo-v2-pro-claude-distill-hs3`, `allura-forge/doubao-seed2.0-distill-multiturn-expr-rp`,
`Delta-Vector/Orion-Deepseek-V3-RP-Filtered`, `Delta-Vector/Orion-Deepseek-R1-RP-Filtered`,
`ToastyPigeon/kimi-stories-instruct`, `ToastyPigeon/kimi-rp-v3`, `ToastyPigeon/fujin-filtered-instruct`,
`Dxniz/Novelist-CoT`, `Gryphe/ChatGPT-4o-Writing-Prompts`; `ConicCat/*` (Gutenberg-SFT, Condor-SFT-Filtered,
Charcards_*, Lamp_P_Preference, C2_Sonnet_4_5, Ao3_Soft_Refusal, VSF, Mura_Books, MiniC2_V3.2, AntiRep).

**Papers / инструменты:** StoryScope — <https://arxiv.org/abs/2604.03136>;
«Elias in the Lighthouse, Again?» — <https://arxiv.org/abs/2605.26492>; Heretic — <https://github.com/p-e-w/heretic>;
ARA-PR — <https://github.com/p-e-w/heretic/pull/211>; mergekit — <https://github.com/arcee-ai/mergekit>;
форк Gemma-4 — <https://github.com/zerofata/mergekit/tree/gemma-4-support>; mergekit-exp — <https://github.com/EldritchLabs/mergekit-exp>.

**Внутренние (проект):** `docs\research\rp-model-candidates.md` (§7 Ateron, §8 CaliperBench, §9 «что держит русский»),
`docs\research\why-ru-models.md`, `docs\research\rp-datasets-en-ru.md`, `docs\research\rp-datasets-quality-check.md`,
`docs\models.md`, `docs\models\gemma-4-31b.md`, `docs\models\gemma-4-31b-rp-merges.md`, `docs\models\gemma-4-26b-a4b.md`.
