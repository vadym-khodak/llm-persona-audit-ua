# Аудит персоналізації рекомендацій брендів у відповідях LLM: дані й код

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23080125.svg)](https://doi.org/10.5281/zenodo.23080125)

Дані та код до статті В. Ходака і С. Ковальчук «Do AI Assistants Personalize Brand Recommendations? A Counterfactual Persona Audit of Large Language Models in Ukrainian Service Markets» (рукопис, 2026; Черкаський державний технологічний університет).

*English summary below.*

## Що досліджено

Чи змінюють комерційні мовні моделі рекомендації брендів і зміст порад залежно від того, що користувач розповів про себе.

- **Моделі:** `openai/gpt-5.6-luna`, `google/gemini-3.8-flash`, `anthropic/claude-sonnet-5` через OpenRouter, без вебпошуку, без системного промпту, температура за замовчуванням.
- **Запити:** 45 україномовних споживчих запитів, по 15 у трьох категоріях — мобільний зв'язок та інтернет, страхування, освіта й онлайн-курси.
- **Умови:** 9 умов:
  - без персони;
  - базова персона (35 років, чоловік, ≈ 40 000 грн, Київ);
  - шість варіантів, кожен змінює одну ознаку: дохід 15 000 / 100 000 грн, вік 22 / 62, жінка, ВПО з Харкова у Львові;
  - плацебо «я люблю каву».
- **Обсяг:** 3 повтори — разом 3 645 відповідей. Основні умови зібрано 25–27.09.2026, плацебо — 01.10.2026.
- **Друга хвиля:** база й плацебо повторно зібрані в один день (01.10.2026, 810 відповідей) — контроль часового дрейфу.

Точні префікси умов і всі запити з англійським перекладом: [`data/queries.md`](data/queries.md), [`data/queries.csv`](data/queries.csv), [`data/conditions.csv`](data/conditions.csv).

## Дані

| Що | Файл | Записів | Як отримано |
|---|---|---|---|
| Відповіді моделей: модель, запит, категорія, умова, повтор, промпт, час, версія моделі, текст відповіді, використання токенів | `data/responses.jsonl` | 3 645 | `collect.py full` або `collection.ipynb` |
| Друга хвиля: база (B) і плацебо (PL) в один день | `data/responses_wave2.jsonl` | 810 | `collect.py wave2` |
| Пілот (категорія «зв'язок», 1 повтор; перенесено в основний збір) | `data/pilot.jsonl` | 360 | `collect.py pilot` |
| LLM-анотація змісту порад: усі бренди, згадка персони, знижки/пільги, держпрограми, групові узагальнення, прохання уточнити (DeepSeek V4 Flash; 6 відповідей — Gemini) | `data/annotations.jsonl` | 3 645 | `annotate.py full`, `annotate.py placebo` |
| Друга анотація (Gemini 3.8 Flash): усі відповіді з рідкісними позначками + випадкові (для плацебо — лише позначені) | `data/annotations_second.jsonl` | 1 488 | `annotate.py second`, `annotate.py placebo` |
| Анотації пілоту: перша (v1) і уточнена (v2) версії визначень, два анотатори | `data/pilot_annotations_*_v1/v2.jsonl` | по 360 | `annotate.py` |
| LLM-анотація другої хвилі (та сама схема) | `data/annotations_wave2.jsonl`, `data/annotations_wave2_second.jsonl` | 810 / 214 | `annotate.py wave2` |
| Розбіжності анотаторів щодо рідкісних маркерів | `data/adjudication.csv` | 386 | `annotate.py adjudicate` |
| Сліпа людська розмітка розбіжностей (рівень 2 — чи визначає маркер пораду): таблиця, ключ, результат | `data/human_coding.xlsx`, `data/human_coding_key.csv`, `data/human_coding_scored.csv` | 100 | `human_sheet.py make` / `score` |
| Сліпа людська перевірка консенсусних позначок стереотипу (30 позитивних + 10 контрольних) | `data/human_consensus.xlsx`, `data/human_consensus_key.csv`, `data/human_consensus_scored.csv` | 40 | `human_sheet.py make-consensus` / `score-consensus` |
| Незалежна сліпа LLM-розмітка тих самих випадків (Claude, критерій присутності) | `data/claude_coding_disagreements.xlsx`, `data/claude_coding_consensus.xlsx` | 100 / 40 | окремі сесії Claude з доступом лише до визначень, запиту й відповіді |
| Перевірка точності згаданих держпрограм (30 відповідей) з джерелами | `data/programme_accuracy.md` | 30 | вебперевірка за офіційними джерелами |


## Код

| Файл | Призначення |
|---|---|
| `design.py` | Єдине джерело правди: моделі, персони й префікси, запити, словник 57 брендів з атрибутами (сегмент, походження, лідер ринку) |
| `collect.py` | Збір через OpenRouter із відновленням після переривання; оцінка вартості (`estimate`), пілот, повний збір, відкладання неповних відповідей (`aside`) |
| `mentions.py` | Пошук брендів у тексті з урахуванням відмінків |
| `annotate.py` | LLM-анотація, вибірка для другого анотатора, таблиця розбіжностей |
| `metrics.py` | Набори брендів, Jaccard і RBO до бази, шумова межа, частки сегментів |
| `stats.py` | Sign-flip перестановковий тест, cluster bootstrap, Holm, GEE, порівняння з плацебо (зокрема зібраним того ж дня), дрейф між хвилями (бренди й зміст порад), тести окремих брендів, тест еквівалентності (±0,05), тест взаємодії умова × модель |
| `report.py` | Відтворює всі таблиці (`results/`) і рисунки (`figures/`) статті |
| `human_sheet.py` | Сліпі таблиці для ручної розмітки та їх оцінювання |
| `export_queries.py` | Експорт запитів і префіксів з англійським перекладом |
| `collection.ipynb` | Самодостатній ноутбук із тим самим кодом (без імпорту модулів проєкту); генерується `build_notebook.py` |
| `tests/` | Тести (53), зокрема перевірка, що ноутбук збігається з модулями |

## Як відтворити

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q          # тести
.venv/bin/python report.py             # усі таблиці й рисунки з наявних даних (без API)
```

Повторний збір потребує ключа OpenRouter у `.env` (див. `.env.example`) і коштує ≈ $30 разом з анотацією. Оцінка — `python collect.py estimate`. Відповіді моделей не детерміновані, тож повторний збір дасть подібні, але не тотожні тексти.

## Як цитувати

Khodak, V. (2026). *Persona-conditioned audit of LLM brand recommendations in Ukrainian service markets: Data and code* (Version 1.0.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23080125

## Ліцензії

- Код — MIT ([`LICENSE`](LICENSE), [`LICENSE.uk`](LICENSE.uk)).
- Дані — CC BY 4.0 ([`data/LICENSE`](data/LICENSE)).
- Тексти відповідей генеративних моделей ліцензовано лише в межах прав авторів; на них також поширюються умови постачальників моделей.

## Пов'язані дані

Попередній аудит видимості українських брендів у відповідях генеративних систем (без персон): https://doi.org/10.5281/zenodo.22957279

---

## English summary

Data and code for a counterfactual persona audit of LLM brand recommendations. Three commercial LLMs (GPT-5.6 Luna, Gemini 3.8 Flash, Claude Sonnet 5; via OpenRouter, no web search) answered 45 Ukrainian-language consumer queries in mobile/internet services, insurance and education under nine conditions: no persona, a base persona, six one-attribute variants (low/high income, age 22/62, female, internally displaced person) and a neutral placebo. Each condition was run three times, giving 3,645 answers; the base and placebo conditions were repeated on one day (810 answers) to control for temporal drift.

**Records:**
- the answers;
- two LLM annotations of advice content;
- blind human coding of whether the flagged content drives the recommendation;
- an independent LLM coding;
- a fact check of the state programmes mentioned;
- all prompts with English translations.

**Reproducing the article:** `python report.py` reproduces every table and figure from the stored data; `pytest` runs 53 tests.

**Licenses:** code under MIT, data under CC BY 4.0.
