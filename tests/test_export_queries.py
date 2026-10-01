import csv

import design as d
import export_queries as e


def test_every_query_has_english_translation():
    assert set(e.QUERIES_EN) == {q["query_id"] for q in d.all_queries()}


def test_export_writes_queries_and_conditions(tmp_path):
    e.export(tmp_path)
    with (tmp_path / "queries.csv").open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 45 and rows[0]["text_en"]
    with (tmp_path / "conditions.csv").open(encoding="utf-8-sig") as f:
        conditions = list(csv.DictReader(f))
    assert [c["condition"] for c in conditions] == list(d.CONDITIONS)
    assert all(c["prefix_uk"] and c["prefix_en"] for c in conditions)
