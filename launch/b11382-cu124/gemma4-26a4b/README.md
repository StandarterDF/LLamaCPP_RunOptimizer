# gemma4-26a4b — Gemma-4-26B-A4B (MoE)

Конфиги под сборку [b11382](../README.md); модель — MoE 26B-A4B (~4B активных). У RP-моделей
MTP-головы нет (спекуляция не включается); со спекуляцией — только StyleTune (внешний MTP-ассистент)
и `dflash-code` (DFlash-спекулятор).

| Конфиг | Модель (квант) | Чем отличается |
| --- | --- | --- |
| [base-rp-nothink](gemma4-26a4b-base-rp-nothink-b11382.bat) | база Gemma-4-26B-A4B-it (unsloth, UD-IQ3_XXS) | RP-baseline, без мышления; без спекуляции. |
| [base-rp-think](gemma4-26a4b-base-rp-think-b11382.bat) | та же база | С мышлением: reasoning утекает в канал — невалидно; рабочий режим — nothink. |
| [styletune-nothink-nospec](gemma4-26a4b-styletune-nothink-nospec-b11382.bat) | StyleTune-V2 (mradermacher, IQ4_XS) | RP: лучший наш Local NoThink; без спекуляции (на RP она вредит: 63 против 50 t/s). |
| [styletune-nothink](gemma4-26a4b-styletune-nothink-b11382.bat) | StyleTune-V2 | Без мышления, со спекуляцией (MTP-ассистент Q4_K_S). |
| [styletune](gemma4-26a4b-styletune-b11382.bat) | StyleTune-V2 | Чат/код: MTP nm5 pmin0.5, c=65536. |
| [dflash-code](gemma4-26a4b-dflash-code.bat) | StyleTune-V2 | Редактор кода: DFlash + ngram-mod, c=32768. |
| [boulesis-v21-nothink](gemma4-26a4b-boulesis-v21-nothink-b11382.bat) | Boulesis v2.1 (SubMaroon; mradermacher i1-IQ4_XS) | Лучший из измеренных 26B-мёржей; NoThink ~55 t/s. |
| [boulesis-v21-think](gemma4-26a4b-boulesis-v21-think-b11382.bat) | Boulesis v2.1 | Think работает, но хуже NoThink (4.27 против 4.48 у gemma-судьи). |
| [goetia-nothink](gemma4-26a4b-goetia-nothink-b11382.bat) | Goetia v1.6 (Naphula, i1-IQ3_XXS) | RP ~73 t/s; без спекуляции. |
| [goetia-think](gemma4-26a4b-goetia-think-b11382.bat) | Goetia v1.6 | Think в llama.cpp непригоден (незакрытый `<channel|>`); конфиг для клиентов с разбором reasoning. |
| [kitchoon-nothink](gemma4-26a4b-kitchoon-nothink-b11382.bat) | Kitchoon (SubMaroon; i1-IQ4_XS) | Не апгрейд: провал памяти, шаблоны; для RP не берём. |
| [kitchoon-think](gemma4-26a4b-kitchoon-think-b11382.bat) | Kitchoon | Think непригоден: англ. reasoning утекает в видимый текст. |
| [meromero-nothink](gemma4-26a4b-meromero-nothink-b11382.bat) | G4-MeroMero (llmfan46, i1-IQ4_XS) | Не апгрейд; русский 100 %, повторяет действия. |
| [meromero-think](gemma4-26a4b-meromero-think-b11382.bat) | G4-MeroMero | Think непригоден (обрывы, утечка черновиков). |
| [waifugemma-nothink](gemma4-26a4b-waifugemma-nothink-b11382.bat) | WaifuGemma4-26b-a4b-v1 (hiwaifu-research, i1-IQ3_XXS) | RU-обученная RP (ru/uk); сэмплинг карточки (temp 1.0 / min-p 0.03) — лучший по русскому, T не понижать. |

## См. также

- [docs\models\gemma-4-26b-a4b.md](../../../docs/models/gemma-4-26b-a4b.md) — скорости, спекуляция, RP-скрин.
- [docs\quality\rp-quality-eval.md](../../../docs/quality/rp-quality-eval.md) — разборы по моделям.
- [docs\quality\sampling-quality.md](../../../docs/quality/sampling-quality.md) — сэмплинг и русский (WaifuGemma, StyleTune).
