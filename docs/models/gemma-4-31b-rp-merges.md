# Gemma-4-31B RP-мержи: Split-Untied-31B и G4-MeroMero-v2-31B-heretic — лог тюнинга

**Модели (обе — gemma4 dense ≈31–32B, IQ3_XXS):**
- `Split-Untied-31B.i1-IQ3_XXS.gguf` (12.8 ГБ) — `mradermacher/Split-Untied-31B-i1-GGUF`,
  база `Blazed-Forge/Split-Untied-31B` (StyleSwap-мерж; среди родителей — Dark-Thoughts V2, untied
  `lm_head`; карточка помечает модель как vision, mmproj не скачан).
- `G4-MeroMero-v2-31B-heretic.i1-IQ3_XXS.gguf` (12.2 ГБ) — `mradermacher/G4-MeroMero-v2-31B-heretic-i1-GGUF`,
  база `DogOnKeyboard/G4-MeroMero-v2-31B-heretic` (abliteration `zerofata/G4-MeroMero-v2-31B`).
  **Модель снята с диска 🗑, конфиги удалены** (лог сохранён как история).

**Драфт (общий для обеих):** `gemma-4-31B-it-assistant.Q4_K_M.gguf` (0.33 ГБ) + `--spec-type draft-mtp`
(папка `mradermacher\Gemma-4-Queen-31B-it-uncensored-heretic-i1-GGUF`).
**Стенд:** RTX 4060 Ti 16 ГБ, Ryzen 7 5700X, 32 ГБ, Windows; сборка b11382 (CUDA 12.4).
**Методика:** `bench\requests_real.json` (RP/чат/код/матем/суммаризация), `cache_prompt: false`, seed 42;
сырые данные — `bench\runs\results.jsonl` (тесты `real_split_*`, `real_meromero_*`), наборы —
`bench\suites\real\real_split_untied.json`, `bench\suites\real\real_meromero.json`.

**Готовые конфиги (b11382):**
- Split-Untied: `..\..\launch\b11382-cu124\gemma4-31b-split-untied-nothink-b11382.bat` (NoThink),
  `..\..\launch\b11382-cu124\gemma4-31b-split-untied-think-b11382.bat` (с мышлением),
  `..\..\launch\b11382-cu124\gemma4-31b-split-untied-nothink-ru-b11382.bat` (RU-пресет temp0.4).
- MeroMero v2 heretic: конфиги и файл модели **удалены** (модель снята с диска 🗑) — см. `docs\models.md`.

## Сэмплинг по карточкам

| Модель | Temp | Min-P | Top-K / Top-P | Прочее | Мышление |
| --- | ---: | ---: | --- | --- | --- |
| Split-Untied-31B | 1.0 | 0.03 | off / 1.0 | rep. penalty off, DRY multiplier 0.8 | опционально (`<\|think\|>`); может ломаться у мержей |
| G4-MeroMero-v2-31B | 0.8–1.0 | 0.05 | дефолт | — | on и off; thinking — лучше recall, хуже темп ERP |

Правило проекта: сэмплинг — по карточке модели (температура на скорость не влияет, см.
`docs\researched.md` §5). В `.bat` зафиксированы эти значения.

## Замеры: MTP vs без спекуляции (b11382, c=51200, KV q4_0, `-fa on`)

Базовый конфиг унаследован от Gemma-4-31B Dark-Thoughts (`docs\models\gemma-4-31b.md`): тот же драфт,
`nmax5 pmin0.75`, `c=51200` (выше 80k — ловушка), KV `q4_0`, `-ctxcp 16 -cms 512` для многотирна.

| Задача | Split-Untied MTP | Split-Untied без спец. | MeroMero v2 h. MTP | MeroMero v2 h. без спец. |
| --- | ---: | ---: | ---: | ---: |
| RP | **22.6** (68.2 %) | 16.8 | **21.1** (57.5 %) | 16.8 |
| Чат | **34.1** (69.5 %) | 16.9 | **25.8** (60.2 %) | 17.0 |
| Код | **46.5** (77.0 %) | 17.0 | **44.6** (73.2 %) | 17.0 |
| Математика | **45.7** (78.8 %) | 17.0 | **47.2** (77.4 %) | 16.9 |
| Суммаризация | **37.9** (68.1 %) | 16.8 | **37.5** (73.0 %) | 16.8 |

VRAM после загрузки: **15 104 MiB** с MTP (обе), 14 240 MiB без спекуляции. Загрузка 5–16 с.

**Выводы:**
- Общий MTP-assistant от Gemma-4-31B **работает и на этих мержах**, включая Split-Untied с *untied*
  `lm_head` — принятие 57–79 %, MTP даёт ×1.25 (RP MeroMero) … ×2.8 (код/математика).
- Числа Split-Untied практически совпадают с Dark-Thoughts V2 (23 / 30.5 / 47.6 / 46.6 / 37.7) — что
  ожидаемо: Dark-Thoughts — один из родителей мержа.
- MeroMero v2 heretic чуть слабее на RP/чате (принятие спекуляции ниже: 57–60 % против 68–70 %), но
  на коде/математике не хуже. Для RP-креатива это нормально: текст высокоэнтропийный, спекуляция
  угадывает хуже — но всё равно окупается (21 против 17 t/s).
- VRAM 15.1 ГБ при 16 ГБ — с запасом ~1.2 ГБ; контекст выше 51200 поднимать не стоит (проверено на
  Dark-Thoughts: 80k = −45 %).

## Не проверено

- Влияние `--reasoning on` (think-профиль) на скорость и качество — `.bat` собран, но не измерялся.
- DRY multiplier 0.8 в связке с MTP (на карточке Split-Untied) — на скорость не влияет, на качество
  не оценивалось.
- Контекст 51k–131k, KV `q8_0`, `-np 2`, vision (mmproj в static-репозитории mradermacher не скачан).
