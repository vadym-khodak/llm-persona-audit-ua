"""Діагностика пілоту: повнота відповідей, мова, покриття словника, частка відповідей без брендів, вартість."""

from collections import Counter

import pandas as pd

from annotate import unmatched_brands
from collect import DATA, is_incomplete, load_jsonl
from metrics import brand_lists, check_served_models, response_frame

records = load_jsonl(DATA / "pilot.jsonl")
annotations = load_jsonl(DATA / "pilot_annotations.jsonl")
lists = brand_lists(records)
frame = response_frame(records, lists)

print("Відповідей:", len(records), "неповних:", sum(is_incomplete(r) for r in records))
print("Вартість, $:", round(sum((r.get("usage") or {}).get("cost") or 0 for r in records), 2))
print("Версії моделей:", check_served_models(records))
print("Без брендів за моделлю й умовою:\n", frame.pivot_table(index="model", columns="condition", values="no_brands", aggfunc="mean").round(2))
print("Середня кількість брендів:\n", frame.pivot_table(index="model", columns="condition", values="n_brands").round(1))
print("Бренди поза словником (топ-30):\n", unmatched_brands(annotations, records).head(30))
print("Мови відповідей:", Counter("uk" if any(ch in r["response_text"] for ch in "іїєґ") else "other" for r in records))