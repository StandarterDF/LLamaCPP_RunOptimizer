# swift — Swift-1.5-Qwen3.8-27B

Dense 27B (ukung/ukisai: GSQ-RCO дообучение Qwen3.8), квант **IQ2_S-mtp** (со встроенной MTP-головой),
c=81920, KV q4_0. Силён в reasoning/агентных задачах; русский чистый.

| Конфиг | Режим | Чем отличается |
| --- | --- | --- |
| [best](swift-best-b11382.bat) | Think | Основной рабочий: MTP nm5 pmin0.5, `--reasoning-preserve`. |
| [best-nothink](swift-best-nothink-b11382.bat) | NoThink | Копия `best` без мышления (`--reasoning off`). |
| [agent-ngram](swift-agent-ngram-b11382.bat) | Think | Агентный/код: MTP + ngram-simple, c=81920. |
| [long-131k](swift-long-131k-b11382.bat) | Think | Длинный контекст 131072, MTP nm3 pmin0.7. |

## См. также

- [docs\models\swift-1.5-27b.md](../../../docs/models/swift-1.5-27b.md) — все серии замеров.
- [docs\models\swift-1.5-27b-launch.md](../../../docs/models/swift-1.5-27b-launch.md) — практическая инструкция и итоговый конфиг.
