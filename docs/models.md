# Модели: протестированные и кандидаты

Реестр моделей проекта. Числа краткие, подробности — по ссылкам в логах (`docs\`). Стенд:
RTX 4060 Ti 16 ГБ, сборка **b11382** (CUDA 12.4). Срез: 2026-10-07.

Обозначения: ✅ берём · ⚠️ с оговорками · ❌ не берём · 📌 по назначению (замеров нет) · 🗑 файл удалён с диска.
«Тестировали» = что реально измеряли в этом репозитории (остальное — не проверено).
**RP-средний** — среднее по 8 осям LLM-судьи (1–5): `bench\quality\rp_judge.py` + `judge_score.py`
(`docs\quality\rp-quality-eval.md`). Судьи — `gemma-4-26B-A4B` и `Qwen3.6-35B-A3B` MXFP4, разной строгости
(26B мягче ~4.4, Qwen строже ~3.3); балл читать вместе с вердиктом и отчётом о числе ответов (N).

## Протестированные: RP / креатив / русский

| Модель (автор) | RP-средний¹ | Квант(ы) | Что тестировали | Итог | Ключевые числа | Конфиг | Лог |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Gemma-4-31B Dark-Thoughts V2** (Ateron) | **4.55** (Think 4.97 · No 4.27) | i1-IQ3_XXS (+ i1-IQ2_S для PPL) | RP-связность; русский; скорость; PPL | ✅ эталон RP; Think > NoThink; RU 96–100 % | RP 23 · чат 30 · код 48 t/s; PPL RU 66 / 337 | `gemma4-31b-dark-thoughts-*.bat` | `docs\models\gemma-4-31b.md`, `docs\quality\rp-quality-eval.md` |
| **Gemma-4-31B Schattenblume** (Nimbz) | **4.55** (Think 4.59 · No 4.52) | i1-IQ3_XXS | RP-связность; русский; скорость | ✅ надёжный (логика/память/язык); слабость — быстро «сдаётся» в соблазне, самоповторы описаний | RP 22 (No) · 27 (Think) t/s; RU 100 % | `gemma4-31b-schattenblume-nothink-b11382.bat` | `docs\quality\rp-quality-eval.md` |
| **Gemma-4-31B Giftige-Blume v1** (Blazed-Forge) | **4.39** п.н. (Think 4.53 · No 4.33) | i1-IQ3_XXS | RP-связность (полный набор, 2 судьи); инициатива; русский | ✅ №1 Combined RP на доске; **лучшая инициатива (4.0)**; замена StyleSwap; Think слабее (4/18 пустых; безлимит — 2/18, но качество то же) | RP 22.3 (No) · 30.4 (Think) t/s; RU 99.9 % | `gemma4-31b-blume-v1-nothink-b11382.bat` | `docs\quality\rp-quality-eval.md` §5.7 |
| **Gemma-4-26B-A4B StyleTune-V2** (Gryphe) | 4.40 (Think 4.65 · No 4.19) | IQ4_XS | RP-связность; русский; скорость | ✅ быстрый RP; слабее на памяти/контексте | RP 63 (без спец.) · чат 70 t/s; RU 96–100 % | `gemma4-26a4b-styletune-*.bat` | `docs\models\gemma-4-26b-a4b.md`, `docs\quality\rp-quality-eval.md` |
| **Gemma-4-26B-A4B Goetia v1.6** (Naphula) | 4.23 (NoThink) | i1-IQ3_XXS | RP-связность; русский; скорость | ⚠️ быстрый MoE; путает сущности, шаблонные реплики; think-режим непригоден в llama.cpp | ~73 t/s; RU 100 % (RU-safe) / 83 % (пресет карточки) | `gemma4-26a4b-goetia-nothink-b11382.bat` | `docs\quality\rp-quality-eval.md` |
| **Gemma-4-31B Glistening-Gem v2.1** (sophosympatheia) | **4.13** (Think 3.60 · No 4.32) | i1-IQ3_XXS | RP-связность (полный набор, 2 судьи); русский; скорость | ✅ NoThink вровень с лидерами (4.32 Gemma / 3.35 Qwen), лучшая по памяти; Think сломан (7/18 пустых) | RP 22.7 (No) · 30.8 (Think) t/s; RU 100 % | `gemma4-31b-glistening-nothink-b11382.bat` | `docs\quality\rp-quality-eval.md` §5.6 |
| **Gemma-4-31B Artemis-31B-v1.2** (TheDrummer) | 3.90 (Think 4.29 · No 3.50) | i1-IQ3_XXS | RP-связность; русский; PPL; скорость | ❌ RP: речевая деградация в кашу при RU 92–96 % | RP 20–26 t/s; PPL RU 983 | `gemma4-31b-artemis-*.bat` | `docs\quality\rp-quality-eval.md`, `docs\research\why-ru-models.md` |
| **Gemma-4-31B-it heretic-ARA** (Heretic / mradermacher) | **4.44** (Think 4.52 · No 4.35) | i1-IQ3_XXS | RP (скрин, 2 судьи); русский; скорость | ⚠️ **база + ARA-abliteration, не RP-тюн**: память/инициатива ок, но голос персонажа слабый («fast-track» в соблазне; литературщина и опечатки в think); **think рабочий** | RP 24.7 (No) · 31.3 (Think) t/s; Qwen-судья 3.52; Чисто 83 % (No) / 100 % (Think) | `gemma4-31b-heretic-ara-{nothink,think}-b11382.bat` | `docs\quality\base-models-rp-eval.md` §4.3 |
| **Gemma-4-31B Giftige-Blume-StyleSwap** (Casual-Autopsy) | 3.76 (Think 3.84 · No 3.64) | i1-IQ3_XXS | RP-связность (полный набор, 2 судьи); русский | ❌ русский 3.3/2.6 — англ. вставки (прививка головы StyleTune); для RU не берём | RP 23.3 t/s; EN-стоп 4.89 | `gemma4-31b-styleswap-{nothink,think}-b11382.bat` | `docs\quality\rp-quality-eval.md` §5.6 |
| Gemma-4-31B **Split-Untied** (Blazed-Forge) | — | i1-IQ3_XXS | русский; скорость | ⚠️ RU 75 % → 96 % при temp0.4; RP НЕ меряли 🗑 | RP 23 t/s | `gemma4-31b-split-untied-*.bat` | `docs\models\gemma-4-31b-rp-merges.md` |
| Gemma-4-31B **G4-MeroMero-v2-31B-heretic** (zerofata) | — | i1-IQ3_XXS | только скорость (RP/чат/код/матем) | ⚠️ RP и русский НЕ тестили; `.bat` удалён 🗑 | RP 21 · код 45 t/s | — | `docs\models\gemma-4-31b-rp-merges.md` |
| Gemma-4-26B-A4B **WaifuGemma4** (hiwaifu-research) | — | i1-IQ3_XXS | только русский; скорость | ⚠️ RU 96 % на карточке, низкая T портит; RP НЕ меряли (по опыту — слабое) 🗑 | 85 t/s | `gemma4-26a4b-waifugemma-nothink-b11382.bat` | `docs\quality\sampling-quality.md` |
| Gemma-4-31B **StyleTune-31B** (Gryphe) | — | i1-IQ3_XXS | русский | ❌ непригоден (17–0 %), битый repack 🗑 | — | — | `docs\quality\sampling-quality.md` §5.4 |
| **Qwen3.6-35B-A3B Genesis Hermes V7** (mradermacher i1) | 3.35 (gemma 3.81 · **Qwen 2.90**) | i1-IQ4_XS | RP (скрин, **nothink**, 2 судьи); русский; скорость | ❌ **не апгрейд**: ниже базовых Qwen и нашего топа; персонаж/инициатива/память слабые; RU 100 % (Caliper 72.4 не подтвердился) | TG 41.6 t/s; IQ4_XS 17.9 ГиБ → offload, без MTP | `qwen36-35b-a3b-genesis-hermes-v7-nothink-b11382.bat` | `docs\quality\rp-quality-eval.md` §5.12 |
| **Gemma-4-26B-A4B G4-MeroMero it-uncensored-heretic** (llmfan46/mradermacher i1) | 3.81 (gemma 4.46 · **Qwen 3.15**) | i1-IQ4_XS | RP (скрин, 2 судьи); русский; скорость; think | ❌ **не апгрейд**: ниже базы Gemma-26B (Qwen 3.56) и лидеров; повторы (1.67), память-ловушка «Питер» (2/3 сида), пассивна в соблазне; RU **100 %**, быстрый MoE 62 t/s; **think сломан** (Чисто 17 %, утечка reasoning) | TG 62.1 t/s (No); 15.5 ГБ | `gemma4-26a4b-meromero-nothink-b11382.bat` (think непригоден) | `docs\quality\rp-quality-eval.md` §5.13 |
| **Dans-PersonalityEngine-V1.3.0-24b** (PocketDoc; база Mistral-Small-3.1) | **2.54** (gemma 3.94 · **Qwen 2.54**) | IQ4_XS | RP (скрин, nothink, 2 судьи); русский; скорость | ⚠️ **не character-RP** (personality/chat-тюн): персонаж 1.5, «быстрое согласие», пассивность; **русский держит чисто (100 %)**, хотя в карточке `en`; годится как RU/EN чат-компаньон | TG 18.9 t/s; 15.0 ГБ | `dans-pers13-nothink-b11382.bat` | `docs\quality\rp-quality-eval.md` §5.14 |

¹ N ответов: DTV2 10, Schattenblume 20, StyleTune 11, Goetia 11, Artemis 6 (часть пунктов судья пропустила);
Glistening 19, StyleSwap 21 (полный набор, два судьи); heretic-ARA 12 (скрин, два судьи).
**Масштаб чисел:** DTV2, Schattenblume, StyleTune, Goetia, Artemis, heretic-ARA — **2 сценария** (судья 26B);
Glistening, StyleSwap, Giftige-Blume-v1 — **полный набор** (средний Gemma; строгий Qwen ниже — см. «Полный набор»).
У «—» RP-бенчмарк не запускался.

### Полный набор (6 сценариев)

DTV2 и Schattenblume шли ноздря в ноздрю на 2 сценариях. Прогнали их на **расширенном наборе**
(`bench\quality\prompts\scenarios_rp_full.json`: +`tactics`, `mystery`, `group`, `everyday`) при **одинаковом
сэмплинге** (temp0.6 / min-p0.1 / top-k0), 6 сценариев × 3 сида × {think, no-think}; судья с полным
покрытием (`rp_judge_full1`).

| Модель | режим | N | ум | память | персонаж | инстр | иниц | рус | проза | повт | **Средний** |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Schattenblume | Think | 17 | 4.53 | 5.00 | 4.29 | 5.00 | 3.24 | 4.94 | 4.65 | 4.82 | 4.56 |
| DTV2 | Think | 18 | 4.39 | 4.72 | 4.28 | 5.00 | 3.83 | 4.94 | 4.50 | 4.72 | 4.55 |
| Schattenblume | NoThink | 17 | 4.12 | 4.53 | 4.29 | 4.41 | 3.00 | 5.00 | 4.65 | 5.00 | 4.38 |
| DTV2 | NoThink | 18 | 3.89 | 4.72 | 3.89 | 4.44 | 2.89 | 4.94 | 4.33 | 4.78 | 4.24 |
| **Schattenblume** | все | 34 | 4.3 | 4.8 | 4.3 | 4.7 | 3.1 | 5.0 | 4.6 | 4.9 | **4.47** |
| **DTV2** | все | 36 | 4.1 | 4.7 | 4.1 | 4.7 | 3.4 | 4.9 | 4.4 | 4.8 | **4.39** |

**Вывод:** расширение набора **не развело их решительно** — Schattenblume чуть впереди (4.47 против
4.39), а в think-режиме вообще паритет (4.56 / 4.55). Новые сцены (`tactics`, `mystery`, `group`)
**просадили инициативу у обеих** (3.0–3.4): обе склонны к «говорящим головам» без продвижения
сюжета. То есть 4.55 на 2 сценариях — реальный паритет одного класса, а не артефакт; выбор между
ними — по вкусу и скорости. Оговорка: судья 26B шумная (на батче 3 средние были 4.57 vs 4.30),
поэтому 0.08 разницы — в пределах её погрешности.

Панель из четырёх судей: два локальных (gemma-4-26B и Qwen3.6-35B, абсолютные оценки) чуть за
Schattenblume, а оба облачных **попарных** (space-bunny и deepseek-v4.1-flash) — за DTV2 (~2:1,
`docs\quality\rp-quality-eval.md` §5.5). То есть разница **на грани**, но при прямом сравнении чуть впереди
DTV2; один класс качества.

#### Сводка полного набора: все модели, NoThink, два судьи (2026-10-07)

Единая таблица для всего, что гоняли полным набором (те же сценарии, сэмплинг temp0.6/min-p0.1/top-k0
и те же судьи; NoThink — рабочий режим). Полный разбор — `docs\quality\rp-quality-eval.md` §5.6–5.7.

| Модель | Gemma (No) | **Qwen (No)** | инициатива (Gemma) | русский (Gemma/Qwen) | Вердикт |
| --- | ---: | ---: | ---: | ---: | --- |
| **Giftige-Blume-v1** (Blazed-Forge) | 4.33 | **3.35** | **4.00** | 4.83 / 4.00 | ✅ лучшая **инициатива**; №1 Combined Caliper |
| Schattenblume (Nimbz) | **4.38** | 3.28 | 3.00 | 5.00 / 4.25 | ✅ лидер по Gemma |
| Glistening-Gem v2.1 (sophosympatheia) | 4.32 | **3.35** | 3.71 | 4.86 / 4.17 | ✅ вровень с лидерами |
| Dark-Thoughts V2 (Ateron) | 4.24 | 3.11 | 2.89 | 4.94 / 3.92 | эталон |
| Giftige-Blume-StyleSwap (Casual-Autopsy) | 3.64 | 2.64 | 3.44 | 3.56 / 2.75 | ❌ англ. вставки (StyleTune-голова) |
| **base Gemma-4-26B-A4B-it** (базовая instruct) | 4.60* | **3.28** | 4.94* | 4.78 / 4.06 | ⚠️ baseline: у строгого судьи **вровень с Schattenblume** (3.28) и выше DTV2; *gemma-колонка — самооценка |

**Think:** у 31B-мержей часто пустые ответы (незакрытый `<channel|>`); безлимит бюджета у Blume снижает
пустые 4/18→2/18, но качества не добавляет. **Рабочий режим — NoThink.**
Строка **base Gemma-4-26B-A4B-it** — baseline (не RP-модель), добавлена для сравнения; её gemma-колонка —
самооценка, независима только Qwen-колонка (детали — `docs\quality\base-models-rp-eval.md`).
Полным набором **не гоняли** (только 2 сценария / судья 26B): StyleTune-26B (No 4.19), Goetia-26B (No 4.23),
Artemis-31B (3.90) — их числа в таблице «Протестированные» выше.

### Базовые instruct-модели (RP-скрин, 2026-10-07)

Не-RP модели, прогнанные тем же RP-харнессом (2 сценария, 3 сида, nothink/think, оба судьи) — это
**baseline**: сколько «добавляет» файнтюн. Полные таблицы, цитаты и оговорки — `docs\quality\base-models-rp-eval.md`.

| Модель | RP-средний (gemma / Qwen) | Квант | Вердикт | Конфиг |
| --- | ---: | --- | --- | --- |
| Gemma-4-26B-A4B-it (base) | 4.67* / 3.35 (nothink 3.56) | UD-IQ3_XXS | ⚠️ лучшая из базовых и **пригодный RP-baseline**: на скрине у строгого судьи выше DTV2/Schattenblume; *самооценка у gemma-судьи; повторы метафор, «сдаётся» в соблазне; think — утечка reasoning | `gemma4-26a4b-base-rp-nothink-b11382.bat` |
| Gemma-4-31B-it (base) | 4.51 / 3.45 (No 3.38 · Think 3.52) | UD-IQ3_XXS | ⚠️ **baseline 31B**: ≈ heretic-ARA (abliteration RP не меняет); **think рабочий** (6/6); у строгого судьи персонаж/инициатива 2.5–2.8, паттерн-циклы; Чисто 100 %, 18.5 t/s | `gemma4-31b-base-{nothink,think}-b11382.bat` |
| Qwen3.8-27B (base) | 3.98 / 3.21 | UD-IQ2_XXS | ❌ коротко/поверхностно, путает факты; think вываливает reasoning текстом | `qwen38-27b-base-rp-nothink-b11382.bat` |
| Qwen3.6-35B-A3B (base) | 4.06 / 2.96* | UD-Q2_K_XL | ❌ самый сухой и короткий, пассивный; think — незакрытый канал → пустой ответ | `qwen36-35b-a3b-base-rp-nothink-b11382.bat` |

\* Самооценка (судья совпадает с моделью). Все три в nothink дают «Чисто» 100 %; think нестабилен
у всех трёх. Вывод: **RP-файнтюн/мерж добавляет, но не всем одинаково** — базовая Gemma-26B на скрине
конкурентоспособна (выше DTV2/Schattenblume у строгого судьи), а базовые Qwen — на дне. Полный набор
для Gemma-26B — `docs\quality\base-models-rp-eval.md` §4.2.
Строка **Gemma-4-31B-it (base)** — тот же скрин, но 31B dense; **≈ heretic-ARA** (abliteration RP
не меняет), **think рабочий** (в отличие от остальных Gemma-31B-мержей). Разбор — §4.4.

## Протестированные: кодинг / универсальные

| Модель (автор) | Квант(ы) | Что тестировали | Итог | Ключевые числа | Конфиг | Лог |
| --- | --- | --- | --- | --- | --- | --- |
| **Qwen3.6-35B-A3B** (MoE 3B акт.) | Q2_K_XL | скорость: чат/код/матем/суммаризация; DFlash+ngram на коде; RP-скрин | ✅ чат/код/матем/длинные док-ты; ❌ RP слабо (базовая модель: сухо/коротко, think ломается) | чат 93 · код 111 · матем 121 · RP 82 t/s; RP-скрин 4.06/2.96 | `qwen36-35b-a3b-mtp-b11382.bat`, `...-dflash-code.bat` | `docs\models\qwen36-35b-a3b.md`, `docs\quality\base-models-rp-eval.md` |
| **Swift-1.5-Qwen3.8-27B** (ukisai) | IQ2_S-mtp | скорость: RP/чат/код/матем; **RP-скрин** | ⚠️ код/чат ок; **RP слабо** (не RP-модель, а efficient-reasoning): скрин 3.42 gemma / **2.77 Qwen**, персонаж 2.2 · инициатива 1.9; RU 100 % (No) / 83 % (Think) | RP 28 · чат 37 · код 36 t/s; RP-скрин — §5.11 | `swift-best-b11382.bat` | `docs\models\swift-1.5-27b.md`, `docs\quality\rp-quality-eval.md` §5.11 |
| **Qwen3.8-27B** (unsloth UD-IQ2_XXS) | UD-IQ2_XXS | кодинг; конфиг-аналог Swift (think/nothink); RP-скрин (базовая) | ❌ RP слабо (коротко/поверхностно; think вываливает reasoning); кодинг — по назначению | 8.39 Г; RP-скрин 3.98/3.21 · 26 t/s | `qwen38-27b-best*.bat`, `qwen38-27b-base-rp-nothink-b11382.bat` | `docs\quality\base-models-rp-eval.md` |

## Кандидаты

`Caliper RP_v3` — англоязычный ориентир (язык не измеряет), только сигнал «стоит ли смотреть». Числа
обновлены по свежему V3 (срез **2026-10-06**, `downloads\CalibreV3.csv`, парсер `bench\parse_caliper.py`).
Размер — файл `IQ3_XXS` под 16 ГБ. Отсортировано по приоритету, внутри — по RP_v3.
**Фильтр «что держит русский»** (Merge + якорь на base, у доноров `embed/lm_head=0`, низкая density;
не чистый финтюн) и полный шорт-лист — `docs\research\rp-model-candidates.md` §9.

| Приоритет | Модель (автор) | Зачем | RP / ERP v3 | GGUF / размер |
| --- | --- | --- | ---: | --- |
| высокий | **MoonGem-31B** (Ateron) | Мульти-донорный (7) рецепт того же автора, что DTV2 — «метод vs семья». ⚠️ по композиту сайдгрейд: Combined 68.0 (ниже DTV2/Glistening/Giftige), ERP 63.1 | 77.1 / 63.1 | bartowski / 12.4 Г |
| средний | **Twisted Cyclone 31B** (Cyclone-Labs) | Якорный, Pantheon + Novelist-Eclipse среди доноров | 73.3 / 65.9 | mradermacher / 11.25 Г |
| средний | **Froopert-31B** (Nimbz) | Якорный, 6 доноров + base | 73.3 / 64.1 | bartowski / 12.1 Г |
| средний | **Gembrain-31B** / **Gemsicle-31B** | Якорные, высокий ERP | 69.7 / 66.3 · 69.7 / 63.7 | mradermacher |
| средний | **Aura Prototype 26B-A4B** (EldritchLabs) | MoE, якорный, быстрый | 76.5 / 65.6 | mradermacher / 10.8 Г |
| средний | **Split-Untied-31B** (Blazed-Forge) | Повторный прогон RP-харнессом; **наш замер RU 75 %** — не приоритет | 74.3 / 66.6 | mradermacher / 12.8 Г |
| средний | **Prosopon-31B** (Nimbz) | 8 доноров | 71.1 / 62.6 | Nimbz/mradermacher / 11.8 Г |
| средний | **Novelist-Eclipse-31B** (Ateron) | Прозо-мерж того же автора | 66.5 / 65.8 | bartowski / ≈12 Г |
| средний | **Dark-Thoughts V1 31B** (Ateron) | Сравнение с V2 («поумнела ли») | — | bartowski / ≈12 Г |
| средний | **Boulesis-26B-A4B** (SubMaroon) | QK task-arithmetic + LoRA + StyleTune head | — | mradermacher / 10.8 Г |
| низкий | **Harmonia-31B** (virtuous7373) | ⬇️ свежий ERP обвалился + heretic | 68.4 / **52.7** | mradermacher / 11.25 Г |
| низкий | **G4-MeroMero-v2-31B-heretic** (zerofata) | Контроль «мерж лечит файнтюн»; свежий ERP низкий | 71.7 / 53.8 | mradermacher / 11.25 Г |
| низкий | **Merotheon-31B** (Casual-Autopsy) | Единственный с reasoning-донором (Pantheon); IQ3 GGUF нет | 68.9 / 64.1 | ❌ конвертить |
| низкий | **Writers-31B-V2** (Ateron) | «less Gemma», фикс нестабильности; GGUF нет | — | ❌ конвертить |
| низкий | **WaifuGemma4-26B-A4B** | RP не измеряли; свежий V3 даёт **RP 19.9** — слабо | 19.9 / 26.7 | mradermacher / 10.6 Г |
| низкий | Sphinsikus Chronist V2 31B (Blazed-Forge) | 6 доноров, якорный | 73.1 / 58.5 | mradermacher / 11.25 Г |
| низкий | Moonlight-Dusk 26B-A4B heretic (Vortex5) | MoE, heretic | — | mradermacher / 10.8 Г |

### Кандидаты вне Gemma (Qwen 3.5/3.6/3.8, Mistral, альтернативы)

Поле Gemma-4 исчерпано; внешний разбор других семейств (CaliperBench V3 + HF) — 
`docs\research\qwen-mistral-rp-candidates.md`. Кратко: новый пул RP — **финтюны Qwen3.8-27B** (ReadyArt
Serenity/Dark-Scarlett/Heimdallr, ukisai Swift, allura-org Anko) и **MoE 35B-A3B** (BlueNipples Anansi,
Genesis Hermes V7); Mistral/Ministral слабее (≤67), альтернатива — Nemotron 3.5 (62). Но у Mistral есть
**русскоязычный RP-ниш** (Mistral официально поддерживает `ru`): **limloop Runeweaver/Hydra-RP-RU 12B**,
**Aleteian Pathfinder-RP-12B-RU**, **Naphula Slimaki-Tavern-24B**, **katafiek Katarau-9B-ru-RP** (Qwen3.5-9B) —
обучались на русском, не «надеются» его удержать. Шаг без скачивания (Swift 1.5 27B) уже сделан:
**❌ не RP-модель** (3.42 Gemma / 2.77 Qwen) — `docs\quality\rp-quality-eval.md` §5.11. Проверен и
**Dans-PersonalityEngine-V1.3.0-24b** (Mistral-Small-3.1): русский держит 100 %, но character-RP слаб
(Qwen 2.54) — §5.14. Остальные — не проверены нашим харнессом.

### Облачные (API) — справочно (2026-10-07)

Проверка **облачных** моделей нашим RP-харнессом: **12 моделей DeepSeek/GLM × 4 судьи** (локальные
Gemma-26B и Qwen3.6 + облачные DeepSeek-Flash/Pro), через `bench\quality\api_rp_eval.py` и
`api_judge.py`; ключи — `.env`, gitignored. Это не локальные конфиги, а верхний референс.
По мягкому судье все **4.06–4.73** (выше локальных мержей 4.24–4.38), но **судьи расходятся**, а
DeepSeek-строки — **self-eval**. Лидеры: GLM-5.3 (Gemma 4.73), DeepSeek-Pro (Gemma 4.71),
GLM-4.7 (Qwen 3.91). У `glm-5.3`/`glm-5.3-flash` форсированный thinking течёт CJK-символами
в русский (Чисто 67–83 %). Полные таблицы — `docs\quality\cloud-api-rp-eval.md`.

## Ссылки

- Детали скорости — логи `docs\` по моделям; реестр проверенного — `docs\researched.md`.
- RP-качество (LLM-судья + средние баллы) — `docs\quality\rp-quality-eval.md`; сводный рейтинг Think/NoThink — `docs\quality\rp-ranking.md`.
- Внешний ресёрч, донор-граф, Ateron — `docs\research\rp-model-candidates.md`.
- Русский, PPL, артефакты — `docs\quality\sampling-quality.md`, `docs\research\why-ru-models.md`.
- Конфиги — `launch\b11382-cu124\`; наборы RP-оценки — `bench\quality\suites\suite_rp_eval_*.json`.
