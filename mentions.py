"""Пошук згадок брендів у тексті відповіді (логіка з audit.find_mentions статті 1)."""

import re

from design import CATEGORIES


def patterns_for(category):
    return CATEGORIES[category]["brands"]


def find_mentions(text, patterns):
    """Бренди в порядку першої появи; rank 1 — згаданий першим."""
    hits = []
    for brand, pattern in patterns.items():
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            hits.append((m.start(), brand))
    hits.sort()
    length = max(len(text), 1)
    return [
        {"brand": brand, "rank": rank, "relative_pos": round(pos / length, 4)}
        for rank, (pos, brand) in enumerate(hits, start=1)
    ]
