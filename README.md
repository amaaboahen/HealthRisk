# HealthRisk — Interactive Healthcare Analytics & Insights

An educational Streamlit dashboard for exploring **synthetic** demographics, smoking history, and invented organ-specific simulation labels. Dark navy and teal styling, responsive Plotly charts, bundled interactive 3D anatomical atlas models, filters, validated CSV uploads, and downloadable data and reports.

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

The anatomical viewer uses the same realistic atlas meshes, naturalistic materials, and starting camera in both Lower and Higher panels. Drag to rotate, scroll/pinch to zoom, and reset the camera through the Plotly toolbar. Each panel moves independently. The models do **not** depict organ damage or patient-specific anatomy. Select **Use static anatomical rendering (no WebGL)** for the bundled high-resolution fallback images, rendered from those same meshes. Charts continue to show cohort summaries in either mode.

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
- `healthrisk/visuals.py`: local mesh loader and Plotly 3D comparison scenes
- `.streamlit/config.toml`: theme and upload limit
- `tests/`: dataset, validation, scoring, reporting, and Streamlit interaction tests
- `data/synthetic_patients.csv`: reproducible sample
- `assets/anatomy/`: compressed atlas meshes, static PNG fallbacks, and license notices
- `tools/`: optional offline mesh export, reduction, rendering, and Chromium smoke checks

Dependencies are pinned in `requirements.txt`. Tests use Streamlit's AppTest and pytest. No changes are pushed automatically.


## Anatomy assets and licenses

All five views use **Z-Anatomy — The libre 3D atlas of anatomy**, by Gauthier
Kervyn, Marcin Zielinski, and contributors, derived in part from **BodyParts3D —
The Database Center for Life Science**, original model by Kousaku Okubo.
Source: https://github.com/Z-Anatomy/Models-of-human-anatomy at commit
`9de5d6912a1b0df9cab739d57f00e036b0496ddc`, `Z-Anatomy.zip/Startup.blend`.

The atlas declares [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/);
the original BodyParts3D attribution is
[CC BY-SA 2.1 Japan](https://creativecommons.org/licenses/by-sa/2.1/jp/).
The upstream atlas additionally credits **Kidney — Lissie Cowley —
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)** without
per-object provenance. We preserve that attribution and conservatively restrict
the kidney assets (including their inclusion in the whole-body view and rendered
PNGs) to noncommercial use. This educational application must not be treated as
commercially cleared anatomy artwork. Obtain provenance clarification or replace
the kidney meshes before commercial deployment.

Assets and their rendered derivatives retain the applicable Creative Commons
terms; the repository's MIT license applies to application code, not these
third-party assets. Full source notices, included structures, modifications, and
licensing details are in [assets/anatomy/ATTRIBUTION.md](assets/anatomy/ATTRIBUTION.md).
Heart includes atria, ventricles and pulmonary trunk; lungs include all five lobes
and trachea; kidneys include paired kidneys and renal pelves; liver is its outer
surface; the whole-body view places these organs inside a reference skeleton.
Fine surface detail is reduced for performance. These are atlas-based surface
representations, not a complete dissection, validated clinical imaging, or an
anatomical model of any selected synthetic record. Anatomy accuracy is limited
by the source atlas and mesh simplification. Scores never change geometry or color.

## Streamlit Community Cloud

Deploy `app.py` from this repository on Python 3.12. `requirements.txt` contains
all runtime dependencies. All meshes and PNGs are bundled; the viewer makes no
external model/CDN request, uses Streamlit's built-in Plotly renderer, and requires
no Blender, API keys, custom component server, or native runtime libraries.
Make sure `assets/anatomy/` is included in the deployment. WebGL is a browser
capability; the static toggle supports devices that cannot run it. A model is
cached locally by organ, and compact typed arrays reduce payload overhead.
Live Community Cloud deployment has not been performed as part of this change.

### Additional development validation

The core suite includes all original dashboard tests plus local asset integrity,
identical comparison geometry/materials, all organ views, and static fallbacks:

```bash
.venv/bin/python -m pytest -q
```

For real-browser mouse rotation/zoom, rendered WebGL scenes, a valid upload,
CSV/report downloads, fallback images, and a narrow viewport:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
# Requires Chromium installed locally; CHROMIUM_PATH can override its location.
.venv/bin/python -m streamlit run app.py --server.headless=true --server.port=8502
# In a separate terminal:
.venv/bin/python -m tools.browser_smoke --url http://127.0.0.1:8502
```

Development-only `playwright` and `fast-simplification` are kept out of runtime
requirements. `tools/export_anatomy.py` can extract the pinned source archive with
Blender; `tools/optimize_anatomy.py` reduces triangle counts, and
`tools/render_anatomy.py` regenerates the bundled static fallbacks. Normal app
startup does not run any of these tools or download assets.
