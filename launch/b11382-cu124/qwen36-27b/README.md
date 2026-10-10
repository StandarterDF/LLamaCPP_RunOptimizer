# qwen36-27b — Qwen3.6-27B Fable-Fusion-711

Dense 27B (uncensored heretic, линейка DavidAU). Два кванта: **IQ2_M** (DavidAU, NEO-MAX MTP, 11.3 GB)
и **i1-IQ3_S** (mradermacher, imatrix, 11.7 ГиБ). На RP спекуляция **вредит** (13.5 против 17.8 t/s) —
MTP оставлен только в конфиге для кода/чата.

| Конфиг | Модель (квант) | Чем отличается |
| --- | --- | --- |
| [fable-fus-711-nothink](qwen36-27b-fable-fus-711-nothink-b11382.bat) | IQ2_M | RP: рабочий режим, без спекуляции; русский 100 %, память 3.9. |
| [fable-fus-711-nothink-author](qwen36-27b-fable-fus-711-nothink-author-b11382.bat) | IQ2_M | Альтернативный сэмплинг автора карточки: резче голос, короче; панель 3.30 против 3.46. |
| [fable-fus-711-think](qwen36-27b-fable-fus-711-think-b11382.bat) | IQ2_M | С мышлением; в seduction дублирует ответ — рабочий режим nothink. |
| [fable-fus-711-mtp](qwen36-27b-fable-fus-711-mtp-b11382.bat) | IQ2_M | Код/чат/математика: MTP (+6–13 %), на RP не использовать. |
| [fable-i1-iq3s-nothink](qwen36-27b-fable-i1-iq3s-nothink-b11382.bat) | i1-IQ3_S | RP без мышления; контекст при KV q4_0 — до ~125k. |
| [fable-i1-iq3s-think](qwen36-27b-fable-i1-iq3s-think-b11382.bat) | i1-IQ3_S | Think рабочий (панель 3.79 — лучший не-Gemma); рабочий режим всё равно NoThink. |

## См. также

- [docs\models.md](../../../docs/models.md) — реестр моделей и баллы.
- [docs\quality\rp-quality-eval.md](../../../docs/quality/rp-quality-eval.md) §5.18 — разбор Fable.
- [docs\research\speculation-research.md](../../../docs/research/speculation-research.md) — почему MTP на RP вредит.
