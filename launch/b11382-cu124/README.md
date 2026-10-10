# b11382-cu124 — основная сборка

Конфиги под **llama.cpp b11382, Windows x64, CUDA 12.4** (сервер — `downloads\llama-b11382-cu124\llama-server.exe`).
Сборка в репозиторий не входит и восстанавливается по [AGENTS.md](../../AGENTS.md).

## Семейства моделей

| Папка | Модели | Конфигов |
| --- | --- | --: |
| [dans-24b](dans-24b) | Dans-PersonalityEngine-V1.3.0-24b (bartowski, IQ4_XS) | 1 |
| [gemma4-26a4b](gemma4-26a4b) | Gemma-4-26B-A4B (MoE): base, StyleTune-V2, Boulesis v2.1, Goetia v1.6, Kitchoon, MeroMero, WaifuGemma | 15 |
| [gemma4-31b](gemma4-31b) | Gemma-4-31B (dense): base, Artemis, Blume-v1, Dark-Thoughts V2, Glistening-Gem, heretic-ARA, Schattenblume, Split-Untied, StyleSwap | 19 |
| [qwen36-27b](qwen36-27b) | Qwen3.6-27B Fable-Fusion-711 (IQ2_M и i1-IQ3_S) | 6 |
| [qwen36-35b-a3b](qwen36-35b-a3b) | Qwen3.6-35B-A3B (MoE): base, Genesis-Hermes-V7, MTP/DFlash | 5 |
| [qwen38-27b](qwen38-27b) | Qwen3.8-27B (dense) | 4 |
| [swift](swift) | Swift-1.5-Qwen3.8-27B (dense) | 4 |

## Правила именования

`<модель>-<режим>[-вариант]-b11382.bat`:

- `-nothink-` / `-think-` — режим мышления (think у части моделей непригоден — см. шапку конфига);
- `-ru` — RU-пресет сэмплинга, `-nospec` — без спекуляции, `-mtp` — со спекуляцией;
- в шапке каждого файла — квант, контекст, спекуляция, сэмплинг и итог по русскому.

Новая модель = новый `.bat` + секция в [launch\router\models-preset.ini](../router/models-preset.ini)
(правило из [AGENTS.md](../../AGENTS.md)).

## См. также

- [launch\README.md](../README.md) — как запускать, `config.local.bat`.
- [docs\models.md](../../docs/models.md) — реестр моделей, баллы и замеры.
