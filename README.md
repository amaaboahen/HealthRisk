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

Select an **Educational condition** independently of the data. Healthy/reference and condition panels show different, source-informed mechanism schematics: artery lumen narrowing, loss of alveolar septa, nephron loss/fibrosis, or fibrous liver bands and nodules. Drag to pan and scroll to zoom each 2D panel independently. Use **Use static educational illustrations (no interactive canvas)** for static images. The **3D reference anatomy & licensed source illustrations** expander provides rotatable/zoomable reference models for heart, lungs, liver, and whole-body anatomy, plus a licensed kidney reference illustration. No reference mesh is deformed into a disease model. The risk charts retain the separate Lower/Moderate/Higher simulation categories.

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
- `assets/anatomy/`: compressed reference atlas meshes and license notices
- `assets/education/`: condition diagrams, source illustrations, and historical CC BY license
- `tools/`: optional offline mesh export, reduction, rendering, and Chromium smoke checks

Dependencies are pinned in `requirements.txt`. Tests use Streamlit's AppTest and pytest. No changes are pushed automatically.


## Educational comparisons: scope and medical limitations

| Organ | Independently selected topic | Visible teaching difference |
|---|---|---|
| Heart | Coronary artery disease | Plaque within the arterial wall reduces lumen space; the outside of the heart may appear unchanged |
| Lungs | Emphysema | Loss of alveolar septa produces enlarged, connected airspaces |
| Kidneys | Advanced CKD-related changes | Conceptual loss of functioning nephron units and fibrosis; no universal kidney size or stage is inferred |
| Liver | Cirrhosis | Fibrous bands and regenerative nodules disrupt tissue architecture |
| Whole body | Any of the four topics | Selected tissue-level comparison plus a separate reference skeleton/organ atlas; no whole-body disease mesh |

Reliable disease-specific 3D meshes with clear provenance were not available for
this release. The app therefore uses the requested **illustration fallback**,
clearly labeled **2D source-informed mechanism schematics**. These are not
realistic reconstructed diseased organs, scans, quantitative pathology, or
independently clinically reviewed/validated illustrations. They communicate
standard medical mechanisms with deliberately simplified structures. See the
condition explanations for functional effects, causes/risk factors, sources, and
limitations. In particular, CKD has diverse causes and kidneys may be small,
normal-sized, or enlarged; a “shrunken kidney” is not a universal representation.

Population filters recalculate counts, mean scores, simulation-label shares,
health indicators, insights, CSV exports, and reports. The education panel reports
cohort context (age, BMI, smoking counts) without claiming condition prevalence.
Condition choices and images are **not functions of smoking, sex, age, BMI, or
simulated scores**. Sex filtering retains Female/Male/Other from the existing
synthetic schema. Whole-body condition switching never changes the score formula.
Reports include the selected educational topic in a separate, explicitly labeled
section. No illustrations diagnose disease, estimate a clinical probability, or
predict organ appearance.

## Artwork sources and portfolio licensing

**Original HealthRisk mechanism schematics** (SVG masters and 1200×920 PNGs):
MIT-licensed artwork generated by `tools/build_education.py`. These illustrate
medical facts; they are not copies of copyrighted source figures and do not deform
anatomical meshes. Factual context comes from OpenStax Anatomy and Physiology 2e
and the linked NHLBI/NIDDK educational resources. OpenStax modules were inspected;
NIH pages were blocked by the build network and are linked as authoritative
further reading. No claim of independent medical review is made.

**Licensed kidney anatomy and artery illustration:** OpenStax / Rice University,
Anatomy and Physiology 2e, historical commit
`b0058a743bdd2cc08196abaaa7d5469970c0d80c` of
https://github.com/openstax/osbooks-anatomy-physiology, explicitly licensed
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) in that edition.
This edition predates the repository's 2026-03-19 noncommercial license change;
its already-granted CC BY permissions are irrevocable when terms are followed.
The kidney illustration is unmodified. Only panel (a) of the artery illustration
is included; the separately credited University of Michigan micrograph is excluded.
Full attribution, changes, and the historical license are retained in
[assets/education/ATTRIBUTION.md](assets/education/ATTRIBUTION.md).

**3D reference atlas:** Z-Anatomy — The libre 3D atlas of anatomy, by Gauthier
Kervyn, Marcin Zielinski, and contributors, derived in part from BodyParts3D —
The Database Center for Life Science, original model by Kousaku Okubo.
Source: https://github.com/Z-Anatomy/Models-of-human-anatomy at commit
`9de5d6912a1b0df9cab739d57f00e036b0496ddc`.
Atlas [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/);
original BodyParts3D attribution
[CC BY-SA 2.1 Japan](https://creativecommons.org/licenses/by-sa/2.1/jp/).
Keep attribution/share-alike terms for redistributed atlas derivatives; these
assets are not covered by the application's MIT license. They depict reference
surfaces, not condition-specific pathology.

The previous kidney mesh with uncertain noncommercial reference provenance was
**removed**, including the kidney parts of the whole-body asset and the kidney
render. The whole-body view now includes skeleton, heart, lungs, and liver; its
missing kidneys are available in the separately licensed 2D reference. The original
upstream notices are retained for provenance, including references not used in
this release. See [assets/anatomy/ATTRIBUTION.md](assets/anatomy/ATTRIBUTION.md).
There are no imported noncommercial kidney assets in this release.

## Streamlit Community Cloud

Deploy `app.py` on Python 3.12 with `requirements.txt`. All models, diagrams, and
source illustrations are local repository files. The viewer uses Streamlit's
built-in Plotly renderer, not a custom component or external CDN. No API key,
Blender, CairoSVG, or native image converter is required at runtime. Static image
mode handles devices without an interactive canvas. PNGs are prepared in advance;
SVG generation and browser checks use development dependencies only.

Include `assets/anatomy/` and `assets/education/` in the deployment. Cached figures
and compact typed arrays reduce rerender overhead. Runtime/import compatibility
and server startup were checked locally; **a live Community Cloud deployment has
not been performed**.

## Additional development validation

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m pip install -r requirements-dev.txt
# Chromium required; CHROMIUM_PATH can override its location.
.venv/bin/python -m streamlit run app.py --server.headless=true --server.port=8502
# Separate terminal:
.venv/bin/python -m tools.browser_smoke --url http://127.0.0.1:8502
```

The suite covers original generation/upload/report behavior, reference mesh
integrity, removal of restricted kidney assets, different condition illustrations,
independent axes, all five organ comparisons, all smoking/sex/age/BMI filters,
cohort context, condition independence, static fallback, and education exports.
Browser checks exercise pan/zoom of all comparisons, rotation/zoom of available
reference models, condition switching, fallback, uploads, and actual downloads.

Development-only tools: `tools/export_anatomy.py` extracts source meshes with
Blender, `tools/optimize_anatomy.py` reduces them, `tools/render_anatomy.py` renders
reference fallbacks, and `tools/build_education.py` builds original mechanism
illustrations. Normal startup does not execute these tools or download artwork.

## Community Cloud import troubleshooting

The documented deployment is Python 3.12, repository `amaaboahen/HealthRisk`,
branch `main`, entrypoint `app.py`, with dependencies installed from the root
`requirements.txt`. Do not deploy from an older branch or a different entrypoint.

The dashboard imports reference rendering directly from
`healthrisk/anatomy_views.py` and condition comparison rendering from
`healthrisk/condition_views.py`. `healthrisk/visuals.py` remains a compatibility
export for existing tests and tools. The two view implementations do not import
each other; condition rendering depends only on the curated education module.
The unused `fallback_path` import was removed from the entrypoint; the function
remains available to rendering tools.

Investigation found all four names in the merged source and successful startup
from a clean runtime-only install. Loading the pre-condition `healthrisk.visuals`
module into Python's module cache reproduces `cannot import name
'condition_figure'`. A running deployment can then have a new `app.py` alongside
an older imported module. The explicit modules avoid that dependency on the old
visuals namespace. The supplied Cloud traceback identifies the same missing symbol in the local
repository module on Python 3.12 immediately after “Updated app!”. Together
with clean startup of the merged source, this strongly points to stale imported
code during the live update. The Cloud interpreter cache was not directly inspected.

After deploying a reviewed fix, use Community Cloud's **Reboot app** action to
start a fresh interpreter. Confirm the branch, entrypoint, Python version, and
installation logs. If the error remains, retain the complete traceback (including
the missing name and module path); a line number alone cannot distinguish stale
code from a missing dependency or an incorrect deployment branch.

`tests/test_imports.py` imports the real `app.py` in a fresh subprocess, exercises
startup with an old visuals namespace cached, checks public compatibility exports,
and checks both view-module import orders. GitHub Actions installs only the runtime
requirements on Python 3.12 and runs the full suite on pushes and PRs. This avoids
relying on development-only CairoSVG or Playwright for app startup.
