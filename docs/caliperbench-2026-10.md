# CaliperBench — RP-рейтинг моделей Gemma 4 (срез 2026-10-01)

Источник: **caliperbench.com** (лидерборд + `methodology.html` + `changelog.html`), открыт через Playwright
с прокси. Снапшот данных: **2026-10-01 21:20 UTC**, 590 моделей, ~330 полей. Полный дамп —
`downloads\caliperbench-2026-10-01.json`.

> Реестр проверенного — `docs\researched.md`. Наши собственные русские замеры — `docs\sampling-quality.md`.
>
> ⚠️ **Срез устарел.** Это дамп от 2026-10-01; после пересчёта v3 (05.10, literal errors) числа сильно
> сдвинулись (DTV2 RPv3 67.4 → **77.5**, Artemis ERP 75.9 → **54.9**). Свежий срез 2026-10-06 и правило
> отбора — `docs\models.md` «Кандидаты», `docs\rp-model-candidates.md` §8–9.

## Главное ограничение

**Язык в CaliperBench не измеряется вообще** (ни `language`, ни `russian`, ни `multilingual` — 0 полей).
Бенчмарк англоязычный (creative writing + RP). Поэтому его рейтинг **нельзя** переносить на русский;
про русский выводы — только по отзывам и нашим прогонам. Кванты бенчмарк тоже не тестирует.

## Gemma-4: позиции (режим Classic RP, всего 590 моделей)

«Внутри 31B» — ранг среди 123 Gemma-4-31B; «внутри 26B» — среди 65 Gemma-4-26B-A4B.

| Модель | RP (ранг/590) | Combined RP | Внутри группы |
| --- | ---: | ---: | --- |
| **Artemis 31B v1.2 Thinking** | **70.2 (#58)** | 60.9 | RP **#3** (31B) |
| **Artemis 31B v1.2** | **69.2 (#80)** | 62.6 | RP **#9** (31B) |
| **Boulesis 26B-A4B Thinking** | 69.1 (#83) | **66.7 (#10)** | RP **#2**, Comb #2 (26B) |
| **Boulesis 26B-A4B** | 68.2 (#107) | 64.9 (#44) | Comb #5 (26B) |
| Isometry Fabled-Persona 31B | 67.7 (#126) | 65.5 (#26) | Comb #14 (31B) |
| MeroMero 31B Heretic Unc. | 66.4 (#172) | 63.8 (#81) | RP #30, Comb #43 |
| **StyleTune 31B** (Gryphe) | 65.7 (#204) | 65.6 (#23) | Comb **#12** |
| Gembrain 31B | 64.9 (#245) | 64.3 (#62) | Comb #36 |
| **Dark-Thoughts V2 31B** (наш) | **63.8 (#291)** | 64.3 (#67) | Comb #38, RP #70 |
| Gemopus 31B | 62.2 (#346) | 61.3 | RP #85 |
| Ortenzya-Creative-Wordsmith | 61.6 (#366) | 56.3 | Comb #115 |
| Gemma-4-31B-Isometry-RP (maldv) | **41.0 (#539)** | 29.5 | **#123/123**, collapse 6.5 % |

Для контекста: **база Gemma-4-31B-Instruct** RP 60.8 (#385), **база 26B-A4B** RP 63.5 (#309) —
то есть многие RP-тюны **снижают** RP-скор относительно базы; лидеры (Artemis, Boulesis) — исключение.

## Выводы

- **Dark Thoughts V2 — не лидер.** По RP он середняк верхней трети (63.8, #291): проседает именно в
  classic RP, при этом хорош в ERP/DRP. Его обгоняют Artemis (v1.2 и Thinking), Boulesis,
  Isometry-Fabled, StyleTune (по Combined), MeroMero.
- **Лидер RP среди Gemma-4 — Artemis-31B-v1.2** (RP 69.2, #9 из 123; Thinking 70.2, #3).
  Сообщество (r/LocalLLaMA) подтверждает: Artemis «заметно лучше оригинала по сторителлингу».
- **Boulesis-26B-A4B** — лучший Combined RP (Thinking #10), MoE, быстрый.
- **StyleTune-31B** — лучший Combined RP среди «ум-сохраняющих» (только `lm_head`), #23.
- **Isometry-RP (maldv) — провал** (41.0, последний; collapse 6.5 %) — «эталонная Isometry» по этим данным
  не работает; не путать с Isometry **Fabled-Persona** (67.7).
- **Про русский** — данных нет ни у одной модели. Единственный Reddit-сигнал о мультиязычности вообще:
  у **MeroMero** «multilingual writing ability was degraded» (r/SillyTavernAI, 2026-05-19). Наши замеры:
  Dark Thoughts V2 96–100 %, StyleTune-26B 100 % (см. `sampling-quality.md`).

## Не подтверждено

- Перенос RP-рейтинга (английский) на русский — нельзя без нашего прогона.
- Устойчивость к кванту (IQ2/IQ3) на русском — гипотеза «merge держит квант лучше», прямых измерений нет
  (хотя у DTV2 Slop 41.2 #296 и адаптивность 79.8 % — хорошие).
- Прямых A/B-постов «X vs Dark Thoughts V2» в Reddit не нашлось.

## Источники

- https://caliperbench.com/ · https://caliperbench.com/methodology.html · https://caliperbench.com/changelog.html
- https://huggingface.co/Ateron/Gemma-4-Dark-Thoughts-V2-31B (двухфазный mergekit, тег `en`)
- Reddit: `1th7q0q` (MeroMero), `1vpzrb3` (Gembrain/Artemis), `1ucy863` (Artemis vs база), `1u16pm2` (база 31B)
