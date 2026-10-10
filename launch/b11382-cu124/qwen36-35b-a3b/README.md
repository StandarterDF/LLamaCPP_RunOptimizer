# qwen36-35b-a3b — Qwen3.6-35B-A3B (MoE)

MoE 35B-A3B (~3B активных), квант unsloth **UD-Q2_K_XL** (11.71 GB). Быстрый и сильный в чате/коде/математике;
как RP-модель — база (сухо, пассивно). Think у Qwen3.6 в llama.cpp ломается (незакрытый канал) — не делаем.

| Конфиг | Модель (квант) | Чем отличается |
| --- | --- | --- |
| [mtp](qwen36-35b-a3b-mtp-b11382.bat) | Qwen3.6-35B-A3B | Основной чат/код: MTP nm5 pmin0.5, c=131072, vision на CPU. |
| [dflash-code](qwen36-35b-a3b-dflash-code.bat) | Qwen3.6-35B-A3B | Редактор кода: DFlash + ngram-mod, c=131072. |
| [base-rp-nothink](qwen36-35b-a3b-base-rp-nothink-b11382.bat) | Qwen3.6-35B-A3B | RP-baseline: русский 100 %, но сухо и пассивно — для RP не годится. |
| [base-rp-think](qwen36-35b-a3b-base-rp-think-b11382.bat) | Qwen3.6-35B-A3B | Think ломается (пустые ответы) — режим не использовать. |
| [genesis-hermes-v7-nothink](qwen36-35b-a3b-genesis-hermes-v7-nothink-b11382.bat) | Genesis Hermes V7 (mradermacher, i1-IQ4_XS) | Не влезает в 16 ГБ (`--fit on` отгружает ~3.7 ГиБ), судьи на уровне базы — не апгрейд. |

## См. также

- [docs\models\qwen36-35b-a3b.md](../../../docs/models/qwen36-35b-a3b.md) — скорости, DFlash/ngram, RP-скрин.
- [docs\quality\rp-quality-eval.md](../../../docs/quality/rp-quality-eval.md) §5.12 — Genesis Hermes V7.
