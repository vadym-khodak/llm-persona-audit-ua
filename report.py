"""Таблиці й рисунки для статті з повного набору даних."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.stats.multitest import multipletests

from annotate import MARKERS, RARE_MARKERS, cohen_kappa
from collect import DATA, load_jsonl, task_key
from metrics import brand_lists, response_frame, shift_table
from stats import drift_table, focal_contrasts, h1_table, interaction_test, placebo_table, sameday_placebo_table, share_gee

ROOT = Path(__file__).parent
RESULTS, FIGURES = ROOT / "results", ROOT / "figures"
ORDER = ["C0", "P1", "P2", "P3", "P4", "P5", "P6", "PL"]
LABELS = {"C0": "No persona", "P1": "Low income", "P2": "High income", "P3": "Age 22",
          "P4": "Age 62", "P5": "Female", "P6": "IDP", "PL": "Placebo"}


def marker_table(annotations, records):
    condition = {task_key(r): r["condition"] for r in records}
    df = pd.DataFrame([{"condition": condition[tuple(a["key"])], **{m: bool(a[m]) for m in MARKERS}} for a in annotations])
    return df.groupby("condition")[MARKERS].mean()


def final_markers(primary, second):
    """Рідкісні маркери — лише за згоди обох анотаторів (людська перевірка показала хибні позначки основного);
    поширені маркери — за основним анотатором. Позначка основного зберігається як верхня межа (<marker>_upper)."""
    checked = {tuple(x["key"]): x for x in second}
    final = []
    for a in primary:
        row = {"key": a["key"], **{m: bool(a[m]) for m in MARKERS}}
        other = checked.get(tuple(a["key"]))
        for m in RARE_MARKERS:
            row[f"{m}_upper"] = bool(a[m])
            row[m] = bool(a[m]) and (other is None and a.get("annotator") == "google/gemini-3.8-flash" or bool(other and other[m]))
        final.append(row)
    return final


def marker_effects(final, responses, reference="B"):
    keyed = pd.DataFrame([{"model": f["key"][0], "query_id": f["key"][1], "condition": f["key"][2], "repeat": f["key"][3],
                           **{m: float(f[m]) for m in MARKERS}} for f in final])
    data = responses[["model", "query_id", "condition", "repeat"]].merge(keyed, on=["model", "query_id", "condition", "repeat"])
    table = pd.concat([share_gee(data, m, reference=reference).assign(marker=m) for m in MARKERS], ignore_index=True)
    table["p_holm"] = multipletests(table["p"], method="holm")[1]
    return table


def agreement(primary, second):
    by_key = {tuple(a["key"]): a for a in primary}
    pairs = [(by_key[tuple(b["key"])], b) for b in second if tuple(b["key"]) in by_key]
    return {m: cohen_kappa([p[m] for p, _ in pairs], [s[m] for _, s in pairs]) for m in MARKERS}


def plot_shift(h1):
    fig, ax = plt.subplots(figsize=(7, 3.5))
    data = h1[h1.condition.isin(ORDER)]
    models = sorted(data.model.unique())
    width = 0.8 / len(models)
    for i, model in enumerate(models):
        g = data[data.model == model].set_index("condition").reindex(ORDER).dropna(subset=["mean_delta"])
        x = [ORDER.index(c) + i * width for c in g.index]
        ax.errorbar(x, g.mean_delta, yerr=[g.mean_delta - g.ci_low, g.ci_high - g.mean_delta],
                    fmt="o", capsize=3, label=model.split("/")[-1])
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_xticks([k + 0.4 - width / 2 for k in range(len(ORDER))], [LABELS[c] for c in ORDER], rotation=20)
    ax.set_ylabel("Δ Jaccard (noise − persona vs base)")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig1_shift_by_condition.png", dpi=300)


def plot_shares(responses):
    cols = ["share_budget", "share_premium", "share_incumbent"]
    means = responses[responses.condition != "C0"].groupby("condition")[cols].mean().reindex(["B", *ORDER[1:]])
    ax = means.plot.bar(figsize=(7, 3.5), rot=20)
    ax.set_xticklabels(["Base", *[LABELS[c] for c in ORDER[1:]]])
    ax.set_ylabel("Mean share of mentioned brands")
    ax.figure.tight_layout()
    ax.figure.savefig(FIGURES / "fig2_segment_shares.png", dpi=300)


def plot_markers(markers):
    cols = {"mentions_discount_or_benefit": "Discounts / benefits", "mentions_state_programme": "State programmes",
            "stereotype": "Group generalisation"}
    order = ["B", *[c for c in ORDER if c != "PL" and c in markers.index]]
    data = markers.reindex(order)[list(cols)].rename(columns=cols) * 100
    ax = data.plot.bar(figsize=(7, 3.5), rot=20, width=0.8)
    ax.set_xticklabels(["Base", *[LABELS[c] for c in order[1:]]])
    ax.set_ylabel("% of responses")
    ax.legend(frameon=False, fontsize=8)
    ax.figure.tight_layout()
    ax.figure.savefig(FIGURES / "fig3_content_markers.png", dpi=300)


def main():
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    records = load_jsonl(DATA / "responses.jsonl")
    lists = brand_lists(records)
    responses = response_frame(records, lists)
    shift = shift_table(lists)

    responses.pivot_table(index="model", columns="condition", values="no_brands", aggfunc=["size", "mean"]).to_csv(RESULTS / "table1_sample.csv")
    h1 = h1_table(shift, "delta_jaccard")
    pd.concat([h1.assign(metric="jaccard"), h1_table(shift, "delta_rbo").assign(metric="rbo")]).to_csv(RESULTS / "table2_h1.csv", index=False)
    focal_contrasts(responses).to_csv(RESULTS / "table3_focal.csv", index=False)
    if (shift["condition"] == "PL").any():
        pd.concat([placebo_table(shift), placebo_table(shift, by_model=True)]).to_csv(RESULTS / "table7_placebo.csv", index=False)
    pd.Series({"p_interaction_condition_x_model": interaction_test(shift)}).to_csv(RESULTS / "table8_h6_interaction.csv")
    responses.pivot_table(index="condition", columns="model", values="no_brands", aggfunc="mean").to_csv(RESULTS / "table9_no_brands.csv")
    primary = load_jsonl(DATA / "annotations.jsonl")
    second = load_jsonl(DATA / "annotations_second.jsonl")
    final = final_markers(primary, second)
    markers = marker_table(final, records)
    upper = marker_table([{**f, **{m: f[f"{m}_upper"] for m in RARE_MARKERS}} for f in final], records)
    markers = markers.join(upper[RARE_MARKERS].add_suffix("_upper"))
    markers.loc["kappa"] = agreement(primary, second)
    markers.to_csv(RESULTS / "table4_markers.csv")
    pd.concat([marker_effects(final, responses).assign(reference="B"),
               marker_effects(final, responses, reference="C0").assign(reference="C0")]).to_csv(RESULTS / "table5_marker_effects.csv", index=False)
    if any(f["key"][2] == "PL" for f in final):
        marker_effects(final, responses, reference="PL").to_csv(RESULTS / "table12_markers_vs_placebo.csv", index=False)
    wave2_path = DATA / "responses_wave2.jsonl"
    if wave2_path.exists():
        lists_w2 = brand_lists(load_jsonl(wave2_path))
        shift_w2 = shift_table(lists_w2)
        pd.concat([sameday_placebo_table(shift, shift_w2).assign(model="pooled"),
                   *[sameday_placebo_table(shift[shift.model == m], shift_w2[shift_w2.model == m]).assign(model=m)
                     for m in sorted(shift.model.unique())]]).to_csv(RESULTS / "table10_sameday_placebo.csv", index=False)
        h1_table(shift_w2).to_csv(RESULTS / "table11_wave2_placebo_delta.csv", index=False)
        drift_table(lists, lists_w2).to_csv(RESULTS / "table13_drift.csv", index=False)
    cols = ["n_brands", "share_budget", "share_premium", "share_free", "share_global", "share_ru", "share_incumbent"]
    responses.groupby("condition")[cols].mean().reindex(["C0", "B", *ORDER[1:]]).to_csv(RESULTS / "table6_shares_by_condition.csv")
    plot_shift(h1)
    plot_shares(responses)
    plot_markers(markers.drop(index="kappa"))
    print("Готово:", sorted(p.name for p in RESULTS.iterdir()), sorted(p.name for p in FIGURES.iterdir()))


if __name__ == "__main__":
    main()
