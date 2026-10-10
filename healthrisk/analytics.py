"""Transparent descriptive summaries; no external models or medical advice."""
from .data import DISCLAIMER, CATEGORIES


def organ_key(organ):
    return organ.lower().replace(" ", "_")


def insights(df, organ):
    if df.empty:
        return ["No records match these filters. Widen the selected ranges to explore the data."]
    key = organ_key(organ)
    higher = df[f"{key}_risk"].eq("Higher")
    result = [f"{len(df):,} selected synthetic records; {higher.sum():,} ({higher.mean():.1%}) carry the Higher {organ.lower()} simulation label."]
    grouped = df.groupby("smoking_status", observed=True)[f"{key}_score"].agg(["mean", "count"])
    if len(grouped) >= 2:
        top, bottom = grouped['mean'].idxmax(), grouped['mean'].idxmin()
        result.append(f"Mean simulation score: {top} {grouped.loc[top, 'mean']:.1f} (n={int(grouped.loc[top, 'count'])}) versus {bottom} {grouped.loc[bottom, 'mean']:.1f} (n={int(grouped.loc[bottom, 'count'])}). Scoring includes smoking duration by design; this comparison is not causal evidence.")
    lo, hi = df[df[f"{key}_risk"] == "Lower"], df[higher]
    if len(lo) and len(hi):
        result.append(f"Mean age is {lo.age.mean():.1f} in the Lower group and {hi.age.mean():.1f} in the Higher group. Age enters the simulation formula, so this pattern is partly built into the labels.")
    if len(df) < 30:
        result.append("Fewer than 30 selected records: descriptive comparisons may vary substantially with filters.")
    return result


def summary_report(df, organ, source, filters):
    key = organ_key(organ)
    counts = df[f"{key}_risk"].value_counts().reindex(CATEGORIES, fill_value=0)
    lines = ["# HealthRisk — Synthetic analytics report", "", DISCLAIMER, "", f"Source: {source}",
             f"Organ: {organ}", f"Filters: {filters}", f"Records: {len(df):,}", "", "## Simulation labels"]
    lines += [f"- {cat}: {int(counts[cat])}" for cat in CATEGORIES]
    lines += ["", "## Rule-based descriptive insights"] + [f"- {s}" for s in insights(df, organ)]
    lines += ["", "## Numeric summary", df[["age", "smoking_duration", "bmi", "cholesterol", "systolic_bp", "diastolic_bp"]].describe().to_csv(),
              "", "Scores use clipped normalized inputs and arbitrary organ weights. Lower ≤35; Moderate >35–60; Higher >60. See README for full rules. These scores are not probabilities. No real patient data should be uploaded."]
    return "\n".join(lines)
