---
description: Short English RP-models digest — what to run now
---

Produce a short **English** digest of the RP/creative models we actually ran locally. It is a ready-to-paste
post for r/SillyTavernAI.

User wish (may be empty): $ARGUMENTS

## Sources (only our own measurements, do not invent)
- `README.md`, `docs/models.md`, `docs/researched.md`, `docs/quality/rp-quality-eval.md`, `docs/quality/sampling-quality.md` §5.2–5.5;
- `bench/runs/results.jsonl` (TG/PP/acceptance) and `summary.md` of the newest folder in `bench/quality/runs/`.

## Output format
Start with the current date line: `As of <DD.MM.YYYY>`.

Hardware line: GPU + CPU of the bench (RTX 4060 Ti 16 GB + Ryzen 7 5700X, 32 GB RAM).

Then one line per model:
`- **<Model> (<quant>):** ran it — worked well, no Russian-language issues (96–100% clean), ~<TG> t/s. Used MTP: <yes/no> (acceptance ~X%). PP ~<PP> t/s. Config: <file>.bat`
If a model leaks on Russian, replace «no Russian-language issues» with a short honest note
(e.g. «stock preset leaks English — 75%; the Russian preset gives 96%»).

Then a closing invitation line, e.g.:
`If you know alternative models with strong Russian support, I'd be glad to hear your suggestions.`

End with a blank line and the link:
`Full configs, logs and benchmarks: https://github.com/StandarterDF/LLamaCPP_RunOptimizer`

## Rules
- **English** only.
- **RP/creative models only** — no chat/code/math models.
- Always state **GPU + CPU**.
- **No llama.cpp build/version** anywhere.
- **Do not** include models we never ran and **do not** write «not tested» notes.
- Numbers from measurements, with units. No local paths. 3–6 model lines.
