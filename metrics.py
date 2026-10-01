"""Показники зсуву рекомендацій під впливом персони."""

from collections import defaultdict
from itertools import combinations, product

import numpy as np
import pandas as pd

from collect import task_key
from design import BRAND_ATTRS
from mentions import find_mentions, patterns_for

CATEGORY_OF_PREFIX = {"tel": "telecom", "ins": "insurance", "edu": "education"}


def jaccard(a, b):
    a, b = set(a), set(b)
    if not a and not b:
        return float("nan")
    return len(a & b) / len(a | b)


def rbo_ext(s, l, p=0.9):
    """Екстрапольований RBO (Webber et al., 2010, eq. 32) для списків різної довжини."""
    if not s and not l:
        return float("nan")
    if not s or not l:
        return 0.0
    if len(s) > len(l):
        s, l = l, s
    k_s, k_l = len(s), len(l)
    overlap = {}
    total = 0.0
    for depth in range(1, k_l + 1):
        overlap[depth] = len(set(s[:depth]) & set(l[:depth]))
        total += overlap[depth] / depth * p**depth
    tail = sum(overlap[k_s] * (depth - k_s) / (k_s * depth) * p**depth for depth in range(k_s + 1, k_l + 1))
    value = (1 - p) / p * (total + tail) + ((overlap[k_l] - overlap[k_s]) / k_l + overlap[k_s] / k_s) * p**k_l
    return min(1.0, value)


def brand_lists(records):
    return {
        task_key(r): [hit["brand"] for hit in find_mentions(r["response_text"], patterns_for(r["category"]))]
        for r in records
    }


def _mean(values):
    values = [v for v in values if not np.isnan(v)]
    return float(np.mean(values)) if values else float("nan")


def shift_table(lists):
    cells = defaultdict(dict)
    for (model, query_id, condition, repeat), brands in lists.items():
        cells[(model, query_id, condition)][repeat] = brands
    rows = []
    for (model, query_id, condition), reps in cells.items():
        if condition == "B":
            continue
        base = cells.get((model, query_id, "B"), {})
        pairs_base = list(combinations(base.values(), 2))
        pairs_cross = list(product(reps.values(), base.values()))
        row = {
            "model": model,
            "query_id": query_id,
            "category": CATEGORY_OF_PREFIX[query_id.split("-")[0]],
            "condition": condition,
            "jaccard_to_base": _mean([jaccard(a, b) for a, b in pairs_cross]),
            "rbo_to_base": _mean([rbo_ext(a, b) for a, b in pairs_cross]),
            "noise_jaccard": _mean([jaccard(a, b) for a, b in pairs_base]),
            "noise_rbo": _mean([rbo_ext(a, b) for a, b in pairs_base]),
        }
        row["delta_jaccard"] = row["noise_jaccard"] - row["jaccard_to_base"]
        row["delta_rbo"] = row["noise_rbo"] - row["rbo_to_base"]
        rows.append(row)
    return pd.DataFrame(rows)


def _share(brands, predicate):
    return sum(predicate(BRAND_ATTRS[b]) for b in brands) / len(brands) if brands else float("nan")


def response_frame(records, lists):
    rows = []
    for r in records:
        brands = lists[task_key(r)]
        rows.append({
            "model": r["model"], "query_id": r["query_id"], "category": r["category"],
            "condition": r["condition"], "repeat": r["repeat"], "n_brands": len(brands),
            "no_brands": not brands,
            "share_budget": _share(brands, lambda a: a["tier"] == "budget"),
            "share_premium": _share(brands, lambda a: a["tier"] == "premium"),
            "share_free": _share(brands, lambda a: a["tier"] == "free"),
            "share_global": _share(brands, lambda a: a["origin"] == "global"),
            "share_ru": _share(brands, lambda a: a["origin"] == "ru"),
            "share_incumbent": _share(brands, lambda a: a["incumbent"]),
        })
    return pd.DataFrame(rows)


def check_served_models(records):
    served = defaultdict(set)
    for r in records:
        served[r["model"]].add(r.get("served_model"))
    return dict(served)
