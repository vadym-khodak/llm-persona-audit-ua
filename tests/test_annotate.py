import annotate as a


def test_unmatched_brands_counts_only_unknown():
    records = [{"model": "m", "query_id": "tel-01", "condition": "B", "repeat": 1, "category": "telecom"}]
    annotations = [{"key": ["m", "tel-01", "B", 1], "brands": ["Київстар", "Інтертелеком", "Інтертелеком"]}]
    assert a.unmatched_brands(annotations, records).to_dict() == {"Інтертелеком": 1}


def test_cohen_kappa():
    assert a.cohen_kappa([1, 1, 0, 0], [1, 1, 0, 0]) == 1.0
    assert abs(a.cohen_kappa([1, 0, 1, 0], [1, 1, 0, 0])) < 1e-12

def rec(i):
    return {"model": "m", "query_id": f"tel-{i:02d}", "condition": "B", "repeat": 1, "category": "telecom",
            "prompt": "p", "response_text": f"text {i}"}


def ann(i, **flags):
    base = {m: False for m in a.MARKERS}
    return {"key": ["m", f"tel-{i:02d}", "B", 1], "brands": [], "stereotype_quote": "", **base, **flags}


def test_second_check_sample_takes_all_flagged_plus_random():
    records = [rec(i) for i in range(50)]
    primary = [ann(i, stereotype=(i in (3, 7)), mentions_state_programme=(i == 9)) for i in range(50)]
    sample = a.second_check_sample(records, primary, n_random=10, seed=1)
    keys = {r["query_id"] for r in sample}
    assert {"tel-03", "tel-07", "tel-09"} <= keys
    assert 10 <= len(sample) == len(keys) <= 13


def test_validate_rejects_missing_marker():
    bad = {k: v for k, v in ann(1).items() if k != "stereotype"}
    try:
        a.validate(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("missing marker accepted")
    a.validate(ann(1))


def test_adjudication_table_lists_rare_disagreements_only():
    records = [rec(1), rec(2)]
    primary = [ann(1, stereotype=True, mentions_discount_or_benefit=True), ann(2)]
    second = [ann(1, stereotype=False), ann(2)]
    table = a.adjudication_table(primary, second, records)
    assert list(table["marker"]) == ["stereotype"]
    assert table.iloc[0]["query_id"] == "tel-01" and table.iloc[0]["human"] == ""


def test_second_check_random_part_does_not_depend_on_flags():
    records = [rec(i) for i in range(50)]
    before = a.second_check_sample(records, [ann(i) for i in range(50)], n_random=10, seed=1)
    after = a.second_check_sample(records, [ann(i, stereotype=(i == 3)) for i in range(50)], n_random=10, seed=1)
    assert {r["query_id"] for r in before} <= {r["query_id"] for r in after}
