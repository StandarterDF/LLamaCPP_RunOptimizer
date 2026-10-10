# bench\skill-selftest — самопроверка скила

Небольшой прогон, проверяющий, что скил llm-launch-tuner (и его скрипты) работают: запускает
llama-server на Swift-1.5 (MTP) с плейсхолдер-путями и коротким запросом, затем собирает отчёт.

| Файл | О чём |
| --- | --- |
| [suite.json](suite.json) | Мини-набор: одна модель (Swift-1.5 IQ2_S-mtp), один тест `selftest_01`, короткий запрос. |
| [runs/](runs) | Результаты: `results.jsonl`, `summary.md` (нагрузка, VRAM, TG), лог `selftest_01.log`. |

Требует локальный llama-server и модель (пути в наборе — плейсхолдеры `${LLAMA_SERVER}`,
`${MODELS_DIR}`, подставляются как в сценариях bench).
