"""Reproducible data and deliberately arbitrary educational scoring rules."""
import numpy as np
import pandas as pd

ORGANS = {
    "Whole body": {"age": .20, "duration": .20, "bmi": .20, "cholesterol": .20, "pressure": .20},
    "Heart": {"age": .20, "duration": .15, "bmi": .15, "cholesterol": .25, "pressure": .25},
    "Lungs": {"age": .25, "duration": .55, "bmi": .10, "cholesterol": .05, "pressure": .05},
    "Kidneys": {"age": .25, "duration": .10, "bmi": .20, "cholesterol": .10, "pressure": .35},
    "Liver": {"age": .15, "duration": .10, "bmi": .50, "cholesterol": .15, "pressure": .10},
}
RANGES = {"age": (18, 90), "smoking_duration": (0, 72), "bmi": (12, 60),
          "cholesterol": (80, 400), "systolic_bp": (70, 240), "diastolic_bp": (40, 150)}
CATEGORIES = ["Lower", "Moderate", "Higher"]
REQUIRED = ["patient_id", "age", "sex", "smoking_status", *list(RANGES)[1:]]
DISCLAIMER = "Educational synthetic data only. Scores and categories are arbitrary simulation labels, not diagnoses, clinical risk estimates, or validated predictions. Observed differences do not establish causation."


def score_data(df):
    out = df.copy()
    components = pd.DataFrame({
        "age": (out.age - 18) / 72,
        "duration": out.smoking_duration / 60,
        "bmi": (out.bmi - 18) / 22,
        "cholesterol": (out.cholesterol - 120) / 180,
        "pressure": (out.systolic_bp - 90) / 90,
    }).clip(0, 1)
    for organ, weights in ORGANS.items():
        key = organ.lower().replace(" ", "_")
        out[f"{key}_score"] = (sum(components[k] * w for k, w in weights.items()) * 100).round(1)
        out[f"{key}_risk"] = pd.cut(out[f"{key}_score"], [-1, 35, 60, 100], labels=CATEGORIES).astype(str)
    out["risk_category"] = out.whole_body_risk
    return out


def generate_data(n=2500, seed=42):
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 91, n)
    status = rng.choice(["Never", "Former", "Current"], n, p=[.48, .27, .25])
    duration = np.where(status == "Never", 0, (rng.uniform(.08, .95, n) * (age - 18)).round())
    bmi = np.clip(rng.normal(27, 5, n), 12, 60).round(1)
    systolic = np.clip(100 + .55 * (age - 18) + .5 * (bmi - 22) + rng.normal(0, 13, n), 70, 240).round()
    df = pd.DataFrame({"patient_id": [f"SYN-{i:05d}" for i in range(1, n + 1)], "age": age,
        "sex": rng.choice(["Female", "Male", "Other"], n, p=[.49, .49, .02]),
        "smoking_status": status, "smoking_duration": duration, "bmi": bmi,
        "cholesterol": np.clip(170 + .6 * (age - 18) + 1.5 * (bmi - 22) + rng.normal(0, 30, n), 80, 400).round(),
        "systolic_bp": systolic,
        "diastolic_bp": np.minimum(np.clip(65 + .2 * (age - 18) + rng.normal(0, 9, n), 40, 150).round(), systolic - 10)})
    return score_data(df)


def validate_data(df):
    errors = []
    if df.columns.duplicated().any():
        errors.append("Duplicate column names are not allowed.")
    missing = set(REQUIRED) - set(df.columns)
    if missing:
        errors.append("Missing required columns: " + ", ".join(sorted(missing)))
    if errors:
        return None, errors
    if not 1 <= len(df) <= 100000:
        return None, ["Provide between 1 and 100,000 records."]
    out = df[REQUIRED].copy()
    if out.patient_id.isna().any() or out.patient_id.astype(str).str.strip().eq("").any() or out.patient_id.duplicated().any():
        errors.append("patient_id must be nonempty and unique.")
    for col, (low, high) in RANGES.items():
        out[col] = pd.to_numeric(out[col], errors="coerce")
        if (~np.isfinite(out[col]) | ~out[col].between(low, high)).any():
            errors.append(f"{col} must contain finite numbers between {low} and {high}; no missing values.")
    if out.age.notna().all() and (out.age % 1 != 0).any():
        errors.append("age must contain whole years.")
    for col, choices in {"sex": ["Female", "Male", "Other"], "smoking_status": ["Never", "Former", "Current"]}.items():
        if not out[col].isin(choices).all():
            errors.append(f"{col} must be one of: {', '.join(choices)} (case sensitive).")
    if (out.smoking_duration > out.age - 18).any():
        errors.append("smoking_duration cannot exceed age minus 18 (this simulation assumes adult smoking onset).")
    if ((out.smoking_status == "Never") & (out.smoking_duration != 0)).any():
        errors.append("Never smokers must have smoking_duration equal to 0.")
    if (out.diastolic_bp >= out.systolic_bp).any():
        errors.append("diastolic_bp must be below systolic_bp.")
    return (None, errors) if errors else (score_data(out), [])


def filter_data(df, ages, statuses, sexes, bmi):
    return df[df.age.between(*ages) & df.smoking_status.isin(statuses) & df.sex.isin(sexes) & df.bmi.between(*bmi)].copy()
