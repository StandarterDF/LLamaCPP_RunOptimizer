# Рейтинг RP-моделей (выбор за 10 секунд)

**Что это:** одна цифра на модель — среднее по **4 судьям** (Gemma-4-26B, Qwen3.6-35B, DeepSeek-Flash,
DeepSeek-Pro), шкала 1–5, по 8 осям. Только **рабочие** модели и годные baseline — сверху вниз.

**Колонки:** `Type` — **Cloud** (API) или **Local** (GGUF); `RP` — средний балл 4 судей; `сц` — число
сценариев в прогоне (**6 строже**, на 2 было бы выше); `Примечание` — для **Local** скорость RP на
16 ГБ (наш стенд), для **Cloud** — цена за 1M токенов (input/output), USD.

**Как читать:** сравнивать только внутри таблицы. Судьи расходятся — подробности и per-judge числа:
`docs\quality\rp-quality-eval.md`, `docs\quality\cloud-api-rp-eval.md`. Отклонённые — `docs\models.md`.

![RP-рейтинг моделей](../images/chart_rp_ranking.png)

## Non-Thinking (основной режим)

| # | Модель | Type | RP | сц | Примечание |
| --: | --- | :--: | --: | --: | --- |
| 1 | **DeepSeek-V4-Pro** *(self-eval)* | Cloud | **4.01** | 2 | 0.66 / 1.98 USD за 1M |
| 2 | **DeepSeek-V4.1-Flash** *(self-eval)* | Cloud | **3.98** | 2 | 0.15 / 0.60 USD за 1M |
| 3 | **GLM-5.2** | Cloud | **3.90** | 2 | 1.4 / 4.4 USD за 1M |
| 4 | **GLM-4.7** | Cloud | 3.87 | 2 | 0.6 / 2.2 USD за 1M |
| 5 | **GLM-5** | Cloud | 3.83 | 2 | 1 / 3.2 USD за 1M |
| 6 | **StyleTune-V2 26B** | Local | **3.78** | 2 | ~66 t/s |
| 7 | base Gemma-4-26B-A4B-it *(baseline, self-eval)* | Local | 3.76 | 2 | ~55 t/s |
| 8 | **Boulesis-v2.1 26B-A4B** | Local | **3.74** | 2 | ~55 t/s; gemma-судья — та же база (родственная) |
| 9 | GLM-5.1 | Cloud | 3.70 | 2 | 1.4 / 4.4 USD за 1M |
| 10 | base Gemma-4-31B-it *(baseline)* | Local | 3.70 | 2 | ~18 t/s |
| 11 | **G4-MeroMero-26B-A4B-heretic** | Local | 3.70 | 2 | ~62 t/s |
| 12 | GLM-4.6 | Cloud | 3.64 | 2 | 0.6 / 2.2 USD за 1M |
| 13 | **Glistening-Gem v2.1 31B** | Local | 3.61 | 6 | ~23 t/s |
| 14 | **Gemma-4-31B heretic-ARA** | Local | 3.59 | 2 | ~25 t/s |
| 15 | **Schattenblume 31B** | Local | 3.59 | 2 | ~22 t/s |
| 16 | **Giftige-Blume-v1 31B** | Local | 3.58 | 6 | ~22 t/s |
| 17 | Goetia-26B-A4B v1.6 | Local | 3.55 | 2 | ~70 t/s |
| 18 | **Dark-Thoughts V2 31B** | Local | 3.51 | 2 | ~24 t/s |
| 19 | GLM-4.7-Flash | Cloud | 3.35 | 2 | **free** |
| 20 | GLM-4.5-Flash | Cloud | 3.28 | 2 | **free** |

## Thinking

| # | Модель | Type | RP | сц | Примечание |
| --: | --- | :--: | --: | --: | --- |
| 1 | **Dark-Thoughts V2 31B** | Local | **4.01** | 2 | ~27 t/s |
| 2 | **GLM-5.3** *(thinking форсирован)* | Cloud | 3.87 | 2 | 1.4 / 4.4 USD за 1M |
| 3 | **Schattenblume 31B** | Local | 3.83 | 2 | ~28 t/s |
| 4 | **StyleTune-V2 26B** | Local | 3.83 | 2 | ~60 t/s |
| 5 | base Gemma-4-31B-it *(baseline)* | Local | 3.81 | 2 | ~19 t/s |
| 6 | GLM-5.3-Flash *(thinking форсирован)* | Cloud | 3.81 | 2 | 0.15 / 0.50 USD за 1M |
| 7 | Gemma-4-31B heretic-ARA | Local | 3.77 | 2 | ~31 t/s |
| 8 | Giftige-Blume-v1 31B | Local | 3.75 | 6 | ~30 t/s |
| 9 | base Gemma-4-26B-A4B-it *(baseline, self-eval)* | Local | 3.61 | 2 | ~55 t/s |
| 10 | **Boulesis-v2.1 26B-A4B** | Local | 3.60 | 2 | ~59 t/s |
| 11 | Glistening-Gem v2.1 31B | Local | 3.41 | 6 | ~31 t/s |
| 12 | G4-MeroMero-26B-A4B-heretic | Local | 3.37 | 2 | ~66 t/s |

> Думающий режим у большинства 31B-мержей в llama.cpp **сломан** (пустые ответы / утечка reasoning) —
> рабочий режим по умолчанию **Non-Think**; в этой таблице только те, где think реально работает.

## Быстрый вывод

- **Лучшее локально (Non-Think):** StyleTune-26B (3.78, ~66 t/s), **Boulesis-26B (3.74, ~55 t/s)**,
  Glistening-Gem (3.61), Schattenblume / heretic-ARA (3.59), Giftige-Blume-v1 (3.58), Goetia (3.55, ~70 t/s), DTV2 (3.51).
- **Базовые Gemma** (`base Gemma-26B/31B`) заходят высоко (3.76 / 3.70 и 3.81 в think) — пригодный
  «дефолт без тюна»; в помеченных строках есть самооценка Gemma-судьи (балл завышен).
- **Лучшее локально (Think):** Dark-Thoughts V2 (4.01), Schattenblume / StyleTune (3.83), Boulesis-26B (3.60).
- **Облако (Cloud):** DeepSeek-Pro 4.01 · DeepSeek-Flash 3.98 · GLM-5.2 3.90 · GLM-4.7 3.87 — выше локальных,
  но это API (платно/сеть/reasoning), **не замена конфигам**; дешёвые — GLM-4.7-Flash (free),
  DeepSeek-Flash (0.15/0.60 USD), GLM-4.7-FlashX (0.07/0.40 USD).
- **Не берём** (в витрину не попали): Local — Giftige-Blume-StyleSwap (англ. вставки в русский),
  Artemis-31B-v1.2 (речевая каша), Swift-1.5-27B (не RP-тюн), Genesis V7 35B-A3B (не апгрейд),
  Kitchoon-26B-A4B (не апгрейд — слабейший из 26B-мёржей, панель 3.25; провал памяти, think сломан),
  Dans-PersonalityEngine (чат-компаньон, не character-RP), base Qwen3.6/3.8 (слабые baseline);
  Cloud — GLM-4.7-FlashX (слабее и платный). Детали и вердикты — `docs\models.md`.

> Оговорки: DeepSeek-строки судят и DeepSeek-судьи, а `base Gemma-26B` — сама Gemma-судья (self-eval —
> балл завышен); у `Boulesis-26B` та же база у gemma-судьи (родственная, не идентичная); `сц=6` строже
> (на 2 сценах было бы выше); цены DeepSeek — off-peak (в пик ×2); t/s — RP на нашем стенде (16 ГБ);
> итоговый выбор «под себя» — за пользователем.
