# EuroEval — что есть и чего нет (проверено 2026-10-05)

Источник: **euroeval.com**, открыт через Playwright с прокси. Версия сайта **v18.2.0**.
Это бенчмарк **NLU/NLG** (understanding / generative / chat по 30+ европейским языкам), **не** RP/creative.

## Главное: русского языка в EuroEval НЕТ

В списке языков — Albanian, Belarusian, Bosnian, Bulgarian, Catalan, Croatian, Czech, Danish, Dutch,
English, Estonian, Faroese, Finnish, French, German, Greek, Hungarian, Icelandic, Italian, Luxembourgish,
Latvian, Lithuanian, Norwegian, Polish, Portuguese, Romanian, Serbian, Slovak, Slovene, Spanish, Swedish,
**Ukrainian**. **Русского нет** (в славянской группе есть украинский и белорусский, но не русский).

Вывод: как «русский лидерборд» EuroEval **не подходит** (прежнее утверждение об обратном — ошибочно).

## Ближайший прокси — восточнославянские языки (generative)

Скачано кнопкой **Download CSV** через Playwright+прокси (файлы в `downloads\`). Позиции моделей Gemma 4:

| Лидерборд (generative) | Моделей | gemma-4-31B-it | gemma-4-26B-A4B-it | gemma-4-12B-it |
| --- | ---: | ---: | ---: | ---: |
| Ukrainian | 259 | **#5** (1.58) | #8 (1.78) | #8 (1.78) |
| Belarusian | 279 | **#6** (1.54) | #11 (1.87) | #13 (2.04) |
| Slavic (мультиязычный) | 378 | **#5** (1.62) | #7 (1.84) | #7 (1.88) |

(в скобках — rank score, меньше = лучше). Инструкт-версии (`-it`) стабильно выше базовых;
31B-it — лучшая Gemma по восточнославянским языкам.

**Файлы:** `downloads\euroeval-ukrainian-generative.csv`, `downloads\euroeval-belarusian.csv`,
`downloads\euroeval-slavic.csv`.

**Вывод:** базы Gemma 4 — в **топ-5–8** по украинскому/белорусскому/славянскому. Это косвенно
подтверждает, что **база Gemma 4 способна к русскому**, а проблемы RP-мержей (Split-Untied — 75 %
чистых) — следствие тюна, а не базы. Но самого русского в EuroEval нет, и RP он не измеряет.

## Чего EuroEval не даёт для нашей задачи

- Нет русского → прямого RU-сигнала нет.
- Не RP/creative → качество ролеплея не измеряется.
- Модели считаются базами/инструкт-версиями, а не RP-файнтюнами (Dark Thoughts V2, StyleTune и т.п. там нет).

## Источники

- <https://euroeval.com/leaderboards/> · <https://euroeval.com/leaderboards/ukrainian> ·
  <https://euroeval.com/methodology.html>
