import math

import metrics as m


def test_jaccard_empty_rule():
    assert math.isnan(m.jaccard([], []))
    assert m.jaccard(["a"], []) == 0.0
    assert m.jaccard(["a", "b"], ["b", "c"]) == 1 / 3


def test_rbo_bounds_and_order_sensitivity():
    assert abs(m.rbo_ext(["a", "b", "c"], ["a", "b", "c"]) - 1.0) < 1e-12
    assert m.rbo_ext(["a", "b"], ["c", "d"]) == 0.0
    assert math.isnan(m.rbo_ext([], []))
    same_top = m.rbo_ext(["a", "b", "c"], ["a", "c", "b"])
    swapped_top = m.rbo_ext(["a", "b", "c"], ["b", "a", "c"])
    assert 0 < swapped_top < same_top < 1
    assert abs(m.rbo_ext(["a", "b"], ["a", "b", "c"]) - m.rbo_ext(["a", "b", "c"], ["a", "b"])) < 1e-12


def lists_fixture():
    key = lambda cond, r: ("m", "tel-01", cond, r)
    return {
        key("B", 1): ["K", "V"], key("B", 2): ["K", "V"], key("B", 3): ["K", "L"],
        key("P1", 1): ["L", "U"], key("P1", 2): ["L", "U"], key("P1", 3): ["L", "U"],
    }


def test_shift_table_delta_sign():
    table = m.shift_table(lists_fixture())
    row = table[table["condition"] == "P1"].iloc[0]
    assert row["noise_jaccard"] > row["jaccard_to_base"]
    assert row["delta_jaccard"] > 0
    assert row["category"] == "telecom"


def test_empty_answers_excluded_not_identical():
    key = lambda cond, r: ("m", "tel-01", cond, r)
    lists = {key("B", r): [] for r in (1, 2, 3)} | {key("P5", r): [] for r in (1, 2, 3)}
    row = m.shift_table(lists).iloc[0]
    assert math.isnan(row["jaccard_to_base"]) and math.isnan(row["noise_jaccard"])


def test_served_model_drift_detected():
    recs = [{"model": "a", "served_model": "a-0801"}, {"model": "a", "served_model": "a-0915"}]
    assert m.check_served_models(recs) == {"a": {"a-0801", "a-0915"}}