# qwen38-27b — Qwen3.8-27B (dense)

Dense 27B (Qwen3.5-архитектура: 64 слоя, гибрид linear/full attention 1:3, встроенная MTP-голова),
квант unsloth **UD-IQ2_XXS** (8.39 GB), c=81920. Аналог семейства Swift (см. [swift](../swift/README.md)).

| Конфиг | Режим | Чем отличается |
| --- | --- | --- |
| [best](qwen38-27b-best-b11382.bat) | Think | Основной: MTP nm5 pmin0.5, сэмплинг как у Swift, `--reasoning-preserve`. |
| [best-nothink](qwen38-27b-best-nothink-b11382.bat) | NoThink | То же без мышления (`--reasoning off`). |
| [base-rp-nothink](qwen38-27b-base-rp-nothink-b11382.bat) | NoThink | RP-baseline: русский 100 %, но коротко и поверхностно (путает факты). |
| [base-rp-think](qwen38-27b-base-rp-think-b11382.bat) | Think | НЕ использовать: reasoning вываливается в видимый ответ без тегов («Чисто» 33 %). |

Vision-проектор (`mmproj-F16.gguf` рядом с моделью) в конфигах не включён — при нужде добавьте
`--mmproj ... --no-mmproj-offload`.

## См. также

- [docs\models.md](../../../docs/models.md) — реестр моделей.
- [docs\quality\base-models-rp-eval.md](../../../docs/quality/base-models-rp-eval.md) — базовые instruct-модели на RP.
