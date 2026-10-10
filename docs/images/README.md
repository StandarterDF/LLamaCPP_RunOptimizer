# docs\images — графики замеров

Только реальные замеры (генераторы: [bench\plot_kv.py](../../bench/plot_kv.py),
[bench\make_charts.py](../../bench/make_charts.py)). Вставлять в `.md` — ссылкой
`images\<файл>.png` (из docs) или `docs/images\<файл>.png` (из корня).

| Файл | Что показывает | Где используется |
| --- | --- | --- |
| `chart_rp_ranking.png` | RP-балл моделей (Non-Think/Think, Local/Cloud) | [rp-ranking.md](../quality/rp-ranking.md), [README.md](../../README.md) |
| `chart_speculation_models.png` | Без спекуляции vs MTP по моделям | [speculation-research.md](../research/speculation-research.md) |
| `chart_speculation_tasks.png` | Qwen3.6: где спекуляция окупается (RP/чат/код/мат./сумма) | [speculation-research.md](../research/speculation-research.md) |
| `chart_cache_prompt.png` | Кэш префикса: пересчёт токенов и время на ход | [context-infinite-chat.md](../research/context-infinite-chat.md) |
| `kv_concept.png` | Как считается память KV-кэша (схема) | [kv-cache-quantization.md](../research/kv-cache-quantization.md) |
| `kv_memory_vs_context.png` | Память KV vs длина контекста (вычислено из GGUF) | [kv-cache-quantization.md](../research/kv-cache-quantization.md), [context-memory-model.md](../research/context-memory-model.md) |
| `kv_max_context.png` | Максимальный контекст по моделям (16 ГБ) | [context-memory-model.md](../research/context-memory-model.md) |
| `kv_vram_budget.png` | Бюджет VRAM по длинам контекста | [kv-cache-quantization.md](../research/kv-cache-quantization.md) |
| `kv_vram_measured.png` | Измеренная VRAM (f16/q8_0/q4_0) | [kv-cache-quantization.md](../research/kv-cache-quantization.md) |
| `kv_niah_schattenblume-31b.png`, `kv_niah_styletune-26b.png` | NIAH (needle-in-a-haystack) на двух моделях | [kv-cache-quantization.md](../research/kv-cache-quantization.md) |
| `kv_recall_vs_context.png` | Recall vs длина контекста | [kv-cache-quantization.md](../research/kv-cache-quantization.md) |
| `kv_canary_schattenblume-31b.png`, `kv_canary_styletune-26b.png` | Канарейка: tool/JSON-вызовы и код | [kv-cache-external.md](../research/kv-cache-external.md) |
| `kv_ppl.png` | PPL по типам KV | [kv-cache-quantization.md](../research/kv-cache-quantization.md) |
| `kv_tg_vs_context.png` | Скорость генерации vs длина контекста | [kv-cache-quantization.md](../research/kv-cache-quantization.md) |
| `kv_prompt_flags_schattenblume-31b.png`, `kv_prompt_flags_styletune-26b.png` | Промптовое сравнение: что портится под квантованным KV | [kv-cache-quantization.md](../research/kv-cache-quantization.md) |
