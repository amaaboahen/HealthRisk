# HealthRisk — Interactive Healthcare Analytics & Insights

An educational Streamlit dashboard for exploring **synthetic** demographics, smoking history, and invented organ-specific simulation labels. Dark navy and teal styling, responsive Plotly charts, original vector schematics, filters, validated CSV uploads, and downloadable data and reports.

**No diagnoses, clinical risk estimates, validated predictions, or medical advice. Associations are descriptive and do not show that smoking caused a difference. Never upload real patient data.**

## Run locally

Python 3.12 is the tested runtime.

```bash
cd /workspace/HealthRisk  # or your checkout directory
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.headless=true
```

Streamlit reports its local address in the terminal. No API key, external service, database, or LLM is required. The repository is already isolated in the cloud; use its existing checkout without creating a worktree.

```bash
.venv/bin/python -m pytest -q
```

## Dashboard

Choose Whole body, Heart, Lungs, Kidneys, or Liver. Every view updates the score KPI, group distribution, smoking-group composition, age scatter, comparison box plot, and fixed-rule insights. Sidebar filters select age, sex, smoking status, and BMI. Empty selections give a helpful empty state. Download the filtered CSV or a Markdown report containing filters, counts, descriptive insights, and numeric statistics. The Data & methodology tab includes the dictionary, scoring rules, and complete sample download.

The original geometric organ illustration uses teal and orange to identify Lower and Higher groups. It does **not** depict disease, tissue damage, or anatomical differences. Charts show actual cohort summaries; schematics are illustrative.

## Reproducible sample

`data/synthetic_patients.csv` contains 2,500 records from `generate_data(seed=42)`. Regenerate from the repository root:

```bash
.venv/bin/python -c "from healthrisk.data import generate_data; generate_data().to_csv('data/synthetic_patients.csv', index=False)"
```

NumPy draws age uniformly from integer years 18–90; smoking status probabilities are Never .48, Former .27, Current .25. Smoking duration is zero for Never, otherwise rounded uniform .08–.95 × (age−18). BMI is clipped Normal(27,5). Cholesterol is clipped 170 + .6×(age−18) + 1.5×(BMI−22) + Normal(0,30). Systolic pressure is clipped 100 + .55×(age−18) + .5×(BMI−22) + Normal(0,13). Diastolic pressure is clipped 65 + .2×(age−18) + Normal(0,9), capped below systolic by 10. Sex probabilities are Female .49, Male .49, Other .02; sex does not affect scoring. Bounds appear below.

## CSV dictionary and validation

UTF-8 CSV, up to 10 MB and 100,000 rows. All ten input columns are required; no missing/nonfinite values. Category spelling is case sensitive. Identifiers must be unique and nonempty. Extra columns are ignored, including uploaded scores and labels, which are always recomputed. An invalid upload displays specific errors and continues showing clearly labeled demo data. Users must confirm the upload is synthetic. Uploads are processed in memory, not intentionally persisted to disk; deploy with appropriate access controls for shared use.

| Column | Type / unit | Accepted values |
|---|---|---|
| patient_id | identifier | unique, nonempty |
| age | whole years | 18–90 |
| sex | category | Female, Male, Other |
| smoking_status | category | Never, Former, Current |
| smoking_duration | years | 0–72; ≤ age−18; Never must be 0 |
| bmi | kg/m² | 12–60 |
| cholesterol | total, mg/dL | 80–400 |
| systolic_bp | mmHg | 70–240 |
| diastolic_bp | mmHg | 40–150; below systolic |

These bounds are schema constraints, not clinical reference intervals. Outputs include `<organ>_score` (0–100) and `<organ>_risk` (Lower, Moderate, Higher), with `whole_body` as the whole-body prefix. `risk_category` aliases `whole_body_risk`.

## Transparent simulation rules

Normalize each component, clipping to [0,1]: age=(age−18)/72; duration=smoking_duration/60; BMI=(BMI−18)/22; cholesterol=(cholesterol−120)/180; pressure=(systolic_bp−90)/90. Score = 100 × weighted sum, rounded to one decimal. **Lower ≤35; Moderate >35–60; Higher >60.** Thresholds and weights are arbitrary, not calibrated clinical cutoffs. A score is not a probability. Sex, smoking status, and diastolic pressure have no direct scoring weight.

| Lens | Age | Duration | BMI | Cholesterol | Pressure |
|---|---:|---:|---:|---:|---:|
| Whole body | .20 | .20 | .20 | .20 | .20 |
| Heart | .20 | .15 | .15 | .25 | .25 |
| Lungs | .25 | .55 | .10 | .05 | .05 |
| Kidneys | .25 | .10 | .20 | .10 | .35 |
| Liver | .15 | .10 | .50 | .15 | .10 |

Insights are fixed Python rules: report Higher counts/shares; compare highest and lowest mean score among available smoking groups with group sizes; compare mean ages when Lower and Higher groups exist; flag cohorts below 30 records. No LLM or remote inference is involved.

## Limitations

Generation and scoring deliberately build relationships into the data, so comparing groups defined by those scores can be circular. Smoking duration enters the scores directly; differences across smoking groups are not independent evidence of an effect. No clinical outcomes, cessation effects, socioeconomic confounders, uncertainty estimates, or causal analysis are modeled. Organ lenses are educational constructs rather than physiological models. Uploaded synthetic data may follow different distributions. Filters can create small or unrepresentative subgroups. This application must not guide patient care or infer disease.

## Project layout

- `app.py`: Streamlit UI and CSV handling
- `healthrisk/data.py`: generation, scoring, validation, filters
- `healthrisk/analytics.py`: descriptive insights and reports
- `healthrisk/visuals.py`: original Plotly vector schematics
- `.streamlit/config.toml`: theme and upload limit
- `tests/`: dataset, validation, scoring, reporting, and Streamlit interaction tests
- `data/synthetic_patients.csv`: reproducible sample

Dependencies are pinned in `requirements.txt`. Tests use Streamlit's AppTest and pytest. No changes are pushed automatically.
