# RP-кандидаты вне Gemma: Qwen 3.5/3.6/3.8, Mistral, альтернативы

Внешний ресёрч, срез **2026-10-07**. Повод: поле Gemma-4 (31B и 26B-A4B) в проекте исчерпано
([docs\research\rp-model-candidates.md](rp-model-candidates.md), [docs\researched.md](../researched.md) §10–11), нужен другой класс моделей.
Здесь — что есть у актуальных **Qwen 3.5/3.6/3.8**, **Mistral/Ministral** и **альтернатив** (Nemotron,
GLM), с фильтрами «есть GGUF под 16 ГБ» и «есть зацепка за русский».

Методика отбора — та же, что в §9 `rp-model-candidates.md`: **CaliperBench V3** (`downloads\CalibreV3.csv`,
440 моделей, парсер [bench\parse_caliper.py](../../bench/parse_caliper.py)) как генератор кандидатов + метаданные HF (тип: merge/finetune,
base, доноры). Caliper **англоязычный и язык не измеряет** — это только сигнал «стоит ли смотреть»; вердикт
даёт наш RP-харнесс ([docs\quality\rp-quality-eval.md](../quality/rp-quality-eval.md), 2 сценария — скрин). Наши собственные RP-замеры на
Qwen уже есть для **баз** ([docs\quality\base-models-rp-eval.md](../quality/base-models-rp-eval.md)): обе базовые Qwen 3.6/3.8 слабы в роли —
но это базы, не тюны.

> ⚠️ Числа Caliper v3 — «thinking» и non-think варианты вперемешку, scanner-specific; сравнивать только как
> ориентир и внутри одного генератора. Наши баллы и их число несравнимы напрямую.

---

## 1. Майнинг CaliperBench V3: кто вообще есть

| Семейство | В дампе (V3) | Комментарий |
| --- | ---: | --- |
| Gemma | 109 | уже разобрано |
| Qwen (3.5/3.6/3.8 + старые) | 55 | **основной новый пул** |
| Mistral / Nemo / Magistral | 11 | классика слаба, но есть новые модели |
| Nemotron (NVIDIA) | 3+ | альтернатива, есть GGUF |
| GLM | 2 | API-класс, локально не берём |

### 1.1. Qwen: топ по RP v3 (non-truncated, с метаданными)

`FT` — finetune, `MRG` — merge. `base` — из HF-метаданных (10-01 dump, join по hf_id).

| # | Модель (автор) | Тип | base | RP | ERP | DRP | Comb | GGUF |
| --: | --- | :-: | --- | --: | --: | --: | --: | --- |
| 23 | **Serenity 27B** (ReadyArt) | FT | Qwen3.8-27B | **78.5** | 44.4 | 52.7 | 60.9 | ✅ ReadyArt/mradermacher |
| 7 | **Swift 27B** (ukisai) | FT | Qwen3.8-27B | 77.6 | 39.4 | 55.7 | 60.0 | ✅ **у нас на диске** |
| 281 | **Anansi 35B-A3B** (BlueNipples) | MRG | Qwen3.6-35B-A3B | 75.4 | 44.9 | 54.8 | 60.1 | ✅ mradermacher |
| 298 | **Anko 27B** (allura-org) | FT | ArliAI/Qwen3.5-27B-Derestricted | 75.2 | 51.1 | 63.8 | 63.9 | ✅ bartowski/mradermacher |
| 1 | Qwen3.8-27B **Base** (Alibaba) | Base | — | 74.0 | 25.1 | 41.4 | 51.0 | ✅ (наш IQ2_XXS) |
| 13 | **RICO 27B** (darkc0de) | FT | Qwen3.8-27B | 73.3 | 46.8 | 46.3 | 57.4 | ✅ XORTRON/RICO-GGUF |
| 15 | **Synthia 4 27B** (migtissera) | FT | Qwen3.8-27B | 72.9 | 43.6 | 59.5 | 59.8 | ❓ карточка 401 |
| 170 | **Genesis Hermes V7 35B-A3B** (LuffyTheFox) | FT | HauhauCS/Qwen3.6-35B-A3B-… | 72.4 | 52.5 | 47.1 | 58.5 | ✅ (568k загрузок) |
| 11 | **Heimdallr 27B** (ReadyArt) | FT | Qwen3.8-27B | 71.3 | 27.8 | 45.8 | 51.5 | ✅ ReadyArt |
| 76 | **Qwen3.6-27B Heretic2** (DavidAU) | FT | Qwen3.6-27B | 70.7 | 45.6 | 64.4 | 60.5 | ✅ DavidAU/mradermacher |
| 162 | **Qwen3.6-27B Heretic SDFT v1.2** (ReadyArt) | FT | Qwen3.6-27B | 69.7 | 57.2 | 36.9 | 55.8 | ✅ mradermacher |
| 6 | **Dark Scarlett 27B v2.0** (ReadyArt) | FT | Qwen3.8-27B | 69.3 | 51.9 | 38.6 | 54.7 | ✅ ReadyArt/mradermacher |
| 301 | **Qwen3.6-35B-A3B Heretic Uncensored** (llmfan46) | FT | Qwen3.6-35B-A3B | 66.2 | 56.5 | 47.8 | 56.8 | ✅ Native-MTP |
| 340 | **StyleTune 35B-A3B** (Gryphe) | FT | Qwen3.6-35B-A3B | 65.8 | 52.3 | 43.3 | 54.3 | ✅ mrademacher |
| 334 | **Zwielicht 27B** (Nimbz) | **MRG** | Qwen3.8-27B + 5 ReadyArt/heretic | 31.3* | 31.2 | 26.5 | 28.2 | ✅ mradermacher |
| 273 | Qwen3.6-27B **Base** (Alibaba) | Base | — | 41.2 | 39.7 | 45.5 | 40.0 | ✅ (наш Q2_K_XL) |
| 314 | Qwen3.5-35B-A3B **Base** (Alibaba) | Base | — | 62.6 | 21.8 | 21.5 | 39.5 | ✅ |

\* У Zwielicht-27B расхождение think/no-think (Thinking-вариант провалился, 15.1) — смотреть non-think.

**Читать так.** Наверху — **плотные 27B-финтюны Qwen3.8-27B** (ReadyArt, ukisai, allura-org, darkc0de) и
**MoE 35B-A3B** (Anansi, Genesis Hermes). То есть новый пул — ровно там, где нам удобно: 27B dense
(~18–28 t/s с MTP) и 35B-A3B MoE (~70–85 t/s).

### 1.2. Mistral / Ministral (классика слаба, но есть новинки)

| # | Модель | Тип | base | RP | ERP | DRP | GGUF |
| --: | --- | :-: | --- | --: | --: | --: | --- |
| 369 | **Skyfall 31B v4.2** (TheDrummer) | FT | **Magistral-Small-2509** | 67.7 | 56.0 | 48.7 | ✅ TheDrummer/bartowski |
| 416 | **Magnum v4 12B** (anthracite-org) | FT | Mistral-Nemo | 65.0 | 49.4 | 58.2 | ✅ |
| 171 | **Ministral 3 14B Instruct** (mistralai) | Base | Ministral-3-14B-Base | 63.0 | 43.3 | 39.1 | ✅ |
| 317 | **Maginum-Cydoms 24B** (Casual-Autopsy) | MRG | MS 3.2 + Drummer-мержи | 59.8 | 51.2 | 46.6 | ✅ |
| 317 | Cydonia/Magidonia 24B v4.3 (TheDrummer) | FT | MS 3.2 | 12–24 | 36–39 | 27–44 | ✅ |
| 363 | Mistral Nemo Instruct 2407 (base) | Base | — | 24.7 | 23.1 | 29.2 | ✅ |
| 367 | Mistral Small 3.1 24B Instruct (base) | Base | — | 4.2 | 1.6 | 3.7 | ✅ |

Плюс **Nemotron 3.5 Lightning 30B-A3B** (NVIDIA, base) — RP 62.2 / DRP 58.6, есть GGUF (ggml-org, unsloth).

**Вывод по Mistral (по англоязычному Caliper):** старая школа (Nemo/Small/Cydonia/Magnum/CD) — **до 66 RP,
ниже класса Qwen-финтюнов**; в чисто английском RP «лидера» на Mistral нет. Новинка **Ministral 3 14B**
(RP 63, база) и **Skyfall v4.2** на Magistral (67.7) — единственные, кто заходит на территорию, но обе
**уступают Qwen3.8-тюнам**.

> ⚠️ Но это **англоязычная** метрика. У Mistral есть структурное преимущество, которого нет у Gemma:
> **Mistral Small 3.2 и Magistral Small официально поддерживают `ru`** (24+ языков, вкл. `uk`), и под них
> существует **целый русскоязычный RP-ниш** — см. §2.5. Именно там Mistral становится интересен.

---

## 2.5. Mistral deep-dive: русскоязычный RP-ниш (главная находка)

Отдельный пласт моделей, который англоязычный Caliper вообще не замечает (там их просто нет):
**русскоязычные RP-мержи и финтюны на Mistral**. Это прямое попадание в наш главный фильтр (русский),
тогда как топовые Qwen3.8-финтюны помечены `language: en`.

### Три линии

| Линия | Модели | База | Язык | Квант под 16 ГБ | Заметка |
| --- | --- | --- | --- | --- | --- |
| **Mistral-Nemo 12B** (limloop) | **LucidFaun-RP-RU**, **Runeweaver-RP-RU**, Faun-RP-RU, Hydra-RP-RU | dreamgen/lucid-v1-nemo, Saiga, Vikhr | **ru, en** | Q4_K_M 7.5 / Q6 10.1 | RU-native RP; Multi-SLERP; uncensored; 32k ctx |
| **Mistral-Nemo 12B** (Aleteian) | **Pathfinder-RP-12B-RU** | **IlyaGusev/saiga_nemo_12b** + NemoMix + Wayfarer | ru | i1-Q4_K_M 7.5 | breadcrumbs-TIES; RU-база Saiga |
| **Mistral Small/Magistral 24B** | **Naphula/Slimaki-Tavern-24B-v1.3**, Morax-24B-v2 | Magistral-Small + Morax | **ru** в списке 10 | i1-IQ3_XXS 9.3 / Q3_K_M 11.5 | multi_fusion merge, uncensored RP/ERP, `ru` в тегах; автор — Naphula (Goetia) |
| **Qwen3.5-9B** (katafiek) | **Katarau-9B-ru-RP-nsfw** | Qwen3.5-9B + ARA-heretic | **ru, en** | Q4_K_M 5.6 / Q6 7.4 | LoRA-SFT на **41.7M токенов русского** RP-датасета; no-think |

### Детали

- **limloop/MN-12B-Runeweaver-RP-RU** — Multi-SLERP трёх: `LucidFaun-RP-RU` (RU-RP, uncensored) +
  `Kinggaroo-12b-v2` (логика) + `Omnino-Obscoenum` (стиль/эрудиция). Карточка: русский RP, tool-calling,
  без морализаторства. `LucidFaun` собран SLERP'ом с `dreamgen/lucid-v1-nemo` (точечно снимали цензуру в
  поздних MLP). Рекомендованный сэмплинг: temp ≤0.5, при 0.8 — top_k 20; проверенный контекст 8k
  (у Nemo — 32k). GGUF: свой + `mradermacher ...-i1`.
- **limloop/MN-12B-Hydra-RP-RU** — TIES-мерж «Pathfinder-RP + Vikhr/Dostoevsky-стиль» → **русская
  литературность** как заявленная цель.
- **Aleteian/Pathfinder-RP-12B-RU** — анкор на **Saiga Nemo 12B** (русскоязычная инструкт-модель
  Ильи Гусева) + NemoMix-Unleashed + Wayfarer; `breadcrumbs_ties`, чекпоинт chatml. Есть кванты
  (mradermacher, roleplaiapp — под RP-платформу).
- **Naphula/Slimaki-Tavern-24B-v1.3** — 2-стадийный `multi_fusion`; родители: `Morax-24B-v2`,
  `Maginum-Cydoms-24B-absolute-heresy`, `Slimaki-24B-v1.2`; uncensored RP/ERP, теги `ru`+9 языков;
  шаблон Mistral Tekken/ChatML. Именно этот **i1-GGUF** — самый скачиваемый в своей семье (~26k).
- **katafiek/Katarau-9B-ru-RP-nsfw** — ARA-abliterated Qwen3.5-9B + **LoRA SFT (r128) на чистом русском
  RP-датасете** (фанатская проза, аниме-архетипы, NSFW; ~2 % `<think>`). Рекомендация карточки — **без
  thinking**, temp 0.65 / min-p 0.05 / rep 1.05, ChatML. Самый лёгкий и быстрый вход (9B, 5.6 ГБ).

### Почему это важно

1. **Mistral официально многоязычен** (Small 3.2 / Magistral — `ru`,`uk` в языке) — база не «сыпется» на
   кириллице, как англо-only Gemma-тюны; RP-мержи поверх неё сохраняют русский по построению.
2. **Есть готовые RU-native авторы** (limloop, Aleteian) — нам не надо надеяться, что англ. финтюн
   удержит русский; можно брать модели, которые **обучались/мержились на русском**.
3. **Цена входа низкая**: 12B Q4 ~7.5 ГБ, 9B Q6 ~7.4 ГБ, 24B i1-IQ3 ~9–10 ГБ — влезают свободно, dense
   12B/9B без спекуляции быстрее наших 31B Gemma.
4. **Ограничения:** Caliper их не мерил (в дампе нет) — RP-качество **неизвестно**; ниши малоскачиваемые
   (десятки-тысячи загрузок), поэтому это ставка на «русскость», а не на проверенный RP-класс.
   Обязательно прогонять нашим харнессом, и особенно смотреть **«Чисто %»** и TTR (RU-native ≠ хорошая проза).

---

## 2. GGUF и размеры (что реально влезает в 16 ГБ)

Кванты, указанные ниже, **влезают в 16 ГБ** (для 27B dense — IQ3/Q3-класс ~11–14 ГБ; для 35B-A3B MoE —
IQ3_XXS ~13.6 ГБ). В скобках — есть ли **MTP-драфт** (спекуляция) и мультимодальность.

| Модель | GGUF-репо | Мин. квант под 16 ГБ | Особенности |
| --- | --- | --- | --- |
| **Swift 1.5 27B** | `ukisai/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF` | **IQ2_S-mtp 8.95 ГБ (у нас)**; IQ3_XXS ~11 ГБ | **MTP-драфт встроен**; gated; RP-фокус — нет (reasoning/efficient) |
| **Serenity 27B** | `ReadyArt/Serenity-27B-GGUF`, `mradermacher/Serenity-27B-i1-GGUF` | Q3_K_M 13.5 / i1-IQ3 ~11 ГБ | **MTP-файл + mmproj**; apache-2.0, unaligned |
| **Dark Scarlett v2.0** | `ReadyArt/Dark-Scarlett-27B-v2.0-GGUF` | Q3_K_M 13.5 / i1-IQ3 | MTP + mmproj |
| **Heimdallr 27B** | `ReadyArt/Heimdallr-27B-GGUF` | Q3_K_M 13.5 | dark-fantasy, MTP + mmproj |
| **Omega Convergence v1.0** | `ReadyArt/Omega-Convergence-27B-v1.0-GGUF` | Q3_K_M 13.5 | MTP + mmproj |
| **Anko 27B** | `mradermacher/Qwen3.5-27B-Anko-i1-GGUF` | **i1-IQ3_XXS 11.19** | Doubao-дистилляция, LoRA r64 |
| **Anansi 35B-A3B** | `mradermacher/Anansi-35B-A3B-i1-GGUF` | **i1-IQ3_XXS 13.62** | DARE-TIES merge + **lm-head swap** от Melody1437 |
| **Genesis Hermes V7 35B-A3B** | `LuffyTheFox/…-V7-GGUF`, mradermacher dequant | IQ3 ~13.6 | «Genesis» пост-обработка GGUF; 568k загрузок |
| **RICO 27B** | `darkc0de/XORTRON-RICO-v3-GGUF` | IQ3/S ~11–12 | abliterated/heretic, «criminal» research; en |
| **llmfan46 Qwen3.6-27B heretic v2** | `llmfan46/…-Native-MTP-Preserved-GGUF` | IQ3 | **нативный MTP сохранён** |
| **Skyfall v4.2 31B** | `TheDrummer/Skyfall-31B-v4.2-GGUF` | Q2_K 11.73 / Q3_K_M 15.2 | dense → ~16 t/s; Magistral base |

Самый дешёвый шаг — **Swift 1.5 уже на диске** (`I:\...\ukisai\Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF\…IQ2_S-mtp`),
RP-качество которого мы **не измеряли** (только скорость). Ноль скачиваний.

---

## 3. Механика и зацепка за русский (гипотезы, по аналогии с Gemma)

Наши выводы по Gemma ([docs\research\why-ru-models.md](why-ru-models.md), `ruled`): язык держит не «тип модели», а
**сохранность головы/эмбеддингов и мелкость дельт**. Переносим на Qwen:

| Признак | Кандидаты | Ожидание по RU |
| --- | --- | --- |
| **Финтюн на Qwen-базе** (эмбеддинги/голова целы) | ReadyArt (Serenity/Dark Scarlett/Heimdallr), 27B Heretic SDFT | лучше — Qwen-токенизатор многоязычнее Gemma-го |
| **LoRA-дистилляция** (узкая) | Anko (r64) | средне-хорошо, но `language: en, zh` — RU не заявлен |
| **Merge с `lm_head`-прививкой** | **Anansi** (lm-head от Melody1437) | ⚠️ **тот же механизм, что дал 17–0 % RU у Gemma-StyleSwap** — главный флаг риска |
| **«Genesis» GGUF-постобработка** | Genesis Hermes V7 | заявлен `multilingual`; метод трогает SSM-тензоры — RU не контролировался |
| **Heretic/abliteration-heavy** | RICO, Heretic2, llmfan46, Zwielicht | ⚠️ калибровка на англ. refusal → RU-риск (как у Gemma) |

Ключевое отличие от Gemma: **базовый Qwen3.8 мультиязычен** (кириллица токенизируется нормально), поэтому
даже англоязычный RP-финтюн имеет шанс удержать русский лучше, чем Gemma-финтюн. Это **проверяемая гипотеза**,
а не факт: RP-карточки ReadyArt/Anko помечены `language: en` (без `ru`).

Отдельно: у готовых **ReadyArt**-репозиториев и Swift в комплекте лежат **MTP-драфты** — на 27B dense
спекуляция даёт ×1.3–1.9 (по нашему Swift-логу), т.е. ~28→40+ t/s. Это снимает главный минус dense-27B
против MoE.

---

## 4. Рекомендуемая первая волна (скрин 2 сцены, наши судьи)

Порядок — по цене/информативности. Всё — RP-скрин ([bench\quality\prompts\scenarios_rp.json](../../bench/quality/prompts/scenarios_rp.json)),
сначала nothink, при рабочем thinking — второй прогон.

0. ~~**Swift 1.5 27B** — **без скачивания**~~ — **сделано (2026-10-07): ❌ не RP-модель.** Скрин
   (2 сцены, nothink/think, 2 судьи): **3.42 Gemma / 2.77 Qwen**, персонаж 2.2 · инициатива 1.9; он
   efficient-reasoning/кодинг-тюн, не RP. Вердикт о классе Qwen3.8-финтюнов им не закрывается — переходим
   к п.1. Детали — [docs\quality\rp-quality-eval.md](../quality/rp-quality-eval.md) §5.11.
1. **ReadyArt Serenity 27B** (Q3_K_M 13.5 или i1-IQ3) — лидер Caliper по Qwen RP, есть MTP. Тот же автор,
   чьи `scotoma-2`/`Melody1437` стоят под топовыми Gemma-мержами → «мержиста знаем, теперь его Qwen».
2. **Anko 27B** (i1-IQ3_XXS 11.19) — другой метод (LoRA Doubao), высокая Combined (63.9).
3. **Anansi 35B-A3B** (i1-IQ3_XXS 13.62) — быстрый MoE + **контроль «lm-head swap ломает RU?»** на Qwen.
4. **Genesis Hermes V7 35B-A3B** — самый популярный (568k), MoE, заявлен multilingual.
5. **RU-native Mistral-ветка** (§2.5) — то, чего у Gemma нет: **Runeweaver-RP-RU 12B** (Q4 7.5 ГБ) and
   **Katarau-9B-ru-RP-nsfw** (Q6 7.4 ГБ); при подтверждении — **Slimaki-Tavern-24B** (i1-IQ3 9.3 ГБ).
   Эти модели *обучались/мержились на русском*, а не «надеются» его удержать — приоритет выше, чем
   англоязычный контроль.
6. Mistral-контроль (по остатку): **Skyfall v4.2 31B** Q3_K_M — держит ли англо-ветка Mistral планку.

Если лидер первой волны возьмёт 3.4+ у строгого судьи при Чисто ≥ 90 % — гнать полным набором
(`scenarios_rp_full.json`) и сравнивать с Gemma-лидерами (DTV2 / Schattenblume / Giftige-Blume-v1).

---

## 4.1. Топ-5 «попробовать» (≥20B, по запросу пользователя)

Нижняя граница — **≥20B** (правило в [AGENTS.md](../../AGENTS.md)): RU-native 9B/12B (Katarau, Runeweaver, Pathfinder)
**исключены**. Ниже — лучшие по Caliper v3 среди ≥20B с GGUF под 16 ГБ, с учётом обоих режимов.
Числа Caliper — **англоязычные**, русский не измерен; у ⚠️-моделей высокий балл только в **think**.

| # | Модель (автор) | База | RP (plain / think) | ERP | DRP | Comb | Квант ≤16 ГБ | Зачем |
| -: | --- | --- | ---: | --: | --: | --: | --- | --- |
| 1 | **Serenity 27B** (ReadyArt) | Qwen3.8-27B (FT) | 32.3 / **78.5** ⚠️think | 44.4 | 52.7 | 60.9 | i1-IQ3_M 12.8 / Q3_K_M 13.5 | топ Qwen3.8-RP, есть MTP |
| 2 | **Anko 27B** (allura-org) | Qwen3.5-27B (FT, LoRA) | —/ **75.2** ⚠️think | 51.1 | **63.8** | **63.9** | i1-IQ3_XXS 11.2 | лучший Combined среди Qwen-финтюнов |
| 3 | **Genesis Hermes V7 35B-A3B** (LuffyTheFox) | Qwen3.6-35B-A3B (FT) | **72.4** / — | 52.5 | 47.1 | 58.5 | i1-IQ3_XXS ~13.6 | **надёжный non-think**, быстрый MoE, 568k загрузок, `multilingual` |
| 4 | **Anansi 35B-A3B** (BlueNipples) | Qwen3.6-35B-A3B (merge) | 58.1 / **75.4** ⚠️think | 44.9 | 54.8 | 60.1 | i1-IQ3_XXS 13.6 | merge + **lm-head swap** (тест механизма на Qwen, RU-риск) |
| 5 | **Skyfall 31B v4.2** (TheDrummer) | **Magistral-Small** (Mistral) | **67.7** / — | **56.0** | 48.7 | 57.6 | Q2_K 11.7 / Q3_K_M 15.2 | не-Qwen контроль, стабильный non-think; dense → ~16 t/s |

**Если хочется шире:**
- **Gleam 30B** (ConicCat; база **`meta-models/Muse-Glimmer-30B`** — новое семейство Meta) — think 75.4,
  **DRP 70.2**, Comb 65.1; i1-IQ3_XXS 11.1. Но `language: en`, think-зависим, квант свежий.
- **Eurydice 24B v3.5** (aixonlab, Mistral) — plain 68.7 / DRP 59.9; **Dans-PersonalityEngine 24B**
  (PocketDoc, Mistral-Small-3.1) — plain 67.3 / ERP 60.3, популярная (bartowski); обе `language: en`.
  **Dans проверен (2026-10-07):** русский держит **100 %** (тег `en` не помешал — Mistral-Small-3.1
  многоязычна), но как **character-RP слаб** (Qwen-судья **2.54** — самый низкий): персонаж 1.5,
  «быстрое согласие». Это personality/chat-модель, не RP. [docs\quality\rp-quality-eval.md](../quality/rp-quality-eval.md) §5.14.
- **Slimaki-Tavern-24B v1.3** (Naphula, Mistral, **`ru`**) — для русского в классе ≥20B.
- **G4-MeroMero-26B-A4B-heretic** (llmfan46, **Gemma-4-26B-A4B**) — **Comb 67.8, ERP 62.7, DRP 65.1** —
  объективно топ среди ≥20B, но Gemma (поле считаем пройденным; heretic → RU-риск).
  **Проверено 2026-10-07: Caliper не подтвердился** (Qwen-судья 3.15, ниже базы) — `rp-quality-eval.md` §5.13.

**Важная оговорка к топам Qwen:** у Serenity/Anko/Anansi высокий RP — **только thinking**; plain падает
(32/—/58). Поэтому при прогоне обязателен think-режим (и отдельно проверять, не «вываливает» ли Qwen3.8
reasoning в видимый ответ, как база — [docs\models.md](../models.md)). Genesis Hermes V7 и Skyfall — наоборот, сильны
в **non-think**.

## 4.2. Топ для **non-think** (≥20B, основной режим)

Пользователь работает **без thinking** и хочет скорость. Это меняет картину: у Serenity/Anko/Anansi высокий
балл был **только в think** — из шорт-листа они выпадают. Зато **MoE** (26B-A4B, 35B-A3B) даёт 60–85 t/s
против ~20 у dense 27–31B. Ниже — ранжирование по **RP plain (non-think)**.

| # | Модель (автор) | Архитектура | RP non-think | ERP | DRP | Comb | Скорость | Квант ≤16 ГБ |
| -: | --- | --- | ---: | --: | --: | --: | --- | --- |
| 1 | **Genesis Hermes V7 35B-A3B** (LuffyTheFox) | Qwen3.6-35B-A3B MoE | **72.4** | 52.5 | 47.1 | 58.5 | ~70–85 t/s | i1-Q2_K 13.3 / IQ3_S 15.6 |
| 2 | **Melody1437 35B-A3B** (ReadyArt) | Qwen3.6-35B-A3B MoE | 69.1 | 45.9 | 44.9 | 54.7 | ~70–85 t/s | i1-Q2_K 13.3 / IQ3_S 15.6 |
| 3 | **Eurydice 24B v3.5** (aixonlab) | Mistral dense | 68.7 | 47.8 | 59.9 | 58.9 | ~25 t/s | i1-IQ3_XXS 9.3 / Q4_K_M 14.3 |
| 4 | **Skyfall 31B v4.2** (TheDrummer) | Magistral dense | 67.7 | **56.0** | 48.7 | 57.6 | ~16 t/s | Q2_K 11.7 / Q3_K_M 15.2 |
| 5 | **Dans-PersonalityEngine 24B v1.3** (PocketDoc) | Mistral-Small-3.1 dense | 67.3 | **60.3** | 42.4 | 56.8 | ~25 t/s | i1-IQ3_XXS 9.3 / Q4_K_M 14.3 |

**Вывод по non-think:** среди **не-Gemma** и с оглядкой на скорость лучший выбор — **MoE Qwen3.6-35B-A3B**
(Genesis Hermes V7, Melody1437). Оба: (1) сильны именно в non-think, (2) дают ~70–85 t/s, (3) база Qwen3.6
мультиязычна (наш же замер: база Qwen3.6/3.8 в nothink — Чисто 100 %). Mistral-24B (Eurydice / Dans) — тоже
рабочие non-think, но dense и медленнее; Skyfall — самый медленный (dense 31B).

**Честная оговорка:** абсолютные лидеры non-think в Caliper — **Gemma-4 MoE**:
`G4-MeroMero-26B-A4B-it-uncensored-heretic` (llmfan46) **76.6 / Comb 67.8**, `Orion-26B-A4B-v1` (TheDrummer)
**74.0**, `G4-MeroMero-31B-…-heretic` **75.8**. Это **не те** Gemma-модели, что мы гоняли (Goetia/StyleTune/
base-26B), и они тоже **MoE и быстрые**. Если правило «Gemma пройдена» не абсолютно — это top по non-think.
Из RU-безопасных ≥20B остаётся **Slimaki-Tavern-24B** (Mistral, `ru`).

> **Проверено (2026-10-07):** `G4-MeroMero-26B-A4B-it-uncensored-heretic` (llmfan46, i1-IQ4_XS) на нашем
> RP-скрине **не подтвердил Caliper RP 76.6**: gemma 4.46 / Qwen **3.15** (ниже базы Gemma-26B 3.56 и
> лидеров); повторы, слабая память, пассивность; think сломан; RU 100 %, ~62 t/s. Подробности —
> [docs\quality\rp-quality-eval.md](../quality/rp-quality-eval.md) §5.13. То есть «Gemma пройдена» **подтверждается** и здесь.
> `Orion-26B-A4B-v1` (TheDrummer) и `G4-MeroMero-31B-…-heretic` — не проверялись.

## 5. Источники и ограничения

- CaliperBench V3 — `downloads\CalibreV3.csv` (срез 2026-10-06), парсер [bench\parse_caliper.py](../../bench/parse_caliper.py);
  метаданные (тип/base/доноры) — `downloads\caliperbench-2026-10-01.json`.
- HF: карточки и HF API (downloads/likes/язык/размеры файлов) — 2026-10-07.
- **Не проверено нашим стендом:** RP-качество, русский и скорость ни у одного из Qwen/Mistral-кандидатов
  (кроме баз, [docs\quality\base-models-rp-eval.md](../quality/base-models-rp-eval.md)). Caliper — англоязычный; язык он не измеряет.
- Кандидаты без GGUF/приватные (Synthia 4, будь-то 401) — на карандаше.
- Прошлый внешний разбор Gemma-поля — [docs\research\rp-model-candidates.md](rp-model-candidates.md); реестр — [docs\researched.md](../researched.md).
