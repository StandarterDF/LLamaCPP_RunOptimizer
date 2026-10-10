# GGUFLauncher — готовые конфиги запуска локальных LLM (llama.cpp)

Подобранные бенчмарками конфиги для llama.cpp: скорость на реалистичных промптах (RP/чат/код/
математика) и качество RP, проверенное LLM-судьями. Тестовый стенд: **RTX 4060 Ti 16 ГБ, Ryzen 7
5700X, 32 ГБ, Windows**, сборка llama.cpp — b11382 (CUDA 12.4).

Здесь — что запустить и что выбрать. Все исследования, методики и полные таблицы — в
[docs\README.md](docs/README.md); что уже проверено и не требует повторов — [docs\researched.md](docs/researched.md).

## Быстрый старт

1. Скопируйте [config.example.bat](config.example.bat) → `config.local.bat` и укажите свои пути:
   `LLAMA_SERVER` (llama-server.exe) и `MODELS_DIR` (папка с GGUF). Готовая сборка — в
   `downloads\llama-b11382-cu124\`.
2. Выберите `.bat` под свою задачу из таблицы ниже и запустите (все конфиги — в
   [launch\b11382-cu124](launch/b11382-cu124)).
3. Дождитесь строки `listening on http://...` — сервер готов (OpenAI-совместимый API).

**Не хочется выбирать `.bat` на каждую модель** — поднимите роутер: один сервер обслуживает все
модели, клиент выбирает её по имени в поле `model` — [launch\router\run-router.bat](launch/router/run-router.bat).
Для RP есть отдельный [run-rp-router.bat](launch/router/run-rp-router.bat) (порт 9932, только
проверенные RP-модели). Подробности — [docs\research\router-mode.md](docs/research/router-mode.md).

## Какую модель выбрать

### RP / креатив

Рабочий режим — **NoThink** (think у большинства 31B-мержей в llama.cpp ломается: пустые ответы).
Баллы — среднее **панели 4 судей** (шкала 1–5) из витрины [docs\quality\rp-ranking.md](docs/quality/rp-ranking.md);
**сравнивать баллы можно только внутри витрины**. Полные разборы и оговорки (self-eval облака,
родственные базы) — [docs\quality\rp-quality-eval.md](docs/quality/rp-quality-eval.md).
Имена моделей в таблицах — ссылки на их GGUF-квантование на Hugging Face.

| Что нужно | Модель | Балл (панель 4 судей) | Скорость RP | Конфиг |
| --- | --- | --- | --- | --- |
| Быстро и хорошо | **[StyleTune-V2 26B-A4B](https://huggingface.co/mradermacher/Gemma-4-26B-A4B-StyleTune-V2-GGUF)** | **3.78** — лучший Local NoThink | ~63 t/s (без спец.) | [styletune-nothink-nospec](launch/b11382-cu124/gemma4-26a4b/gemma4-26a4b-styletune-nothink-nospec-b11382.bat) |
| Баланс (MoE) | **[Boulesis v2.1 26B-A4B](https://huggingface.co/mradermacher/Boulesis-v2.1-26B-A4B-i1-GGUF)** | 3.74 | ~55 t/s | [boulesis-v21-nothink](launch/b11382-cu124/gemma4-26a4b/gemma4-26a4b-boulesis-v21-nothink-b11382.bat) |
| Максимум качества, 31B dense | **[Giftige-Blume-v1](https://huggingface.co/mradermacher/Gemma-4-Giftige-Blume-31B-v1-i1-GGUF) · [Schattenblume](https://huggingface.co/mradermacher/Schattenblume-31B-i1-GGUF) · [Glistening-Gem v2.1](https://huggingface.co/mradermacher/Glistening-Gem-31B-v2.1-i1-GGUF) · [Dark-Thoughts V2](https://huggingface.co/mradermacher/Gemma-4-Dark-Thoughts-V2-31B-i1-GGUF)** | 3.51–3.61; у Blume — лучшая инициатива (4.0) | 22–25 t/s | [blume-v1](launch/b11382-cu124/gemma4-31b/gemma4-31b-blume-v1-nothink-b11382.bat) · [schattenblume](launch/b11382-cu124/gemma4-31b/gemma4-31b-schattenblume-nothink-b11382.bat) · [glistening](launch/b11382-cu124/gemma4-31b/gemma4-31b-glistening-nothink-b11382.bat) · [dark-thoughts](launch/b11382-cu124/gemma4-31b/gemma4-31b-dark-thoughts-nothink-b11382.bat) (все `-nothink`) |
| Лучший Think | **[Dark-Thoughts V2 31B](https://huggingface.co/mradermacher/Gemma-4-Dark-Thoughts-V2-31B-i1-GGUF)** | **4.01** — лучший Local Think | ~27 t/s | [dark-thoughts-think](launch/b11382-cu124/gemma4-31b/gemma4-31b-dark-thoughts-think-b11382.bat) |
| Верхний референс (не локально) | DeepSeek-V4-Pro · V4.1-Flash · GLM-5.2 — облако, API | 4.01 · 3.98 · 3.90 | — | [docs\quality\cloud-api-rp-eval.md](docs/quality/cloud-api-rp-eval.md) |

![RP-рейтинг моделей](docs/images/chart_rp_ranking.png)

- **Русский язык**: чисто держат **Dark-Thoughts V2** и **StyleTune-V2** (96–100 % ответов без англ.
  вставок и BPE-склеек); слабый Split-Untied лечится RU-пресетом (`temp 0.4`). Сэмплинг подбирается
  под модель — [docs\quality\sampling-quality.md](docs/quality/sampling-quality.md).
- **Пригодный baseline без тюна** — базовая [Gemma-4-26B-A4B-it](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF) (панель 3.76, ~55 t/s):
  [gemma4-26a4b-base-rp-nothink](launch/b11382-cu124/gemma4-26a4b/gemma4-26a4b-base-rp-nothink-b11382.bat).
- **Хочется всё сразу:** RP-роутер (9932) — 4 лидера 31B + быстрые StyleTune/Goetia, выбор по имени.
- **Под RP не брать:** Artemis-31B (речевая каша), Giftige-Blume-StyleSwap (англ. вставки), Kitchoon v1,
  MeroMero (не апгрейд), Swift-1.5 и базовые Qwen — не RP-модели. Вердикты и кандидаты (без `.bat`
  это не рекомендация) — [docs\models.md](docs/models.md).
- Лидеры 31B идут плотной группой — итоговый вкусовой выбор за пользователем.

### Остальные задачи

- **Чат, код, математика, длинные документы — [Qwen3.6-35B-A3B](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-MTP-GGUF)** (MoE, Q2_K_XL): 93 / 111 / 121 t/s,
  контекст 131k, PP ~800–1700 t/s. Кодинг-профиль с DFlash+ngram: **+18 % рефакторинг**, **+44 %
  новый код** к MTP. Конфиги: [qwen36-35b-a3b-mtp](launch/b11382-cu124/qwen36-35b-a3b/qwen36-35b-a3b-mtp-b11382.bat),
  [qwen36-35b-a3b-dflash-code](launch/b11382-cu124/qwen36-35b-a3b/qwen36-35b-a3b-dflash-code.bat).
- **Русский чат/код на Gemma-4 — [StyleTune-V2 26B-A4B](https://huggingface.co/mradermacher/Gemma-4-26B-A4B-StyleTune-V2-GGUF)** (70/100/107 t/s): тот же `.bat`, что и для
  чата — [gemma4-26a4b-styletune](launch/b11382-cu124/gemma4-26a4b/gemma4-26a4b-styletune-b11382.bat).
- **Dense 27B (медленнее):** [Swift-1.5-27B](https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF) — 28–37 t/s, efficient reasoning/агенты
  ([swift-best](launch/b11382-cu124/swift/swift-best-b11382.bat)); [Qwen3.6-27B Fable-Fusion-711](https://huggingface.co/DavidAU/Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic-NM-DAU-NEO-MAX-MTP-GGUF) —
  ~18–20 t/s, русский чистый ([fus-711](launch/b11382-cu124/qwen36-27b/qwen36-27b-fable-fus-711-nothink-b11382.bat),
  [i1-iq3s](launch/b11382-cu124/qwen36-27b/qwen36-27b-fable-i1-iq3s-nothink-b11382.bat)).
- **Несколько пользователей:** `-np 2` делит контекст между слотами и требует больше VRAM — на 16 ГБ
  держите один слот и одну модель.

## Готовые конфиги (`.bat`)

Скорость TG (t/s) на реалистичных промптах ([bench\requests_real.json](bench/requests_real.json)):
RP / чат / код / математика. «—» — не измеряли.

| Модель (тип, квант) | RP | Чат | Код | Мат. | Конфиг |
| --- | ---: | ---: | ---: | ---: | --- |
| **[Qwen3.6-35B-A3B](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-MTP-GGUF)** (MoE ~3B акт., Q2_K_XL) | **82** | **93** | **111** | **121** | [qwen36-35b-a3b-mtp](launch/b11382-cu124/qwen36-35b-a3b/qwen36-35b-a3b-mtp-b11382.bat) (+ [dflash-code](launch/b11382-cu124/qwen36-35b-a3b/qwen36-35b-a3b-dflash-code.bat)) |
| **[Gemma-4-26B-A4B StyleTune-V2](https://huggingface.co/mradermacher/Gemma-4-26B-A4B-StyleTune-V2-GGUF)** (MoE, IQ4_XS) | 63¹ | 70 | 100 | 107 | RP — [styletune-nothink-nospec](launch/b11382-cu124/gemma4-26a4b/gemma4-26a4b-styletune-nothink-nospec-b11382.bat); чат/код — [styletune](launch/b11382-cu124/gemma4-26a4b/gemma4-26a4b-styletune-b11382.bat) |
| **[Gemma-4-26B-A4B Boulesis v2.1](https://huggingface.co/mradermacher/Boulesis-v2.1-26B-A4B-i1-GGUF)** (MoE, IQ4_XS) | 55² | — | — | — | [boulesis-v21-nothink](launch/b11382-cu124/gemma4-26a4b/gemma4-26a4b-boulesis-v21-nothink-b11382.bat) (+ `-think`) |
| **[Gemma-4-26B-A4B Goetia v1.6](https://huggingface.co/mradermacher/Goetia-26B-A4B-v1.6-i1-GGUF)** (MoE, IQ3_XXS) | ~73 | — | — | — | [goetia-nothink](launch/b11382-cu124/gemma4-26a4b/gemma4-26a4b-goetia-nothink-b11382.bat) (think непригоден) |
| **[Giftige-Blume-v1 31B](https://huggingface.co/mradermacher/Gemma-4-Giftige-Blume-31B-v1-i1-GGUF)** (dense RP-мерж, IQ3_XXS) | 22 | — | — | — | [blume-v1-nothink](launch/b11382-cu124/gemma4-31b/gemma4-31b-blume-v1-nothink-b11382.bat) (+ `-think`) |
| **[Schattenblume 31B](https://huggingface.co/mradermacher/Schattenblume-31B-i1-GGUF)** (dense RP-мерж, IQ3_XXS) | 22 | — | — | — | [schattenblume-nothink](launch/b11382-cu124/gemma4-31b/gemma4-31b-schattenblume-nothink-b11382.bat) (+ `-think`) |
| **[Glistening-Gem v2.1 31B](https://huggingface.co/mradermacher/Glistening-Gem-31B-v2.1-i1-GGUF)** (dense RP-мерж, IQ3_XXS) | 23 | — | — | — | [glistening-nothink](launch/b11382-cu124/gemma4-31b/gemma4-31b-glistening-nothink-b11382.bat) (+ `-think`) |
| **[Dark-Thoughts V2 31B](https://huggingface.co/mradermacher/Gemma-4-Dark-Thoughts-V2-31B-i1-GGUF)** (dense RP-мерж, IQ3_XXS) | 23 | 31 | 48 | 47 | [dark-thoughts-nothink](launch/b11382-cu124/gemma4-31b/gemma4-31b-dark-thoughts-nothink-b11382.bat) (+ `-think`) |
| **[Split-Untied 31B](https://huggingface.co/mradermacher/Split-Untied-31B-i1-GGUF)** (dense RP-мерж, IQ3_XXS) | 23 | 34 | 47 | 46 | [nothink](launch/b11382-cu124/gemma4-31b/gemma4-31b-split-untied-nothink-b11382.bat); RU — [nothink-ru](launch/b11382-cu124/gemma4-31b/gemma4-31b-split-untied-nothink-ru-b11382.bat); [think](launch/b11382-cu124/gemma4-31b/gemma4-31b-split-untied-think-b11382.bat) |
| **[Qwen3.6-27B Fable-Fusion-711](https://huggingface.co/DavidAU/Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic-NM-DAU-NEO-MAX-MTP-GGUF)** (dense, IQ2_M) | 18³ | 18 | 19 | 20 | [fus-711-nothink](launch/b11382-cu124/qwen36-27b/qwen36-27b-fable-fus-711-nothink-b11382.bat) (+ `-think`, `-author`, `-mtp`); RP-квант — [i1-iq3s-nothink](launch/b11382-cu124/qwen36-27b/qwen36-27b-fable-i1-iq3s-nothink-b11382.bat) (+ `-think`) |
| **[Swift-1.5-Qwen3.8-27B](https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF)** (dense, IQ2_S) | 28 | 37 | 36 | 37 | [swift-best](launch/b11382-cu124/swift/swift-best-b11382.bat) (+ `-nothink`, `-agent`, `-131k`) |

¹ StyleTune-V2: RP измерен **без спекуляции** — на креативном тексте MTP не окупается (63 t/s против
~50 с ним). Остальные числа — с MTP.
² Boulesis: измерен только RP (харнесс качества). Контекст `-c 51200`: при модели 14.3 ГБ больший
упирается в VRAM.
³ Fable (IQ2_M): RP — без спекуляции 17.8 t/s (с MTP 13.5 — вредит); код/математика — с MTP.
«—»: у 31B RP-мержей мерили в основном RP; полный список файлов — [launch\b11382-cu124](launch/b11382-cu124).

Код-профили `*-dflash-code` — только для Qwen3.6; на Gemma-26B DFlash проигрывает MTP (−17 %).
Конфиги старой сборки (10472) удалены — актуальна только b11382.

## Какая у вас видеокарта?

- **16 ГБ (как на стенде — проверено):** конфиги выше работают как есть; контекст 51k–131k в
  зависимости от модели.
- **12 ГБ (ориентир):** кванты на 9–12 ГБ (IQ2_S/Q2_K, IQ3_XXS), контекст 32–64k, KV `q4_0`;
  `--fit on` разложит слои сам, часть уедет на CPU — MTP-спекуляция частично компенсирует просадку.
- **8 ГБ (ориентир):** реально 7–9B в IQ2/Q2 или лёгкие MoE; контекст 16–32k, KV `q4_0`; выгрузка
  на CPU неизбежна.
- **24 ГБ+ (ориентир):** KV можно поднять до `q8_0`/f16, контекст 131k+ и vision на GPU; перепроверьте
  EAGLE-3/DSpark — на старших картах их оверхед может окупиться (на 16 ГБ они проиграли MTP).

*12/8/24 ГБ не измерялись — это ориентиры, выведенные из замеров на 16 ГБ.*

## Короткие правила, которые дают больше всего

1. **MTP-спекуляция** — главный рычаг на dense-моделях и на коде/математике; на RP у Gemma-26B и
   Qwen3.6-27B Fable она **вредит** — включайте осознанно (`--spec-draft-n-max 4…5`,
   `--spec-draft-p-min 0.5…0.75`).
2. **MoE-модель держите целиком в VRAM** — выгрузка экспертов на CPU даёт −32…−43 %.
3. **Контекст — с запасом 1.5–2 ГБ**: перегруз VRAM валит спекуляцию (до −45 %).
4. **KV-кэш `q4_0` — ради памяти, а не скорости** (`f16 ≥ q4_0 > q8_0`): на 31B поднимает контекст
   с ~26k до ~116k без потери качества до 49k. Для tool/JSON и кода — сначала проверьте
   ([docs\research\kv-cache-quantization.md](docs/research/kv-cache-quantization.md)). FlashAttention обязателен.
5. **Батчи и потоки не трогайте** — `-ub` сверх дефолта только ест VRAM, `-t/-tb` на TG не влияют.
6. **`cache_prompt: true` в клиенте** — в многотирне PP падает с тысяч токенов до ~100.
7. **Свежая сборка llama.cpp**: старые флаги вроде `--no-mmap` в b11382 удалены (замена —
   `--load-mode none`).

### Пример: ядро конфига и почему именно так

Ключевые флаги двух реальных конфигов (полные и рабочие — по ссылкам; здесь ядро без путей).

**RP на dense 31B** — [gemma4-31b-dark-thoughts-nothink-b11382.bat](launch/b11382-cu124/gemma4-31b/gemma4-31b-dark-thoughts-nothink-b11382.bat):

```text
-np 1 -c 51200                                  # один слот; контекст — по бюджету VRAM
-fa on --fit on --load-mode none                # FlashAttention; авто-раскладка; быстрая загрузка
-ctk q4_0 -ctv q4_0                             # KV q4_0: 31B ~26k → ~116k контекста
--spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.75
-md <драфт gemma-4-31B-it-assistant.Q4_K_M>     # внешний MTP-драфт
--jinja --reasoning off --reasoning-budget 0    # RP — NoThink
--temp 0.6 --min-p 0.1                          # RU-safe сэмплинг
```

**Чат/код на MoE** — [qwen36-35b-a3b-mtp-b11382.bat](launch/b11382-cu124/qwen36-35b-a3b/qwen36-35b-a3b-mtp-b11382.bat):

```text
-np 1 -c 131072                                 # MoE: KV и накладные дешевле — 131k помещается
-fa on --fit on --load-mode none -tb 12
-ctk q4_0 -ctv q4_0
--spec-type draft-mtp --spec-draft-n-max 5 --spec-draft-n-min 1 --spec-draft-p-min 0.5
--reasoning-budget 8192                         # ограничиваем think
--jinja --temp 0.6
```

- `-np 1` — один слот: на 16 ГБ `-np 2` делит контекст и стоит ~15 % скорости.
- `-c` подбирается **по бюджету VRAM, а не «на максимум»**: перегруз валит спекуляцию (до −45 %) и
  роняет слои на CPU. Как посчитать свой — [docs\research\context-memory-model.md](docs/research/context-memory-model.md):
  формула + `bench\vram_model.py`
  (`.\.venv\Scripts\python.exe bench\vram_model.py --model <model.gguf> --tk q4_0 --tv q4_0`).
- `-ctk/-ctv q4_0` — экономит 0.5–2 ГБ и поднимает контекст; до 49k качество не страдает, но `q4_0`
  **не** быстрее f16 (`f16 ≥ q4_0 > q8_0`). С квантованным V обязателен `-fa on`.
- `--spec-draft-n-max 5`, `--spec-draft-p-min 0.5…0.75` — рабочая глубина MTP (`nmax 8` хуже, под
  копирование кода берут `3`); `p-min` — порог для драфта: 0.75 консервативнее и даёт более высокое
  принятие. `-md` нужен для внешнего драфта Gemma; у Qwen3.6 MTP-голова встроена.
- `--reasoning off` / `--reasoning-budget` — рабочий режим RP — NoThink; у думающих Qwen бюджет
  просто не даёт think разрастаться.
- `--temp 0.6 --min-p 0.1` — безопасная точка для русского; точный пресет подбирается под модель
  ([docs\quality\sampling-quality.md](docs/quality/sampling-quality.md)).

## Чего избегать (проверено)

- `top-k` (включая официальный пресет Gemma-4 `top-k 64`) и высокую температуру на русском — до
  ~25 % брака против ~4 % при `temp 0.4` ([docs\quality\sampling-quality.md](docs/quality/sampling-quality.md)).
- EAGLE-3 и DSpark на 16 ГБ — в 1.4–3 раза медленнее MTP.
- `--spec-draft-n-max 8 --spec-draft-p-min 0.8` вне копирования кода; `ngram` в одиночку слабее MTP;
  DFlash+ngram — только для Qwen3.6 на коде.
- `-ncmoe` на влезающей модели, `-ub 2048`, контекст «на всю память», `-fa off` с квантованным V.
- «Играть температурой» ради скорости: TG не меняется (±3 %), растёт только принятие спекуляции.
- Второй `llama-server` при занятой VRAM — слои уедут на CPU, генерация падает примерно вдвое.

## Где подробности

Полный индекс — [docs\README.md](docs/README.md). Главные точки входа:

| Что | Где |
| --- | --- |
| Реестр проверенного (не повторять исследования) | [docs\researched.md](docs/researched.md) |
| Реестр моделей: тесты, вердикты, кандидаты, облако | [docs\models.md](docs/models.md) |
| **RP-рейтинг: Think/NoThink, панель 4 судей** | [docs\quality\rp-ranking.md](docs/quality/rp-ranking.md) |
| Методика оценки RP и полные разборы | [docs\quality\rp-quality-eval.md](docs/quality/rp-quality-eval.md) |
| Русский текст и сэмплинг | [docs\quality\sampling-quality.md](docs/quality/sampling-quality.md) |
| Спекуляция: MTP/DFlash/EAGLE, сравнение сборок | [docs\research\speculation-research.md](docs/research/speculation-research.md) |
| KV-кэш: качество, память, контекст | [docs\research\kv-cache-quantization.md](docs/research/kv-cache-quantization.md) |
| **Как посчитать контекст под свою VRAM** | [docs\research\context-memory-model.md](docs/research/context-memory-model.md), [bench\vram_model.py](bench/vram_model.py) |
| Длинные сессии, «бесконечный» контекст, SillyTavern | [docs\research\context-infinite-chat.md](docs/research/context-infinite-chat.md) |
| Роутер-режим | [docs\research\router-mode.md](docs/research/router-mode.md) |
| Логи по моделям | [docs\models](docs/models) |
| Сырые замеры | [bench\runs\results.jsonl](bench/runs/results.jsonl) |
| Скилы: подбор конфига новой модели / RP-оценка | [.opencode\skills\llm-launch-tuner](.opencode/skills/llm-launch-tuner), [.opencode\skills\rp-model-eval](.opencode/skills/rp-model-eval) |

## Воспроизведение замеров

```powershell
cd <папка проекта>
# один раз: скопировать bench\env.example.json в bench\env.local.json и указать свои пути
.\.venv\Scripts\python.exe bench\bench.py bench\suites\real\real_qwen36.json   # прогон набора
.\.venv\Scripts\python.exe bench\report.py                                     # сводка
```

RP-качество — одной командой через скил [.opencode\skills\rp-model-eval](.opencode/skills/rp-model-eval)
(скрин 2 сценария → панель 4 судей → баллы); ход прогона виден в `logs\rp_eval_<имя>_<stamp>.log`.
Перед публикацией изменений — `.\.venv\Scripts\python.exe bench\sanitize.py` (личные пути →
плейсхолдеры). Правила работы с репозиторием — [AGENTS.md](AGENTS.md).

Повторяющийся «тест-заполнитель» (`target`) — только стресс-тест спекуляции: он завышает TG
в 1.5–2 раза и в итоговые таблицы не попадает.
