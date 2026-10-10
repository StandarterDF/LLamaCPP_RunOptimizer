# gemma4-31b — Gemma-4-31B (dense)

Конфиги под сборку [b11382](../README.md); dense 31B, кванты **i1-IQ3_XXS** (кроме Artemis-nothink —
bartowski IQ3_XXS). По умолчанию: c=51200, KV q4_0, спекуляция — MTP-ассистент (nmax5 pmin0.75).
Think у части мёржей ломается (незакрытый `<channel|>`) — рабочий режим смотрите в шапке конфига.

| Конфиг | Модель (квант) | Чем отличается |
| --- | --- | --- |
| [artemis-nothink](gemma4-31b-artemis-nothink-b11382.bat) | Artemis-31B-v1.2 (bartowski, IQ3_XXS) | Русский 92–96 %, ~20–22 t/s; c=32k — садится впритык к 16 ГБ. |
| [artemis-think](gemma4-31b-artemis-think-b11382.bat) | Artemis-31B-v1.2 (mradermacher, i1-IQ3_XXS) | С мышлением; бюджет задаётся `--reasoning-budget`. |
| [base-nothink](gemma4-31b-base-nothink-b11382.bat) | Gemma-4-31B-it (unsloth, UD-IQ3_XXS) | Instruct-база, не RP-тюн; русский 100 %. |
| [base-think](gemma4-31b-base-think-b11382.bat) | Gemma-4-31B-it | Think рабочий (редкость для 31B); голос персонажа — слабое место. |
| [blume-v1-nothink](gemma4-31b-blume-v1-nothink-b11382.bat) | Giftige-Blume-v1 (Blazed-Forge, i1-IQ3_XXS) | CaliperBench №1; лучшая инициатива на полном наборе. |
| [blume-v1-think](gemma4-31b-blume-v1-think-b11382.bat) | Giftige-Blume-v1 | Think без лимита бюджета; пустых меньше, качество ≈ NoThink. |
| [dark-thoughts-nothink](gemma4-31b-dark-thoughts-nothink-b11382.bat) | Dark-Thoughts V2 (mradermacher, i1-IQ3_XXS) | RP, без мышления; MTP nmax5 pmin0.75. |
| [dark-thoughts-think](gemma4-31b-dark-thoughts-think-b11382.bat) | Dark-Thoughts V2 | Лучший наш Local Think (панель 4.01). |
| [glistening-nothink](gemma4-31b-glistening-nothink-b11382.bat) | Glistening-Gem v2.1 (sophosympatheia, i1-IQ3_XXS) | Лучшая по памяти; русский чистый, TG ~23 t/s. |
| [glistening-think](gemma4-31b-glistening-think-b11382.bat) | Glistening-Gem v2.1 | Think давал пустые ответы (7/18) — неполноценно; рабочий — nothink. |
| [heretic-ara-nothink](gemma4-31b-heretic-ara-nothink-b11382.bat) | Gemma-4-31B-it-heretic-ARA (i1-IQ3_XXS) | Abliterated база, не RP-тюн; русский 83 % в NoThink. |
| [heretic-ara-think](gemma4-31b-heretic-ara-think-b11382.bat) | heretic-ARA | Think рабочий: русский 100 %. |
| [schattenblume-nothink](gemma4-31b-schattenblume-nothink-b11382.bat) | Schattenblume (Nimbz, i1-IQ3_XXS) | Наш балл 4.55; русский 100 %. |
| [schattenblume-think](gemma4-31b-schattenblume-think-b11382.bat) | Schattenblume | Think иногда не закрывает канал (пустой ответ) — поднимайте бюджет/n_predict. |
| [split-untied-nothink](gemma4-31b-split-untied-nothink-b11382.bat) | Split-Untied-31B (i1-IQ3_XXS) | Сэмплинг по карточке (temp 1.0 / min-p 0.03 / DRY 0.8). |
| [split-untied-nothink-ru](gemma4-31b-split-untied-nothink-ru-b11382.bat) | Split-Untied-31B | RU-пресет: temp 0.4, top-k off — лечит англ. вставки/склейки (96 % чистых). |
| [split-untied-think](gemma4-31b-split-untied-think-b11382.bat) | Split-Untied-31B | С мышлением (по карточке — лучший recall); если ломается — берите nothink. |
| [styleswap-nothink](gemma4-31b-styleswap-nothink-b11382.bat) | Giftige-Blume-v1-StyleSwap (Casual-Autopsy, i1-IQ3_XXS) | Худший из проверенных, англ. вставки; для RU не берём. |
| [styleswap-think](gemma4-31b-styleswap-think-b11382.bat) | StyleSwap | То же с мышлением; think может не закрывать канал. |

## См. также

- [docs\models\gemma-4-31b.md](../../../docs/models/gemma-4-31b.md) — серии замеров и конфиги.
- [docs\models\gemma-4-31b-rp-merges.md](../../../docs/models/gemma-4-31b-rp-merges.md) — RP-мержи.
- [docs\quality\rp-quality-eval.md](../../../docs/quality/rp-quality-eval.md) — баллы по моделям.
- [docs\quality\base-models-rp-eval.md](../../../docs/quality/base-models-rp-eval.md) — базовые instruct-модели.
- [docs\quality\sampling-quality.md](../../../docs/quality/sampling-quality.md) — сэмплинг и русский (Split-Untied, Artemis).
