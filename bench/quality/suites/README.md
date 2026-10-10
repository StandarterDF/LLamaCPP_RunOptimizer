# suites — сгенерированные наборы прогонов

`suite_rp_eval_<модель>_<режим>.json` — готовые входные файлы для [rp_quality.py](../rp_quality.py):
модель, `base_args` (как в её `.bat`), сценарии, сиды, сэмплинг. Генерируются скриптом харнесса
из [prompts](../prompts/README.md); вручную не правятся.

- `*_nothink` / `*_think` — режим модели;
- `*_en` — английский скрин, `*_full` — полный набор (6 сценариев);
- примеры: `suite_rp_eval_dtv2_nothink.json`, `suite_rp_eval_blume_full_think.json`.

Результаты прогонов — в [runs](../runs/README.md).
