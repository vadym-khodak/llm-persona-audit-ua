"""Збирає самодостатній collection.ipynb з design.py, mentions.py, collect.py та annotate.py.

Ноутбук не імпортує модулі проєкту: код модулів копіюється в клітинки. Після змін у модулях
перезапусти цей скрипт; tests/test_notebook.py перевіряє, що ноутбук актуальний.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
LOCAL_IMPORT = re.compile(r"^(import design as d|from (design|collect|mentions) import .*)\n", flags=re.M)


def module_source(name):
    text = (ROOT / f"{name}.py").read_text(encoding="utf-8")
    text = LOCAL_IMPORT.sub("", text)
    text = text.split("\ndef main(", 1)[0].rstrip() + "\n"
    text = re.sub(r"\bd\.", "", text)
    return text.replace('DATA = Path(__file__).parent / "data"', 'DATA = Path("data")')


def lines(text):
    return text.strip("\n").splitlines(keepends=True)


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": lines(text)}


def code(text, library=False):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"tags": ["library"]} if library else {},
        "outputs": [],
        "source": lines(text),
    }


INTRO = """
# Persona-conditioned audit of LLM brand recommendations — збір даних

Ноутбук повністю самодостатній: тут увесь код дизайну, збору через OpenRouter і анотації.
Ті самі кроки є у скриптах `collect.py` і `annotate.py`; ноутбук згенеровано з них скриптом `build_notebook.py`.

**Як запустити:** ключ `OPENROUTER_API_KEY` у файлі `.env` (у цій або батьківській папці); клітинки виконувати згори донизу.
Платні кроки захищено прапорцем `RUN_PAID = False` — змініть на `True`, лише коли готові платити.
"""

SETUP = """
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))
RUN_PAID = False
"""

OVERVIEW_DESIGN = """
import pandas as pd

pd.set_option("display.max_colwidth", 200)
display(pd.DataFrame({"condition": list(CONDITIONS), "prefix": [persona_prefix(p) for p in CONDITIONS.values()]}))
queries = all_queries()
print(len(queries), "запитів;", len(MODELS), "моделі;", len(CONDITIONS), "умов;", REPEATS, "повтори")
display(pd.DataFrame(queries).groupby(["category", "intent"]).size().unstack(fill_value=0))
"""

ESTIMATE = """
prices = fetch_catalog_prices()
for stage in ("pilot", "full"):
    table = estimate_cost(tasks_for(stage), prices)
    display(table)
    print(stage, "разом, $:", round(table["cost_usd"].sum(), 2))
"""

COLLECT = """
STAGE = "full"  # або "pilot"
target = DATA / ("pilot.jsonl" if STAGE == "pilot" else "responses.jsonl")
if RUN_PAID:
    for attempt in range(3):
        failed = run_collection(tasks_for(STAGE), target)
        moved = set_aside_incomplete(target)
        print(f"Спроба {attempt + 1}: помилок {len(failed)}, відкладено неповних {moved}")
        if not failed and not moved:
            break
else:
    print("RUN_PAID = False — збір пропущено")
"""

CHECK = """
records = load_jsonl(target)
frame = pd.DataFrame([{k: v for k, v in r.items() if k != "prompt"} for r in records])
print("Відповідей:", len(records), "з", len(tasks_for(STAGE)), "| неповних:", sum(is_incomplete(r) for r in records))
print("Вартість збору, $:", round(sum((r.get("usage") or {}).get("cost") or 0 for r in records), 2))
display(frame.groupby("model")["served_model"].unique())
display(frame.pivot_table(index="model", columns="condition", values="repeat", aggfunc="size", fill_value=0))
"""

ANNOTATE = """
annotations_path = DATA / ("pilot_annotations.jsonl" if STAGE == "pilot" else "annotations.jsonl")
second_path = DATA / ("pilot_annotations_second.jsonl" if STAGE == "pilot" else "annotations_second.jsonl")
if RUN_PAID:
    for attempt in range(3):
        failed = run_annotation(records, annotations_path, PRIMARY)
        print(f"{PRIMARY}, спроба {attempt + 1}: помилок {len(failed)}")
        if not failed:
            break
    sample = second_check_sample(records, load_jsonl(annotations_path))
    for attempt in range(3):
        failed = run_annotation(sample, second_path, SECOND)
        print(f"{SECOND} на {len(sample)} відповідях, спроба {attempt + 1}: помилок {len(failed)}")
        if not failed:
            break
else:
    print("RUN_PAID = False — анотацію пропущено")
"""

ADJUDICATE = """
if annotations_path.exists() and second_path.exists():
    table = adjudication_table(load_jsonl(annotations_path), load_jsonl(second_path), records)
    table.to_csv(DATA / "adjudication.csv", index=False, encoding="utf-8-sig")
    print(len(table), "розбіжностей для ручного рішення → data/adjudication.csv")
    display(table.groupby(["marker", "condition"]).size().unstack(fill_value=0))
"""

MENTIONS = """
rows = []
for r in records:
    for hit in find_mentions(r["response_text"], patterns_for(r["category"])):
        rows.append({"model": r["model"], "category": r["category"], "condition": r["condition"], **hit})
mentions = pd.DataFrame(rows)
per_response = mentions.groupby(["model", "condition"]).size() / frame.groupby(["model", "condition"]).size()
display(per_response.unstack().round(2))
display(mentions.groupby(["category", "brand"]).size().sort_values(ascending=False).groupby(level=0).head(8))
"""


def render():
    cells = [
        md(INTRO),
        code(SETUP),
        md("## 1. Дизайн: персони, запити, бренди\n\nЄдине джерело правди — `design.py`; нижче його точна копія."),
        code(module_source("design"), library=True),
        code(OVERVIEW_DESIGN),
        md("## 2. Пошук згадок брендів"),
        code(module_source("mentions"), library=True),
        md("## 3. Збір відповідей через OpenRouter"),
        code(module_source("collect"), library=True),
        md("### 3.1. Оцінка вартості (безкоштовно)"),
        code(ESTIMATE),
        md("### 3.2. Збір (платно)\n\nЗапуск можна переривати: повторний добирає лише відсутні відповіді."),
        code(COLLECT),
        md("### 3.3. Контроль повноти"),
        code(CHECK),
        md("## 4. LLM-анотація (платно)\n\nОсновний анотатор (DeepSeek, не входить до моделей аудиту) — усі відповіді; другий (Gemini) — усі, де основний позначив рідкісний маркер, плюс 300 випадкових."),
        code(module_source("annotate"), library=True),
        code(ANNOTATE),
        md("### 4.1. Розбіжності щодо рідкісних маркерів\n\nСтереотип, держпрограми, прохання уточнити: спірні випадки розмічає автор у колонці `human` (1/0)."),
        code(ADJUDICATE),
        md("## 5. Перший погляд на згадки брендів\n\nСередня кількість відстежуваних брендів у відповіді та топ брендів за категорією. Повний аналіз — `report.py`."),
        code(MENTIONS),
    ]
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }


def main():
    path = ROOT / "collection.ipynb"
    path.write_text(json.dumps(render(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("Записано", path.name)


if __name__ == "__main__":
    main()
