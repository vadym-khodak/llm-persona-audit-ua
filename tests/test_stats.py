import numpy as np
import pandas as pd

import stats as s


def test_sign_flip_detects_shift_and_null():
    rng = np.random.default_rng(1)
    _, p_shift = s.sign_flip_test(rng.normal(0.3, 0.1, 45))
    _, p_null = s.sign_flip_test(rng.normal(0.0, 0.1, 45))
    assert p_shift < 0.001
    assert p_null > 0.05


def test_sign_flip_ignores_nan():
    mean, p = s.sign_flip_test([0.2, np.nan, 0.3, 0.25])
    assert abs(mean - 0.25) < 1e-12 and 0 < p <= 1


def fake_shift():
    rows = []
    for model in ("m1", "m2"):
        for q in range(45):
            for cond in ("P1", "P5"):
                delta = 0.3 if cond == "P1" else 0.0
                rows.append({"model": model, "query_id": f"tel-{q:02d}", "condition": cond,
                             "delta_jaccard": delta + (0.05 if q % 2 else -0.05)})
    return pd.DataFrame(rows)


def test_h1_table_holm_and_pooled():
    table = s.h1_table(fake_shift())
    p1 = table[(table.model == "pooled") & (table.condition == "P1")].iloc[0]
    p5 = table[(table.model == "pooled") & (table.condition == "P5")].iloc[0]
    assert p1.p_holm < 0.01 and p5.p_holm > 0.05
    assert (table.p_holm >= table.p).all()
    assert p1.ci_low < p1.mean_delta < p1.ci_high


def test_share_gee_recovers_effect():
    rng = np.random.default_rng(0)
    rows = []
    for q in range(40):
        for cond, shift in (("B", 0.0), ("P2", 0.2)):
            for model in ("m1", "m2"):
                for r in range(3):
                    rows.append({"query_id": f"q{q}", "condition": cond, "model": model,
                                 "share_premium": 0.3 + shift + rng.normal(0, 0.05)})
    out = s.share_gee(pd.DataFrame(rows), "share_premium")
    p2 = out[out.condition == "P2"].iloc[0]
    assert 0.15 < p2.coef < 0.25 and p2.p < 0.001

def test_placebo_table_attribute_beyond_placebo():
    rows = []
    for model in ("m1", "m2"):
        for q in range(45):
            jitter = 0.02 if q % 2 else -0.02
            rows.append({"model": model, "query_id": f"tel-{q:02d}", "condition": "PL", "jaccard_to_base": 0.70 + jitter})
            rows.append({"model": model, "query_id": f"tel-{q:02d}", "condition": "P1", "jaccard_to_base": 0.60 + jitter})
            rows.append({"model": model, "query_id": f"tel-{q:02d}", "condition": "P5", "jaccard_to_base": 0.70 - jitter})
    table = s.placebo_table(pd.DataFrame(rows)).set_index("condition")
    assert table.loc["P1", "mean_diff"] > 0.09 and table.loc["P1", "p_holm"] < 0.01
    assert table.loc["P5", "p_holm"] > 0.05
    assert "PL" not in table.index


def test_equivalence_bounds():
    rng = np.random.default_rng(3)
    df = pd.DataFrame({"query_id": [f"q{i}" for i in range(45)], "diff": rng.normal(0.0, 0.01, 45)})
    eq = s.equivalence(df, "diff", sesoi=0.05)
    assert eq["equivalent"] and eq["ci90_low"] > -0.05 and eq["ci90_high"] < 0.05
    df["diff"] = rng.normal(0.06, 0.03, 45)
    assert not s.equivalence(df, "diff", sesoi=0.05)["equivalent"]


def test_placebo_table_per_model_has_model_column():
    rows = []
    for model in ("m1", "m2"):
        for q in range(10):
            rows.append({"model": model, "query_id": f"q{q}", "condition": "PL", "jaccard_to_base": 0.7})
            rows.append({"model": model, "query_id": f"q{q}", "condition": "P1", "jaccard_to_base": 0.6 + 0.01 * (q % 2)})
    table = s.placebo_table(pd.DataFrame(rows), by_model=True)
    assert set(table["model"]) == {"m1", "m2"} and {"equivalent", "ci90_low"} <= set(table.columns)


def test_interaction_test_detects_model_specific_effect():
    rng = np.random.default_rng(0)
    rows = []
    for q in range(45):
        for model, eff in (("m1", 0.1), ("m2", 0.0)):
            for cond in ("P1", "P5"):
                rows.append({"model": model, "query_id": f"q{q}", "condition": cond,
                             "delta_jaccard": (eff if cond == "P1" else 0) + rng.normal(0, 0.02)})
    p = s.interaction_test(pd.DataFrame(rows))
    assert p < 0.001


def test_share_gee_reference_c0():
    rng = np.random.default_rng(0)
    rows = [{"query_id": f"q{q}", "condition": cond, "model": "m", "x": base + rng.normal(0, 0.01)}
            for q in range(30) for cond, base in (("C0", 0.2), ("B", 0.1), ("P1", 0.2))]
    out = s.share_gee(pd.DataFrame(rows), "x", reference="C0").set_index("condition")
    assert abs(out.loc["P1", "coef"]) < 0.02 and out.loc["B", "coef"] < -0.08


def test_sameday_placebo_contrast_uses_deltas():
    main = pd.DataFrame([{"model": "m", "query_id": f"q{q}", "condition": c, "delta_jaccard": d}
                         for q in range(30) for c, d in (("P1", 0.10 + 0.01 * (q % 2)), ("P5", 0.02))])
    wave2 = pd.DataFrame([{"model": "m", "query_id": f"q{q}", "condition": "PL", "delta_jaccard": 0.02}
                          for q in range(30)])
    table = s.sameday_placebo_table(main, wave2).set_index("condition")
    assert table.loc["P1", "mean_diff"] > 0.08 and table.loc["P1", "p_holm"] < 0.01
    assert abs(table.loc["P5", "mean_diff"]) < 1e-9


def test_drift_table_detects_change_between_waves():
    key = lambda q, r: ("m", f"q{q}", "B", r)
    main = {key(q, r): ["a", "b", "c"] for q in range(20) for r in (1, 2, 3)}
    wave2 = {key(q, r): ["a", "x", "y"] for q in range(20) for r in (1, 2, 3)}
    row = s.drift_table(main, wave2).iloc[0]
    assert row["mean_drift"] > 0.5 and row["p"] < 0.001


def test_brand_mention_contrasts_binary_gee():
    rng = np.random.default_rng(0)
    rows = []
    for q in range(30):
        for cond, p in (("B", 0.5), ("P1", 0.8), ("P2", 0.2)):
            for model in ("m1", "m2"):
                rows.append({"query_id": f"edu-{q}", "condition": cond, "model": model, "brand": "X",
                             "mentioned": float(rng.random() < p)})
    out = s.brand_mention_contrasts(pd.DataFrame(rows), brands=["X"], conditions=["P1", "P2"]).set_index("condition")
    assert out.loc["P1", "coef"] > 0.15 and out.loc["P2", "coef"] < -0.15 and (out.p_holm < 0.05).all()
