# data — данные для разбора ответов

| Файл | О чём |
| --- | --- |
| [blacklist_split_untied.json](blacklist_split_untied.json) | Чёрный список токенов для Split-Untied-31B (иноалфавит и т.п.), собран из словаря GGUF скриптом [gguf_vocab.py](../gguf_vocab.py). Вход для `logit_bias` и разбора «мусора» в ответах. |

Список собран из словаря конкретного GGUF и нужен скриптам, которые чистят и анализируют ответы
(см. [gguf_vocab.py](../gguf_vocab.py) и разбор «мусора» в [rp_quality.py](../rp_quality.py)).
