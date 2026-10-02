"""Статистичні тести гіпотез H1–H6."""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

FOCAL = [
    # (гіпотеза, умова, показник, очікуваний знак)
    ("H2", "P1", "share_budget", +1),
    ("H2", "P2", "share_premium", +1),
    ("H3", "P4", "share_incumbent", +1),
    ("H3", "P3", "share_incumbent", -1),
    ("H4", "P5", "share_premium", 0),
    ("H5", "P6", "share_incumbent", 0),
]


def sign_flip_test(values, n_perm=20000, seed=0):
    x = np.asarray(values, dtype=float)
    x = x[~np.isnan(x)]
    observed = x.mean()
    signs = np.random.default_rng(seed).choice([-1.0, 1.0], size=(n_perm, len(x)))
    null = (signs * x).mean(axis=1)
    return float(observed), float((1 + (null >= observed).sum()) / (n_perm + 1))


def cluster_bootstrap_ci(df, value, cluster="query_id", n_boot=5000, seed=0):
    per_cluster = df.groupby(cluster)[value].mean().dropna().to_numpy()
    rng = np.random.default_rng(seed)
    draws = rng.choice(per_cluster, size=(n_boot, len(per_cluster)), replace=True).mean(axis=1)
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def h1_table(shift, metric="delta_jaccard"):
    rows = []
    groups = list(shift.groupby(["model", "condition"])) + [
        (("pooled", cond), g) for cond, g in shift.groupby("condition")
    ]
    for (model, condition), g in groups:
        per_query = g.groupby("query_id")[metric].mean()
        mean, p = sign_flip_test(per_query.to_numpy())
        low, high = cluster_bootstrap_ci(g, metric)
        rows.append({"model": model, "condition": condition, "mean_delta": mean, "ci_low": low,
                     "ci_high": high, "p": p, "n_queries": int(per_query.notna().sum())})
    table = pd.DataFrame(rows)
    for family in (table.model == "pooled", table.model != "pooled"):
        table.loc[family, "p_holm"] = multipletests(table.loc[family, "p"], method="holm")[1]
    return table


def share_gee(responses, outcome, reference="B"):
    data = responses.dropna(subset=[outcome])
    if reference != "C0":
        data = data[data.condition != "C0"]
    if reference != "PL":
        data = data[data.condition != "PL"]
    model = smf.gee(
        f"{outcome} ~ C(condition, Treatment('{reference}')) + C(model)",
        groups="query_id", data=data,
        cov_struct=sm.cov_struct.Exchangeable(), family=sm.families.Gaussian(),
    )
    fit = model.fit()
    ci = fit.conf_int()
    rows = []
    for name in fit.params.index:
        if name.startswith("C(condition"):
            rows.append({"condition": name.split("[T.")[1].rstrip("]"), "coef": fit.params[name],
                         "ci_low": ci.loc[name, 0], "ci_high": ci.loc[name, 1], "p": fit.pvalues[name]})
    return pd.DataFrame(rows)


def focal_contrasts(responses):
    rows = []
    for hypothesis, condition, outcome, sign in FOCAL:
        effect = share_gee(responses, outcome).set_index("condition").loc[condition]
        rows.append({"hypothesis": hypothesis, "condition": condition, "outcome": outcome,
                     "expected_sign": sign, **effect.to_dict()})
    table = pd.DataFrame(rows)
    table["p_holm"] = multipletests(table["p"], method="holm")[1]
    return table


def equivalence(df, value, sesoi, cluster="query_id", n_boot=5000, seed=0):
    """Еквівалентність (TOST через 90 % cluster bootstrap CI): ефект вважається практично нульовим,
    якщо весь 90 % CI лежить у межах ±sesoi."""
    low, high = cluster_bootstrap_ci_level(df, value, cluster, 0.90, n_boot, seed)
    return {"ci90_low": low, "ci90_high": high, "equivalent": bool(-sesoi < low and high < sesoi)}


def cluster_bootstrap_ci_level(df, value, cluster, level, n_boot=5000, seed=0):
    per_cluster = df.groupby(cluster)[value].mean().dropna().to_numpy()
    draws = np.random.default_rng(seed).choice(per_cluster, size=(n_boot, len(per_cluster)), replace=True).mean(axis=1)
    tail = (1 - level) / 2 * 100
    return float(np.percentile(draws, tail)), float(np.percentile(draws, 100 - tail))


# Найменший практично значущий ефект: 0,05 Jaccard ≈ заміна одного з ~4 брендів у кожній восьмій відповіді.
SESOI = 0.05


def placebo_table(shift, metric="jaccard_to_base", by_model=False, sesoi=SESOI):
    """Чи зсуває ознака набір брендів сильніше за плацебо-деталь: різниця подібності до бази (PL − Pk) у межах
    пари «модель × запит»; додатна різниця означає, що ознака змінює набір сильніше за нейтральну деталь."""
    groups = list(shift.groupby("model")) if by_model else [("pooled", shift)]
    rows = []
    for model, part in groups:
        wide = part.pivot_table(index=["model", "query_id"], columns="condition", values=metric)
        for condition in [c for c in wide.columns if c != "PL"]:
            diff = (wide["PL"] - wide[condition]).dropna().rename("diff").reset_index()
            per_query = diff.groupby("query_id")["diff"].mean()
            mean, p = sign_flip_test(per_query.to_numpy())
            low, high = cluster_bootstrap_ci(diff, "diff")
            rows.append({"model": model, "condition": condition, "mean_diff": mean, "ci_low": low, "ci_high": high,
                         "p": p, "n_queries": len(per_query), **equivalence(diff, "diff", sesoi)})
    table = pd.DataFrame(rows)
    table["p_holm"] = table.groupby("model")["p"].transform(lambda x: multipletests(x, method="holm")[1])
    return table


def interaction_test(shift, metric="delta_jaccard"):
    """H6: чи залежить ефект умови від моделі — Wald-тест членів взаємодії condition × model у GEE з кластерами за запитом."""
    data = shift.dropna(subset=[metric])
    fit = smf.gee(f"{metric} ~ C(condition) * C(model)", groups="query_id", data=data,
                  cov_struct=sm.cov_struct.Exchangeable(), family=sm.families.Gaussian()).fit()
    names = [n for n in fit.params.index if ":" in n]
    constraint = np.zeros((len(names), len(fit.params)))
    for i, name in enumerate(names):
        constraint[i, list(fit.params.index).index(name)] = 1
    return float(fit.wald_test(constraint, scalar=True).pvalue)


def sameday_placebo_table(shift_main, shift_wave2, metric="delta_jaccard", sesoi=SESOI):
    """Ознака проти плацебо, коли кожне виміряно в межах одного дня: Δ ознаки (вересень, відносно тогочасної бази)
    мінус Δ плацебо (жовтень, відносно бази, зібраної того ж дня). Додатне — ознака зсуває набір сильніше."""
    placebo = shift_wave2[shift_wave2.condition == "PL"][["model", "query_id", metric]].rename(columns={metric: "placebo"})
    rows = []
    for condition, part in shift_main[shift_main.condition != "PL"].groupby("condition"):
        merged = part[["model", "query_id", metric]].merge(placebo, on=["model", "query_id"]).dropna()
        merged["diff"] = merged[metric] - merged["placebo"]
        per_query = merged.groupby("query_id")["diff"].mean()
        mean, p = sign_flip_test(per_query.to_numpy())
        low, high = cluster_bootstrap_ci(merged, "diff")
        rows.append({"condition": condition, "mean_diff": mean, "ci_low": low, "ci_high": high, "p": p,
                     "n_queries": len(per_query), **equivalence(merged, "diff", sesoi)})
    table = pd.DataFrame(rows)
    table["p_holm"] = multipletests(table["p"], method="holm")[1]
    return table


def drift_table(lists_main, lists_wave2, condition="B"):
    """Дрейф у часі: шумова межа бази у вересні мінус подібність вересневої бази до жовтневої (Jaccard)."""
    from collections import defaultdict
    from itertools import combinations, product

    from metrics import jaccard

    def cells(lists):
        out = defaultdict(list)
        for (model, query_id, cond, _), brands in lists.items():
            if cond == condition:
                out[(model, query_id)].append(brands)
        return out

    first, second = cells(lists_main), cells(lists_wave2)
    rows = []
    for key in first.keys() & second.keys():
        noise = [jaccard(a, b) for a, b in combinations(first[key], 2)]
        cross = [jaccard(a, b) for a, b in product(first[key], second[key])]
        noise, cross = np.nanmean(noise) if noise else np.nan, np.nanmean(cross) if cross else np.nan
        rows.append({"model": key[0], "query_id": key[1], "drift": noise - cross})
    df = pd.DataFrame(rows)
    out = []
    for model, part in [("pooled", df), *df.groupby("model")]:
        per_query = part.groupby("query_id")["drift"].mean()
        mean, p = sign_flip_test(per_query.to_numpy())
        low, high = cluster_bootstrap_ci(part, "drift")
        out.append({"model": model, "mean_drift": mean, "ci_low": low, "ci_high": high, "p": p})
    return pd.DataFrame(out)


def brand_mention_contrasts(mentions, brands, conditions, reference="B"):
    """Частота згадки окремих брендів (0/1 на відповідь) за умовами відносно бази: GEE, кластери за запитом, Holm."""
    rows = []
    for brand in brands:
        data = mentions[(mentions.brand == brand) & mentions.condition.isin([reference, *conditions])]
        effects = share_gee(data, "mentioned", reference=reference).set_index("condition")
        for condition in conditions:
            rows.append({"brand": brand, "condition": condition, **effects.loc[condition].to_dict()})
    table = pd.DataFrame(rows)
    table["p_holm"] = multipletests(table["p"], method="holm")[1]
    return table
