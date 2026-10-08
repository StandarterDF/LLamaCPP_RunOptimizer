# Датасеты для RP/DRP/ERP (EN и RU) — внешний ресёрч

Срез: **2026-10-08**. Задача: собрать пул датасетов, которые можно (1) взять как есть для
SFT/файнтюна RP-модели и (2) **перевести EN→RU**, чтобы получить русскую RP-модель сильнее
текущих (`Runeweaver/Hydra-RP-RU`, `Pathfinder-RP-RU`, `Slimaki-Tavern`, `Katarau` —
см. `docs\research\qwen-mistral-rp-candidates.md` §2.5). Опора: наш вывод, что язык держится не
типом модели, а **языком обучающих данных** (`docs\research\why-ru-models.md` §5–6), поэтому
перевод качественного англоязычного RP-корпуса — прямой путь к русской модели.

## 0. Методика и ограничения

- Источники: **HF Dataset API** (`/api/datasets`, `/api/datasets/<id>`, README карточек) — снято
  `downloads`/`likes`/`lastModified`/`cardData` (license, language, size_categories) **08.10.2026**;
  HF-поиск по 30+ запросам; GitHub (awesome-llm-role-playing-with-persona, RPRevamped);
  arXiv (RoleLLM 2310.00746, CoSER 2502.09082, OpenCharacter 2501.15427, KokoroChat 2603.22913).
- **Проверено**: существование репо (API вернул карточку), лицензия/язык/категория размера — из
  `cardData`. Числа строк/диалогов — из README карточек, где они указаны явно.
- **Не проверено**: фактическая разметка, качество и токсичность внутри файлов (карточки не читали
  построчно); для части датасетов лицензия «unknown»/«other» — это риск, а не подтверждение.
- «Размер» в таблицах — категория HF (`size_categories`) либо явные строки из карточки. Где не
  указано — «н/д».
- Даты устаревания: HF-числа быстро меняются; всё помечено как срез 08.10.2026.

## 1. Главные выводы

1. **EN-пул RP/ERP огромен и качественен, но «старый».** Ядро (PIPPA, LimaRP, Roleplay-Forums,
   Sonnet3.5-Charcard) — 2023–2024; новое (2025–2026) — в основном переупаковки и CoT/DPO-надстройки.
2. **Лучшие кандидаты на перевод — не «сырые форумы», а готовые SFT-диалоги**: PIPPA (26k диалогов),
   LimaRP (~2k выверенных), Sonnet3.5-Charcard (9.7k карточных сцен), CoSER (диалоги из 771 романа).
3. **RU-native RP-датасетов мало и они слабые.** Крупнейшие — уже **переводы EN-корпусов**
   (`Arketov/ru_roleplay_conversation` из lima+pippa+bluemoon) либо **сырые логи** с chub.ai
   (`Arketov/ru_roleplay_conversation_chub`, 6 548 строк) и **RU-NSFW-фикшн** (`krplt/ru-fictext-nsfw`).
   Готового «золотого» RU-RP-датасета нет — это и есть окно возможностей.
4. **Самая дешёвая ставка:** взять PIPPA + LimaRP + Sonnet3.5-Charcard, перевести диалоги на русский
   LLM-переводчиком (с глоссарием и сохранением плейсхолдеров), добавить RU-native `chub`-логи как
   «живой» стиль и `ru-fictext-nsfw` для ERP. Это закрывает и character-RP, и ERP, и длинный контекст.
5. **Риски, которые надо решать до обучения:** лицензии (`cc-by-nc-4.0`, `unknown`, «other»,
   фанфикшн-копирайт), NSFW-легальность, шум в форумных корпусах, «переводной канцелярит» при MT.

---

## 2. Англоязычные RP-датасеты (общие, карточки персонажей, память)

«Тип»: SFT — готовые диалоги для обучения; DPO — пары предпочтений; benchmark — только оценка;
pre-training — сырой текст. «Перевод EN→RU»: ✅/⚠️/❌ + объём диалоговой части.

| Датасет | Язык | Размер | Тип / формат | Лицензия | Происхождение | EN→RU | Вердикт |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **[PygmalionAI/PIPPA](https://huggingface.co/datasets/PygmalionAI/PIPPA)** | en | ~26 000 диалогов, >1 млн реплик (10K<n<100K) | SFT, Character.AI-логи, JSONL (custom) | apache-2.0 | частью синтетика + реальные логи с согласия; NSFW, 1000+ персон | ✅ высокая доля диалогов, но много шума/повторов | **Брать + переводить (№1)** |
| **[lemonilia/LimaRP](https://huggingface.co/datasets/lemonilia/LimaRP)** | en | ~2 000 диалогов (1K<n<10K) | SFT, human-human, YAML→completion | apache-2.0 | **человеческие**, курированы вручную (>500 ч), NSFW/extreme | ✅ мало, но высшее качество; MT-риск на сленге | **Брать + переводить (эталон качества)** |
| **[lemonilia/Roleplay-Forums_2023-04](https://huggingface.co/datasets/lemonilia/Roleplay-Forums_2023-04)** | en | **35 212 830 строк** (1M<n<10M) | pre-training, сырой HTML с форумов | cc-by-4.0 | человеческие, **не очищено**, ~47 ГБ | ⚠️ огромно, не диалоги, нужен свой парсер | **Только как корпус претрейна** (не брать как SFT) |
| **[lemonilia/roleplaying-forums-raw](https://huggingface.co/datasets/lemonilia/roleplaying-forums-raw)** | en | 100K<n<1M | pre-training, частично очищенные форумы | cc-by-4.0 | человеческие | ⚠️ то же, но чище | Ограниченно (претрейн/стиль) |
| **[Gryphe/Sonnet3.5-Charcard-Roleplay](https://huggingface.co/datasets/Gryphe/Sonnet3.5-Charcard-Roleplay)** | en | **9 736 диалогов** (1K<n<10K) | SFT, character-card сцены, JSON/ShareGPT | **unknown** | синтетика (unrestrained Sonnet 3.5), ~19.6 ходов, NSFW | ✅ отличный кандидат (однозвенный сюжет, живой стиль) | **Переводить** (лицензия — риск) |
| **[sinhal/Charcard-Roleplay-ShareGPT-NSFW](https://huggingface.co/datasets/sinhal/Charcard-Roleplay-ShareGPT-NSFW)** | en | **9 736** (ShareGPT, ~165 МБ) | SFT, ShareGPT JSONL, multi-turn | cc-by-4.0 | синтетика (Sonnet 3.5), NSFW, 2026-08 | ✅ лучшая лицензионная альтернатива предыдущему | **Переводить (предпочтительно)** |
| **[hieunguyenminh/roleplay](https://huggingface.co/datasets/hieunguyenminh/roleplay)** | en | **5 755 строк** (1K<n<10K) | SFT, карточка + 3–5 реплик (parquet) | cc-by-4.0 | синтетика/ручное, original-персоны | ✅ малый объём, чистая структура | Брать + переводить (добор) |
| **[rickRossie/bluemoon_roleplay_chat_data_300k_messages](https://huggingface.co/datasets/rickRossie/bluemoon_roleplay_chat_data_300k_messages)** | en | **261 071 сообщение** (100K<n<1M) | SFT/сырьё, форум Bluemoon RP, plain | **н/д** | **человеческие** логи | ⚠️ нужна реконструкция тредов → диалогов | Брать как «живой стиль» после очистки |
| **[agentlans/combined-roleplay](https://huggingface.co/datasets/agentlans/combined-roleplay)** | en | 1M<n<10M (21 конфиг) | SFT, агрегатор (multiturn_mix, SODA, RPGPT…) | **н/д** | смешанное, часть синтетика | ✅ готовые ShareGPT-миксы, удобно переводить | Брать (готовый микс) |
| **[Neph0s/CoSER](https://huggingface.co/datasets/Neph0s/CoSER)** | en | 100M<n<1000M | SFT, диалоги из **771 романа** + профили/мысли, ShareGPT | mit | **человеческие** (литература) | ✅ высокое качество прозы, но не ERP; переводить только диалоги | Переводить (проза/память) |
| **[Neph0s/CoSER-Books-Gutenberg](https://huggingface.co/datasets/Neph0s/CoSER-Books-Gutenberg)** | en | 10M<n<100M | сырьё/диалоги из Gutenberg | mit | человеческие | ✅ | Переводить (пул диалогов) |
| **[ZenMoore/RoleBench](https://huggingface.co/datasets/ZenMoore/RoleBench)** | zh, en | **168 093 сэмпла** (RoleLLM) | SFT + benchmark, инструкции/диалоги | apache-2.0 | синтетика (ChatGPT/GPT) | ✅ крупный, но «плоский» стиль | Брать + переводить (объём) |
| **[xywang1/OpenCharacter](https://huggingface.co/datasets/xywang1/OpenCharacter)** | en | 100K<n<1M | SFT, синтетические персоны + диалоги | apache-2.0 | синтетика (self-instruct, масштабные персоны) | ✅ хороший объём, карточки персонажей | Переводить |
| **[IlyaGusev/gpt_roleplay_realm](https://huggingface.co/datasets/IlyaGusev/gpt_roleplay_realm)** | **ru, en** | 216 en + 219 ru персонажей × 20 диалогов (~8.7k) | SFT, карточки + диалоги (image/messages) | cc-by-4.0 | синтетика GPT-4/3.5, Kandinsky-карточки | ✅ **уже двуязычный** — русский готов | Брать как есть (RU-ветка) |
| **[beyoru/Aesir-Character-CoT-roleplay](https://huggingface.co/datasets/beyoru/Aesir-Character-CoT-roleplay)** | en | 1K<n<10K | SFT, character CoT (рассуждение+ответ) | apache-2.0 | синтетика (DeepSeek, «reasoning-effort-max») | ⚠️ CoT-трейсы переводить рискованно | Брать (non-think RP) / CoT — осторожно |
| **[CausalLM/Kingfall-Roleplay](https://huggingface.co/datasets/CausalLM/Kingfall-Roleplay)** | en, zh, ja, de | 10K<n<100K | SFT, RP | wtfpl | синтетика, 2026-05 | ✅ | Брать + переводить |
| **[scryptiam/anime-waifu-personality-chat](https://huggingface.co/datasets/scryptiam/anime-waifu-personality-chat)** | en | 1K<n<10K | SFT, persona-chat (anime) | cc-by-4.0 | синтетика | ✅ | Брать (аниме-ниш) |
| **[zerofata/Roleplay-Anime-Characters](https://huggingface.co/datasets/zerofata/Roleplay-Anime-Characters)** | en | n<1K | SFT, anime RP | н/д | синтетика | ⚠️ очень мало | Добор |
| **[MiniMaxAI/role-play-bench](https://huggingface.co/datasets/MiniMaxAI/role-play-bench)** | zh, en | 1K<n<10K | **benchmark** (seeds/dialogues/evaluations) | apache-2.0 | человеческое+синтетика | ❌ не для обучения | Только оценка (152 лайка) |

**Пояснения.**
- **PIPPA** — де-факто стандарт обучения RP-моделей; даёт character-consistency и NSFW, но шумная:
  перед переводом нужны дедуп и обрезка «echo chamber»-ходов.
- **LimaRP** — эталон «человеческого» RP/ERP; несмотря на объём, даёт самый естественный стиль;
  карточка прямо предупреждает об extreme-контенте.
- **Sonnet3.5-Charcard** — современный «карточный» формат (как в SillyTavern): ровно то, что нужно
  RP-модели. Лицензия `unknown`; CC-BY-переупаковка `sinhal/...` снимает этот риск.
- **CoSER** — литературные диалоги, идеальны для «проза + память», но это не ERP и много нарратива;
  переводить только реплики, а не весь текст.
- **Roleplay-Forums / roleplaying-forums-raw** — не SFT, а сырьё под continual pre-training; как
  диалоговый SFT без серьёзной обработки не годятся (карточка прямо это пишет).

---

## 3. ERP / NSFW / uncensored RP-датасеты (EN в первую очередь)

| Датасет | Язык | Размер | Тип / формат | Лицензия | Происхождение | EN→RU | Вердикт |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **[ResplendentAI/NSFW_RP_Format_DPO](https://huggingface.co/datasets/ResplendentAI/NSFW_RP_Format_DPO)** | en | n<1K | **DPO-пары** (RP-формат, NSFW) | apache-2.0 | синтетика | ⚠️ предпочтения, не SFT | Брать (DPO-этап) |
| **[deebosh/NSFW_RP_Format_DPO-ru](https://huggingface.co/datasets/deebosh/NSFW_RP_Format_DPO-ru)** | ru | n<1K | **DPO-пары**, RU | н/д | синтетика, 2026-02 | — (уже RU) | Брать как RU-DPO (проверить объём) |
| **[athirdpath/DPO_Pairs-Roleplay-NSFW](https://huggingface.co/datasets/athirdpath/DPO_Pairs-Roleplay-NSFW)** | en | 1K<n<10K | DPO-пары | **cc-by-nc-4.0** | синтетика | ❌ NC-лицензия (некоммерч.) | Осторожно (NC) |
| **[athirdpath/DPO_Pairs-Roleplay-Alpaca-NSFW](https://huggingface.co/datasets/athirdpath/DPO_Pairs-Roleplay-Alpaca-NSFW)** | en | 1K<n<10K | DPO-пары | cc-by-nc-4.0 | синтетика | ❌ NC | Осторожно (NC) |
| **[ChaoticNeutrals/Reddit-NSFW-Writing_Prompts_ShareGPT](https://huggingface.co/datasets/ChaoticNeutrals/Reddit-NSFW-Writing_Prompts_ShareGPT)** | en | 1K<n<10K | SFT, ShareGPT (writing prompts) | **other** | синтетика/реальные промпты, NSFW | ✅ | Брать (стиль/ERP) |
| **[erpgen/nsfw-writing-prompts](https://huggingface.co/datasets/erpgen/nsfw-writing-prompts)** | en | н/д | SFT, промпты/текст | apache-2.0 | синтетика | ✅ | Брать |
| **[sdsr/erp-and-erotica](https://huggingface.co/datasets/sdsr/erp-and-erotica)** | en | **10M<n<100M** | SFT/сырьё, ERP+эротика | н/д | вероятно синтетика/скрейп, 2026-03 | ⚠️ очень много, нужен фильтр | Брать после фильтрации (объём) |
| **[bluuwhale/nsfwstory](https://huggingface.co/datasets/bluuwhale/nsfwstory)** | en | 10K<n<100K | SFT/сырьё, NSFW-истории | **unknown** | н/д | ⚠️ | Добор (осторожно) |
| **[Sao10K/FastChat_Erotica](https://huggingface.co/datasets/Sao10K/FastChat_Erotica)** | en | н/д (мало) | SFT, эротика | н/д | н/д | ⚠️ мало | Добор |
| **[Casual-Autopsy/Slop-Forensics_Nitral-AI_NSFW-SFW-Writing-Prompts-Mix-125x2](https://huggingface.co/datasets/Casual-Autopsy/Slop-Forensics_Nitral-AI_NSFW-SFW-Writing-Prompts-Mix-125x2)** | en | н/д | SFT, микс NSFW/SFW промптов | н/д | синтетика | ✅ | Добор |
| **[SuperbEmphasis/Deepseek-R1-ERP-Dataset](https://huggingface.co/datasets/SuperbEmphasis/Deepseek-R1-ERP-Dataset)** | en | 1K<n<10K | SFT, ERP с reasoning-трейсами (R1) | **gated (auto)** | синтетика DeepSeek-R1 | ⚠️ трейсы на англ. | Осторожно (reasoning на RU течёт) |
| **[ganjaninja/writing-prompts-sfw-nsfw-interleaved](https://huggingface.co/datasets/ganjaninja/writing-prompts-sfw-nsfw-interleaved)** | en | н/д | SFT, интерлив NSFW/SFW | н/д | синтетика | ✅ | Добор |

**Пояснения.**
- Свежие ERP-датасеты 2025–2026 почти все **синтетические** (DeepSeek/Claude/GPT) и мелкие;
  крупных «человеческих» ERP-корпусов, кроме LimaRP и `sdsr/erp-and-erotica`, нет.
- `cc-by-nc-4.0` у DPO-пар — **некоммерческая** лицензия: для локального research-файнтюна ок,
  для публикации модели — риск.
- Reasoning-ERP (`Deepseek-R1-ERP-Dataset`) для RU опасен: наши замеры показывают, что thinking
  часто утекает в английский (`docs\research\why-ru-models.md` §5.2, п.2).

---

## 4. Dark RP / TTRPG / интерактивная проза / длинная память

| Датасет | Язык | Размер | Тип / формат | Лицензия | Происхождение | EN→RU | Вердикт |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **[ChaoticNeutrals/Synthetic-Dark-RP](https://huggingface.co/datasets/ChaoticNeutrals/Synthetic-Dark-RP)** | en | n<1K | SFT, dark RP | **agpl-3.0** | синтетика | ⚠️ очень мало | Добор (лицензия AGPL) |
| **[m0no1/dnd-35-training-dataset](https://huggingface.co/datasets/m0no1/dnd-35-training-dataset)** | en | 10K<n<100K | SFT/QA, D&D 3.5 (механика+лор) | mit | синтетика (Qwen) | ✅ (термины D&D — глоссарий) | Брать (DRP-лор) |
| **[PocketDoc/Choose-Your-Story-Long-Text-Adventures](https://huggingface.co/datasets/PocketDoc/Choose-Your-Story-Long-Text-Adventures)** | en | н/д | SFT, интерактивная проза | н/д | синтетика | ✅ | Брать (IF/DRP) |
| **[PocketDoc/Floyd-Text-Adventures](https://huggingface.co/datasets/PocketDoc/Floyd-Text-Adventures)** | en | н/д | SFT, text-adventure | н/д | синтетика | ✅ | Брать (IF) |
| **[exnihilum/ttrpg-rpg-fandom-com-en](https://huggingface.co/datasets/exnihilum/ttrpg-rpg-fandom-com-en)** | en, ru | н/д | pre-training, TTRPG-фандом | cc-by-sa-4.0 | человеческие вики | ✅ | Добор (лор/претрейн) |
| **[xiaowu0162/LongMemEval](https://huggingface.co/datasets/xiaowu0162/longmemeval)** | en | benchmark (~500 вопросов) | **benchmark** длинной памяти | mit | синтетика | ❌ не для обучения | Только оценка памяти |
| **[allenai/WildChat-1M](https://huggingface.co/datasets/allenai/WildChat-1M)** | multi (в осн. en) | 100K<n<1M | сырьё, реальные логи (есть RP/NSFW) | odc-by | **человеческие** (ChatGPT) | ⚠️ фильтровать RP/NSFW | Брать как донор стиля (после фильтра) |
| **[lmsys/lmsys-chat-1m](https://huggingface.co/datasets/lmsys/lmsys-chat-1m)** | multi | 1M<n<10M | сырьё, реальные логи | gated, смотреть карточку | человеческие | ⚠️ | Ограниченно (gated) |

---

## 5. Готовые русскоязычные RP-датасеты (даже небольшие)

| Датасет | Язык | Размер | Тип / формат | Лицензия | Происхождение | Вердикт |
| --- | --- | --- | --- | --- | --- | --- |
| **[Arketov/ru_roleplay_conversation](https://huggingface.co/datasets/Arketov/ru_roleplay_conversation)** | ru | 10K<n<100K | SFT, **перевод lima+pippa+bluemoon**, NSFW | н/д | MT-перевод EN-корпусов; карточка: «нужна доп. фильтрация, редко дубли» | **Брать как есть + чистить** |
| **[Arketov/ru_roleplay_conversation_chub](https://huggingface.co/datasets/Arketov/ru_roleplay_conversation_chub)** | ru, en | **6 548 строк** (811 МБ) | SFT, **сырые RP-логи с chub.ai** (en+ru поля, персона+сценарий) | н/д | человеческие логи, нефильтрованные, NSFW | **Брать (RU-native, живой стиль)** |
| **[Arketov/hieunguyenminh_roleplay-deduped-ShareGPT_ru](https://huggingface.co/datasets/Arketov/hieunguyenminh_roleplay-deduped-ShareGPT_ru)** | ru, en | 1K<n<10K (карточка: n<1K) | SFT, ShareGPT, перевод | н/д | MT-перевод | Брать (добор) |
| **[krplt/ru-fictext-nsfw](https://huggingface.co/datasets/krplt/ru-fictext-nsfw)** | ru | 10K<n<100K | SFT/сырьё, **RU-NSFW-фанфик** (ficbook.net) | cc-by-4.0 | человеческие, преимущественно NSFW | **Брать (ERP/проза, RU-native)** |
| **[march228/factual-multiagent-roleplay-ft-ru](https://huggingface.co/datasets/march228/factual-multiagent-roleplay-ft-ru)** | ru | **902 примера** | SFT, персона + factual grounding + thoughts | other | синтетика, 2026-03 | Брать (факт/память в роли) |
| **[secretmoon/ru-roleplay](https://huggingface.co/datasets/secretmoon/ru-roleplay)** | ru | мало | SFT, RU RP | mit | н/д (связан с YankaGPT — см. `rp-model-candidates.md` §3) | Осторожно (проверить качество) |
| **[qklent/roleplay_ru_gusev_preprocessed](https://huggingface.co/datasets/qklent/roleplay_ru_gusev_preprocessed)** | ru | 1K<n<10K | SFT, препроцесс RU roleplay (на базе Gusev) | н/д | синтетика/перевод | Добор |
| **[IlyaGusev/gpt_roleplay_realm](https://huggingface.co/datasets/IlyaGusev/gpt_roleplay_realm) (ru split)** | ru, en | 219 персонажей × 20 диалогов | SFT, карточки + диалоги | cc-by-4.0 | синтетика GPT-4/3.5 | **Брать (готовый RU)** |
| **[Den4ikAI/russian_dialogues](https://huggingface.co/datasets/Den4ikAI/russian_dialogues)** | ru | 1M<n<10M | SFT/сырьё, **общие диалоги** (не RP) | mit | человеческие | Только как языковой корпус (не RP) |
| **[OpenAssistant/oasst1](https://huggingface.co/datasets/OpenAssistant/oasst1)** | 35 языков, вкл. **ru** | 100K<n<1M | SFT, ассистент-диалоги (не RP) | apache-2.0 | человеческие | Языковая база, не RP |
| **[40umov/dostoevsky](https://huggingface.co/datasets/40umov/dostoevsky)** / **[Vikhrmodels/dostoevsky_scored](https://huggingface.co/datasets/Vikhrmodels/dostoevsky_scored)** | ru | 1K<n<10K | SFT, литературный стиль (не RP) | unknown / н/д | человеческие | Стиль/проза, не RP |
| **[IlyaGusev/saiga_scored](https://huggingface.co/datasets/IlyaGusev/saiga_scored)** | ru | 10K<n<100K | SFT, инструкции RU (scored) | н/д | синтетика+человеческие | Языковая база (не RP) |

**Пояснения.**
- **`Arketov/ru_roleplay_conversation`** — самый прямой аналог того, что мы собираемся делать, но
  автор сам пишет «нужна дополнительная фильтрация» и «есть редкие дубликаты»: это сырой MT-перевод.
  Ценность — как baseline и как источник идей по пайплайну.
- **`Arketov/ru_roleplay_conversation_chub`** — редкий **RU-native** корпус реальных логов с chub.ai
  (6 548 диалогов, поля и en, и ru — можно использовать как параллельный корпус для оценки перевода).
- **`krplt/ru-fictext-nsfw`** — крупнейший RU-NSFW-текстовый корпус (fanfiction), но это **проза, а не
  диалог**: годится для ERP-стиля и словаря, не для multi-turn структуры.
- Проект уже отметил `katafiek/Katarau-9B-ru-RP-nsfw` (обучен на ~41.7 млн токенов русского RP;
  датасет gated) — см. `docs\research\qwen-mistral-rp-candidates.md` §2.5; **не проверено** нами.

---

## 6. Пайплайн перевода EN→RU (рекомендации)

**Цель:** получить русские диалоги, которые звучат как живая речь, а не как «переводной канцелярит»,
с сохранением имён, терминов и структуры ролей.

### 6.1. Инструменты (от качества к скорости)

| Инструмент | Плюсы | Минусы | Когда брать |
| --- | --- | --- | --- |
| **LLM-переводчик** (Qwen3.x / Gemma-4-31B / DeepSeek / GPT / Claude) с few-shot + глоссарием | лучше всех держит стиль, сленг, ERP; управляемый тон | дорого по токенам, нужен контроль | **Основной путь** для диалогов |
| **Multi-LLM ensemble** (KokoroChat, arXiv 2603.22913): гипотезы от нескольких LLM → один LLM выбирает/синтезирует | превосходит любую одиночную модель по fidelity | ×N стоимости | Для самых важных подмножеств (LimaRP) |
| **NLLB-200** (`facebook/nllb-200-distilled-600M`) | быстро, локально, 200 языков | «гладко, но безлико», теряет сленг/ERP | Черновой прогон, затем post-edit LLM |
| **MarianMT** (`Helsinki-NLP/opus-mt-en-ru`) | очень быстро, локально | слаб на разговорной речи, буквализм | Только baseline/сравнение |
| **DeepL / Google Translate** | высокая беглость | $, дрейф терминов, нет контроля стиля | Если нужен «просто перевод» без RP-тона |

### 6.2. Сохранение имён и терминов
- **Глоссарий + плейсхолдеры:** защищать `{{char}}`, `{{user}}`, `{user}`, `[tags]`, `*действия*`,
  `(OOC)`, markdown-разметку до перевода (замена на sentinel-токены), восстанавливать после.
- **Имена собственные:** политика «не переводить, только транслитерировать при необходимости»;
  единый словарь транслитерации (чтобы `Astaroth` был всегда одним и тем же).
- **Лор/термины:** NER-прогон → словарь `EN→RU` → подавать в промпт перевода; проверять по подстроке,
  что термин действительно использован (терминологически-ограниченный MT, WMT-2023/2024).
- **Формат:** переводить **только диалоги**, а не всю карточку; сохранять разбиение по ходам и ролям
  (ShareGPT `from/to`), чтобы не сломать multi-turn структуру.

### 6.3. Как избежать «переводного канцелярита» в RP
- Промпт: «переведи как **живую разговорную речь персонажа**, без канцелярита и кальки; сохрани
  характер, тон, длину реплик, междометия; ERP — прямые формулировки без эвфемизмов».
- Отдельный **стиль на жанр** (dark fantasy / ERP / anime) — свой tone-пресет.
- **Post-edit проход** вторым LLM («сделай русский естественнее, не меняй смысл и имена»).
- **Калибровка на 100–300 парах** вручную, затем масштабирование.

### 6.4. Оценка качества перевода
- **MT-метрики:** chrF/BLEU (быстро, но не про RP), **COMET** (лучше коррелирует с человеком).
- **LLM-судья:** pairwise «A vs B» по естественности, сохранению характера, отсутствию кальки;
  **сравнивать только внутри одного судьи** (как в нашем `bench\quality\rp_judge.py`).
- **RP-специфичное:** сохранены ли имена/факты/действия, нет ли смены языка (наши метрики «Чисто %»,
  PPL на русском — `docs\research\why-ru-models.md`), длина/структура ходов.
- **Контрольный прогон:** обучить/оценить на переведённом наборе нашим RP-харнессом
  (`docs\quality\rp-quality-eval.md`) и сравнить с текущими RU-моделями.

### 6.5. Практика и бюджет
- Дедуп **до** перевода (PIPPA шумная), фильтр «echo chamber» (длинные AI-on-AI ходы).
- Оценка стоимости: LLM-перевод ~1 токен выхода ≈ 1 токен входа × k; для PIPPA (>1M реплик) —
  это главный расход; переводить выборочно (топ-персоны, лучшие сцены).
- Хранить **EN-оригинал и RU-перевод рядом** (параллельный корпус) — нужен для судьи и для
  дообучения/контроля качества.

---

## 6.6. Что делает сам Hugging Face: FineTranslations (срез 2026-01)

У HF **есть собственный масштабный проект перевода датасетов** — `HuggingFaceFW/finetranslations`
(>1 трлн токенов параллельного текста, EN + 500+ языков, odc-by). Это прямой ответ на вопрос
«что HF думает про перевод данных»:

- **Направление — INTO English.** Взяли **не-английский FineWeb2** и перевели **в английский**
  моделью **Gemma 3 27B**. Причина (цитата карточки): модели сильны в X→English, а обратное
  (English→X) слабо, особенно для малоресурсных языков. То есть датасет сделан, чтобы **дообучать
  MT на English→X**. Побочно: переведённый английский несёт культурную информацию и по качеству
  ≈ FineWeb для English-only обучения.
- **Пайплайн открыт** (`github.com/huggingface/finetranslations`, `datatrove`): отбор языков
  (`bible_wiki_ratio < 0.5` → ~500 языков), до 50B токенов/язык, **чанки по 512 токенов со скользящим
  окном**, early-exit-классификатор adult/spam **до** перевода, строгие правила форматирования,
  пост-обработка, свой edu-классификатор (FineWeb-Edu к Gemma-тексту не подошёл). 3 месяца на кластере HF.
- **Честные ограничения (их же слова):** качество перевода неравномерно (низкоресурсные хуже);
  форматирование сохраняется не всегда; чанкинг теряет связность на границах; возможны токсичный
  контент и ошибки; «переводы могут читаться не так естественно, как человеческие».
- **Но флагманский многоязычный корпус HF (`fineweb-2`) — НЕ переводной**, а **нативный** по языкам,
  с индивидуально настроенными фильтрами/стоп-словами на каждый язык. Для претрейна HF предпочитает
  native; перевод — отдельный инструмент (параллельные данные для MT + англоязычный корпус).

**Вывод для нас:** перевод — легитимный и масштабируемый метод (у HF есть готовый пайплайн и модель),
но **English→X — заведомо слабое направление** (HF строил датасет именно чтобы его починить). Для RP/ERP
это тем рискованнее (стиль, сленг, ERP-термины), поэтому наш путь — **EN→RU + post-edit + LLM-судья**
(`§6.1–6.4`), а не «сырой» MT. Родственно: `finetranslations-edu`, а также открытая семья
**TranslateGemma** (Google, Gemma 3, 55 языков, arXiv 2601.09012).

## 7. Топ-5 рекомендаций

| # | Датасет | Действие | Почему |
| --: | --- | --- | --- |
| 1 | **PygmalionAI/PIPPA** | **Переводить EN→RU** | Максимальный объём диалогов (26k), 1000+ персон, NSFW, apache-2.0; де-факто стандарт RP-обучения. Даёт character-consistency и разнообразие. |
| 2 | **lemonilia/LimaRP** | **Переводить EN→RU** (лучший MT, LLM-ensemble) | ~2k **человеческих** выверенных RP/ERP-диалогов — эталон стиля; малый объём → можно позволить дорогой перевод. |
| 3 | **Gryphe/Sonnet3.5-Charcard-Roleplay** (или CC-BY-переупаковка `sinhal/...`) | **Переводить EN→RU** | 9 736 современных «карточных» сцен, ровно формат SillyTavern/chub; однозвенный сюжет, живой стиль, NSFW. Брать CC-BY-версию из-за лицензии. |
| 4 | **Arketov/ru_roleplay_conversation_chub** | **Брать как есть + чистить** | 6 548 **RU-native** реальных RP-логов (chub.ai), двуязычные поля — готовый «живой» русский и параллельный корпус. |
| 5 | **Neph0s/CoSER** | **Переводить EN→RU (только диалоги)** | Диалоги из 771 романа: человеческое качество, естественный multi-turn, память/характер; лучший источник для «проза + связность» (mit). |

**Дополнительно брать как есть:** `IlyaGusev/gpt_roleplay_realm` (готовый RU-сплит, cc-by-4.0),
`krplt/ru-fictext-nsfw` (RU-ERP-проза), `agentlans/combined-roleplay` (готовые ShareGPT-миксы),
`march228/factual-multiagent-roleplay-ft-ru` (RU факт+персона).
**Не брать как SFT:** `lemonilia/Roleplay-Forums_2023-04` (сырой HTML, 35M строк — только претрейн),
`MiniMaxAI/role-play-bench` и `LongMemEval` (benchmark), `fujiiee/roleplay-bot-data` (это дамп
runtime-состояния бота, а не RP-диалоги — 40k загрузок обманчивы).

---

## 8. Итоговая таблица (датасет → язык → размер → тип → лицензия → вердикт)

| Датасет | Язык | Размер | Тип | Лицензия | Вердикт |
| --- | --- | --- | --- | --- | --- |
| PygmalionAI/PIPPA | en | 26k диалогов | SFT | apache-2.0 | **Переводить** |
| lemonilia/LimaRP | en | ~2k диалогов | SFT (human) | apache-2.0 | **Переводить** |
| Gryphe/Sonnet3.5-Charcard-Roleplay | en | 9 736 | SFT (char-card) | unknown | **Переводить** (CC-BY-версия) |
| sinhal/Charcard-Roleplay-ShareGPT-NSFW | en | 9 736 | SFT | cc-by-4.0 | **Переводить** |
| hieunguyenminh/roleplay | en | 5 755 | SFT | cc-by-4.0 | Брать/переводить |
| rickRossie/bluemoon_…300k | en | 261 071 сообщ. | сырьё/человек | н/д | Брать (чистить) |
| agentlans/combined-roleplay | en | 1M<n<10M | SFT-микс | н/д | Брать |
| Neph0s/CoSER | en | 100M<n<1000M | SFT (human, проза) | mit | **Переводить** |
| ZenMoore/RoleBench | zh,en | 168 093 | SFT+bench | apache-2.0 | Брать/переводить |
| xywang1/OpenCharacter | en | 100K<n<1M | SFT (synthetic) | apache-2.0 | Переводить |
| IlyaGusev/gpt_roleplay_realm | ru,en | ~8.7k диалогов | SFT | cc-by-4.0 | **Брать (RU готов)** |
| CausalLM/Kingfall-Roleplay | en,zh,ja,de | 10K<n<100K | SFT | wtfpl | Брать/переводить |
| beyoru/Aesir-Character-CoT | en | 1K<n<10K | SFT+CoT | apache-2.0 | Брать |
| scryptiam/anime-waifu-personality-chat | en | 1K<n<10K | SFT | cc-by-4.0 | Брать |
| lemonilia/Roleplay-Forums_2023-04 | en | 35 212 830 | претрейн (raw) | cc-by-4.0 | Не брать как SFT |
| MiniMaxAI/role-play-bench | zh,en | 1K<n<10K | benchmark | apache-2.0 | Только оценка |
| ResplendentAI/NSFW_RP_Format_DPO | en | n<1K | DPO | apache-2.0 | Брать (DPO) |
| deebosh/NSFW_RP_Format_DPO-ru | ru | n<1K | DPO | н/д | Брать (RU-DPO) |
| athirdpath/DPO_Pairs-Roleplay-NSFW | en | 1K<n<10K | DPO | cc-by-nc-4.0 | Осторожно (NC) |
| ChaoticNeutrals/Reddit-NSFW-Writing_Prompts_ShareGPT | en | 1K<n<10K | SFT | other | Брать |
| erpgen/nsfw-writing-prompts | en | н/д | SFT | apache-2.0 | Брать |
| sdsr/erp-and-erotica | en | 10M<n<100M | SFT/сырьё | н/д | Брать после фильтра |
| bluuwhale/nsfwstory | en | 10K<n<100K | SFT/сырьё | unknown | Добор |
| SuperbEmphasis/Deepseek-R1-ERP-Dataset | en | 1K<n<10K | SFT+CoT | gated | Осторожно |
| ChaoticNeutrals/Synthetic-Dark-RP | en | n<1K | SFT (dark) | agpl-3.0 | Добор |
| m0no1/dnd-35-training-dataset | en | 10K<n<100K | SFT/QA (DRP) | mit | Брать |
| PocketDoc/Choose-Your-Story-Long-Text-Adventures | en | н/д | SFT (IF) | н/д | Брать |
| PocketDoc/Floyd-Text-Adventures | en | н/д | SFT (IF) | н/д | Брать |
| xiaowu0162/LongMemEval | en | ~500 вопросов | benchmark | mit | Только оценка |
| allenai/WildChat-1M | multi | 100K<n<1M | сырьё | odc-by | Донор стиля (фильтр) |
| lmsys/lmsys-chat-1m | multi | 1M<n<10M | сырьё | gated | Ограниченно |
| **Arketov/ru_roleplay_conversation** | ru | 10K<n<100K | SFT (MT) | н/д | Брать+чистить |
| **Arketov/ru_roleplay_conversation_chub** | ru,en | 6 548 | SFT (RU-native) | н/д | **Брать** |
| Arketov/hieunguyenminh…_ru | ru,en | 1K<n<10K | SFT (MT) | н/д | Добор |
| krplt/ru-fictext-nsfw | ru | 10K<n<100K | сырьё (RU-ERP) | cc-by-4.0 | **Брать** |
| march228/factual-multiagent-roleplay-ft-ru | ru | 902 | SFT | other | Брать |
| secretmoon/ru-roleplay | ru | мало | SFT | mit | Осторожно |
| qklent/roleplay_ru_gusev_preprocessed | ru | 1K<n<10K | SFT | н/д | Добор |
| Den4ikAI/russian_dialogues | ru | 1M<n<10M | сырьё (не RP) | mit | Языковая база |
| OpenAssistant/oasst1 | multi (ru) | 100K<n<1M | SFT (не RP) | apache-2.0 | Языковая база |
| 40umov/dostoevsky / Vikhrmodels/dostoevsky_scored | ru | 1K<n<10K | SFT (стиль) | unknown | Стиль, не RP |
| IlyaGusev/saiga_scored | ru | 10K<n<100K | SFT (инстр.) | н/д | Языковая база |

---

## 9. Риски

| Риск | Где | Что делать |
| --- | --- | --- |
| **Некоммерческие лицензии** | `athirdpath/DPO_Pairs-*-NSFW` (cc-by-nc-4.0), `ChaoticNeutrals/Synthetic-Dark-RP` (AGPL), `sdsr/erp-and-erotica` (н/д) | NC — только некоммерчески; AGPL — copyleft. Полная таблица «можно ли публиковать перевод» — **§9.1** |
| **Лицензия `unknown`/`other`/нет** | Sonnet3.5-Charcard (unknown), `bluuwhale/nsfwstory`, RU-датасеты Arketov, bluemoon | **Нельзя** публиковать без разрешения автора; CC-BY-переупаковка (`sinhal`) прав не даёт, если оригинал без лицензии. См. **§9.1** |
| **NSFW/легальность** | PIPPA, LimaRP, все ERP | Фантазийный **текст**; проверять законодательство своей юрисдикции; не смешивать с реальными персонами |
| **Копирайт (фанфикшн/литература)** | CoSER (романы), `krplt/ru-fictext-nsfw` (ficbook.net), RoleBench (герои фильмов) | CoSER — public-domain/Gutenberg-часть; фанфикшн — риск, только research |
| **Шум/сырость** | Roleplay-Forums (HTML), bluemoon, WildChat | Дедуп, реконструкция тредов, фильтр «echo chamber», чистка от PII |
| **«Переводной канцелярит»** | Любой MT | LLM-перевод + post-edit + LLM-судья (см. §6) |
| **Reasoning-трейсы на англ.** | Deepseek-R1-ERP, Aesir-CoT, march228 | Для RU non-think — вырезать/не переводить трейсы (наш вывод: thinking утекает в EN) |
| **Объём/стоимость** | PIPPA (>1M реплик), sdsr (10M+) | Переводить выборочно, хранить пары EN/RU |
| **Даты/устаревание** | Все HF-числа | Срез 08.10.2026; перепроверять перед закупкой/скачиванием |

---

### 9.1. Лицензии и публикация производных (переводов) — проверено по HF API (08.10.2026)

**Правило:** перевод — это **производное произведение**, поэтому выложить перевод на свой HF можно
только если лицензия источника **разрешает производные** и ты соблюдаешь условия (атрибуция, ShareAlike,
NC и т.п.). Отдельно: **лицензия датасета не покрывает чужой контент внутри** (тексты книг, фанфики,
логи пользователей, форумные посты). Лицензии ниже сняты **по HF API** 08.10.2026 (поле `license`).

**✅ Можно перевести и опубликовать (permissive; нужна атрибуция + отметка «производное/изменено»):**

| Датасет | Лицензия | Условия / риски |
| --- | --- | --- |
| `PygmalionAI/PIPPA` | apache-2.0 | атрибуция; ⚠️ внутри **логи Character.AI + PII** пользователей |
| `lemonilia/LimaRP` | apache-2.0 | атрибуция; ⚠️ human-форумы (посты авторов), extreme |
| `lemonilia/Roleplay-Forums_2023-04`, `roleplaying-forums-raw` | cc-by-4.0 | атрибуция; ⚠️ сырые форумы (посты авторов), нужен парсер |
| `hieunguyenminh/roleplay` | cc-by-4.0 | атрибуция + отметить изменения |
| `xywang1/OpenCharacter` | apache-2.0 | синтетика |
| `IlyaGusev/gpt_roleplay_realm` | cc-by-4.0 | синтетика; **RU-ветка готова** |
| `beyoru/Aesir-Character-CoT-roleplay` | apache-2.0 | синтетика (CoT) |
| `scryptiam/anime-waifu-personality-chat` | cc-by-4.0 | синтетика |
| `CausalLM/Kingfall-Roleplay` | wtfpl | очень пермиссивно |
| `ZenMoore/RoleBench` | apache-2.0 | синтетика; ⚠️ персонажи из фильмов/книг |
| `MiniMaxAI/role-play-bench` | apache-2.0 | benchmark |
| `ResplendentAI/NSFW_RP_Format_DPO` | apache-2.0 | синтетика (DPO) |
| `erpgen/nsfw-writing-prompts` | apache-2.0 | синтетика |
| `m0no1/dnd-35-training-dataset` | mit | синтетика |
| `xiaowu0162/LongMemEval` | mit | benchmark |
| `Den4ikAI/russian_dialogues` | mit | human, **не RP** |
| `OpenAssistant/oasst1` | apache-2.0 | human, **не RP** |
| `secretmoon/ru-roleplay` | mit | мало объёма |
| `Neph0s/CoSER`, `CoSER-Books-Gutenberg` | mit | ✅ код/аннотации; ⚠️ **текст книг** — брать только public-domain/Gutenberg |
| `allenai/WildChat-1M` | odc-by | атрибуция; ⚠️ реальные ChatGPT-логи + PII |

**⚠️ Можно с условиями (copyleft / NC / custom / сомнительный провенанс):**

| Датасет | Лицензия | Условие |
| --- | --- | --- |
| `athirdpath/DPO_Pairs-Roleplay-NSFW`, `-Alpaca-NSFW` | cc-by-nc-4.0 | **только некоммерчески** (NC); выложить бесплатно — ок, пометить NC |
| `ChaoticNeutrals/Synthetic-Dark-RP` | agpl-3.0 | **copyleft**: производное обязано быть под AGPL |
| `exnihilum/ttrpg-rpg-fandom-com-en` | cc-by-sa-4.0 | **ShareAlike**: производное под той же лицензией |
| `krplt/ru-fictext-nsfw` | cc-by-4.0 | лицензия ок, но ⚠️ **фанфики** (копирайт) + extreme-теги |
| `ChaoticNeutrals/Reddit-NSFW-Writing_Prompts_ShareGPT` | other | кастомные условия — **читать карточку** |
| `march228/factual-multiagent-roleplay-ft-ru` | other | кастомные условия |
| `sinhal/Charcard-Roleplay-ShareGPT-NSFW` | cc-by-4.0 (заявлена) | ⚠️ оригинал (`Gryphe`) — **unknown**; чужой relicense прав не даёт |
| `SuperbEmphasis/Deepseek-R1-ERP-Dataset` | нет (gated `auto`) | условия при доступе; reasoning-трейсы |
| `lmsys/lmsys-chat-1m` | нет (gated `auto`) | свои условия; ⚠️ PII |

**❌ Нельзя без письменного разрешения автора (нет лицензии / `unknown`):**

| Датасет | Лицензия | Комментарий |
| --- | --- | --- |
| `Gryphe/Sonnet3.5-Charcard-Roleplay` | **unknown** | лучший RP-стиль, но лицензии нет → спросить Gryphe |
| `rickRossie/bluemoon…300k` | нет | сырые форумы (посты авторов) |
| `agentlans/combined-roleplay` | нет | агрегатор: у каждого конфига свой провенанс — проверять отдельно |
| `zerofata/Roleplay-Anime-Characters` | нет | — |
| `deebosh/NSFW_RP_Format_DPO-ru` | нет | — |
| `sdsr/erp-and-erotica` | нет | сырой HTML-дамп форума |
| `bluuwhale/nsfwstory` | unknown | — |
| `Sao10K/FastChat_Erotica` | нет | — |
| `ganjaninja/writing-prompts-sfw-nsfw-interleaved` | нет | — |
| `PocketDoc/Choose-Your-Story-Long-Text-Adventures`, `Floyd-Text-Adventures` | нет | — |
| `Arketov/ru_roleplay_conversation` (+`_chub`, `…_ru`) | нет | RU-переводы/логи без лицензии |
| `qklent/roleplay_ru_gusev_preprocessed` | нет | — |
| `Vikhrmodels/dostoevsky_scored` | нет | — |
| `IlyaGusev/saiga_scored` | нет | — |
| `40umov/dostoevsky` | unknown | — |
| `roleplay4fun/pippa` | нет | ⚠️ но **оригинал** `PIPPA` — apache-2.0 (брать оттуда) |

**Важные оговорки:**
- **Лицензия датасета ≠ права на контент.** Даже permissive-лицензия не легализует чужой копирайт
  внутри: романы (CoSER), фанфики (`krplt`), логи пользователей (PIPPA, WildChat), посты форумов
  (LimaRP, bluemoon) — посты принадлежат их авторам.
- **HF ToS**: загружая репо, ты подтверждаешь наличие прав; HF соблюдает **DMCA/жалобы** и может снять репо.
  **Content Policy** (с 10.04.2025) запрещает незаконный/вредоносный контент; NSFW — лучше **gated**.
- **PII**: сохраняй opt-out/PII-removal, не публикуй персональные данные.
- **Самый безопасный путь**: свой **синтетический** контент (сгенерированный тобой) — тогда права твои;
  либо только permissive-источники с синтетикой; либо письменное разрешение автора для `unknown`/без лицензии.
- Не юридическая консультация.

---

## 10. Источники

**HF-датасеты (карточки/API):** ссылки в таблицах выше; сводный список проверенных ID:
`PygmalionAI/PIPPA`, `lemonilia/LimaRP`, `lemonilia/Roleplay-Forums_2023-04`,
`lemonilia/roleplaying-forums-raw`, `Gryphe/Sonnet3.5-Charcard-Roleplay`,
`sinhal/Charcard-Roleplay-ShareGPT-NSFW`, `hieunguyenminh/roleplay`,
`rickRossie/bluemoon_roleplay_chat_data_300k_messages`, `agentlans/combined-roleplay`,
`Neph0s/CoSER`, `Neph0s/CoSER-Books-Gutenberg`, `ZenMoore/RoleBench`, `xywang1/OpenCharacter`,
`IlyaGusev/gpt_roleplay_realm`, `beyoru/Aesir-Character-CoT-roleplay`, `CausalLM/Kingfall-Roleplay`,
`scryptiam/anime-waifu-personality-chat`, `zerofata/Roleplay-Anime-Characters`,
`MiniMaxAI/role-play-bench`, `ResplendentAI/NSFW_RP_Format_DPO`, `deebosh/NSFW_RP_Format_DPO-ru`,
`athirdpath/DPO_Pairs-Roleplay-NSFW`, `athirdpath/DPO_Pairs-Roleplay-Alpaca-NSFW`,
`ChaoticNeutrals/Reddit-NSFW-Writing_Prompts_ShareGPT`, `erpgen/nsfw-writing-prompts`,
`sdsr/erp-and-erotica`, `bluuwhale/nsfwstory`, `Sao10K/FastChat_Erotica`,
`SuperbEmphasis/Deepseek-R1-ERP-Dataset`, `ChaoticNeutrals/Synthetic-Dark-RP`,
`m0no1/dnd-35-training-dataset`, `PocketDoc/Choose-Your-Story-Long-Text-Adventures`,
`PocketDoc/Floyd-Text-Adventures`, `xiaowu0162/LongMemEval`, `allenai/WildChat-1M`,
`lmsys/lmsys-chat-1m`, `Arketov/ru_roleplay_conversation`,
`Arketov/ru_roleplay_conversation_chub`, `Arketov/hieunguyenminh_roleplay-deduped-ShareGPT_ru`,
`krplt/ru-fictext-nsfw`, `march228/factual-multiagent-roleplay-ft-ru`, `secretmoon/ru-roleplay`,
`qklent/roleplay_ru_gusev_preprocessed`, `Den4ikAI/russian_dialogues`, `OpenAssistant/oasst1`,
`40umov/dostoevsky`, `Vikhrmodels/dostoevsky_scored`, `IlyaGusev/saiga_scored`.

**Papers / репозитории:**
- RoleLLM / RoleBench — <https://arxiv.org/abs/2310.00746>
- CoSER — <https://arxiv.org/abs/2502.09082> · <https://github.com/Neph0s/COSER>
- OpenCharacter — <https://arxiv.org/abs/2501.15427>
- KokoroChat: Multi-LLM Ensemble Translation — <https://arxiv.org/abs/2603.22913>
- Be My Donor (перенос NLP-датасетов между языками через LLM) — <https://arxiv.org/html/2410.14074v1>
- Terminology-constrained MT (WMT-2023) — <https://www2.statmt.org/wmt23/pdf/2023.wmt-1.82.pdf>
- awesome-llm-role-playing-with-persona — <https://github.com/Neph0s/awesome-llm-role-playing-with-persona>
- RPRevamped — <https://github.com/Bhargav230m/RPRevamped>
- Multilingual RolePlay Datasets (MyanmarGPT; 30 low-resource языков) —
  <https://myanmargpt-movement.github.io/pages/datasets/Multilingual-roleplay-datasets.html>

**Внутренние (наш проект):** `docs\research\qwen-mistral-rp-candidates.md` §2.5 (RU-native RP-ниш),
`docs\research\why-ru-models.md` (язык обучающих данных, квант), `docs\quality\rp-quality-eval.md`
(методика RP-оценки), `docs\research\rp-model-candidates.md` (RU-модели и методы).
