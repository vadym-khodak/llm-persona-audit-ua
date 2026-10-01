import report as rp


def test_marker_table_shares_by_condition():
    records = [{"model": "m", "query_id": "tel-01", "condition": c, "repeat": 1} for c in ("B", "P6")]
    ann = [
        {"key": ["m", "tel-01", "B", 1], "asks_clarification": False, "mentions_discount_or_benefit": False,
         "mentions_state_programme": False, "references_persona": False, "stereotype": False},
        {"key": ["m", "tel-01", "P6", 1], "asks_clarification": False, "mentions_discount_or_benefit": True,
         "mentions_state_programme": True, "references_persona": True, "stereotype": False},
    ]
    table = rp.marker_table(ann, records)
    assert table.loc["P6", "mentions_state_programme"] == 1.0
    assert table.loc["B", "mentions_state_programme"] == 0.0

def flags(key, **kw):
    base = {"asks_clarification": False, "mentions_discount_or_benefit": False, "mentions_state_programme": False,
            "references_persona": False, "stereotype": False}
    return {"key": key, **base, **kw}


def test_final_markers_consensus_for_rare_primary_for_common():
    k1, k2, k3 = ["m", "q", "B", 1], ["m", "q", "B", 2], ["m", "q", "B", 3]
    primary = [flags(k1, stereotype=True, mentions_discount_or_benefit=True),
               flags(k2, stereotype=True), flags(k3)]
    second = [flags(k1, stereotype=False, mentions_discount_or_benefit=False), flags(k2, stereotype=True)]
    final = {tuple(x["key"]): x for x in rp.final_markers(primary, second)}
    assert final[tuple(k1)]["stereotype"] is False
    assert final[tuple(k1)]["mentions_discount_or_benefit"] is True
    assert final[tuple(k2)]["stereotype"] is True
    assert final[tuple(k3)]["stereotype"] is False
    assert final[tuple(k1)]["stereotype_upper"] is True
