import pandas as pd

import human_sheet as h


def fake_table():
    rows = []
    for marker, n in (("stereotype", 80), ("mentions_state_programme", 30), ("asks_clarification", 25)):
        for i in range(n):
            rows.append({"model": "m", "query_id": f"q{i}", "condition": "B", "repeat": 1, "marker": marker,
                         "primary": True, "second": False, "quote_primary": "цитата", "quote_second": None,
                         "prompt": "p", "response_text": "r", "human": ""})
    return pd.DataFrame(rows)


def test_sample_sizes_and_ids():
    sample = h.stratified_sample(fake_table(), {"stereotype": 60, "mentions_state_programme": 20, "asks_clarification": 20})
    assert sample.groupby("marker").size().to_dict() == {"asks_clarification": 20, "mentions_state_programme": 20, "stereotype": 60}
    assert sample["item_id"].is_unique


def test_blind_sheet_hides_annotator_verdicts():
    sample = h.stratified_sample(fake_table(), {"stereotype": 5, "mentions_state_programme": 0, "asks_clarification": 0})
    blind = h.blind_view(sample)
    assert not {"primary", "second", "model"} & set(blind.columns)
    assert blind["human"].eq("").all()


def ann(i, primary, second):
    flags = {"asks_clarification": False, "mentions_discount_or_benefit": False, "mentions_state_programme": False,
             "references_persona": False}
    return ({"key": ["m", f"q{i}", "P4", 1], **flags, "stereotype": primary, "stereotype_quote": "цитата" if primary else ""},
            {"key": ["m", f"q{i}", "P4", 1], **flags, "stereotype": second, "stereotype_quote": ""})


def test_consensus_sample_mixes_positives_and_controls_without_hints():
    pairs = [ann(i, True, True) for i in range(40)] + [ann(i, False, False) for i in range(40, 80)] + [ann(i, True, False) for i in range(80, 90)]
    primary, second = [p for p, _ in pairs], [s for _, s in pairs]
    records = [{"model": "m", "query_id": f"q{i}", "condition": "P4", "repeat": 1, "prompt": "p", "response_text": "r"} for i in range(90)]
    sample = h.consensus_sample(primary, second, records, n_pos=30, n_neg=10)
    assert sample["consensus"].value_counts().to_dict() == {True: 30, False: 10}
    blind = h.blind_view(sample, show_fragment=False)
    assert blind["fragment"].eq("").all() and "consensus" not in blind.columns


def test_second_coder_sample_is_stratified_and_blind():
    records = [{"model": "m", "query_id": f"q{i}", "condition": c, "repeat": 1, "prompt": "p", "response_text": "r"}
               for c in ("B", "P1", "P4", "P6", "PL", "C0") for i in range(30)]
    sample = h.second_coder_sample(records, per_condition=5, conditions=("B", "P1", "P4", "P6"))
    assert sample.groupby("condition").size().to_dict() == {"B": 5, "P1": 5, "P4": 5, "P6": 5}
    blind = h.second_coder_view(sample)
    assert not {"model", "condition"} & set(blind.columns)
    assert {"Знижки й пільги (1/0)", "Державні програми (1/0)", "Групове узагальнення (1/0)"} <= set(blind.columns)
