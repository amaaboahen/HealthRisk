"""HealthRisk — interactive educational healthcare analytics."""
import pandas as pd
import plotly.express as px
import streamlit as st
from healthrisk.data import generate_data, filter_data, ORGANS, CATEGORIES, DISCLAIMER
from healthrisk.analytics import insights, summary_report, organ_key
from healthrisk.visuals import anatomy_figure, fallback_path
from healthrisk.uploads import load_csv

st.set_page_config(page_title="HealthRisk | Healthcare Analytics", page_icon="🫀", layout="wide")
st.markdown('''<style>
.block-container {padding-top:2rem; max-width:1450px}
h1 {letter-spacing:-1.5px} h3 {letter-spacing:-.4px}
[data-testid="stMetric"] {background:#102237;border:1px solid #223d50;border-radius:14px;padding:18px}
[data-testid="stMetricValue"] {color:#2dd4bf}
[data-testid="stSidebar"] {border-right:1px solid #223d50}
.hero-label {color:#2dd4bf;letter-spacing:3px;font-size:12px;font-weight:700}
</style>''', unsafe_allow_html=True)

@st.cache_data
def demo_data():
    return generate_data()

st.markdown('<div class="hero-label">EDUCATIONAL ANALYTICS · SYNTHETIC DATA ONLY</div>', unsafe_allow_html=True)
st.title("HealthRisk")
st.markdown("### Interactive Healthcare Analytics & Insights")
st.caption("Explore demographic patterns and organ-specific simulation labels in a transparent educational sandbox.")
st.info(DISCLAIMER)

with st.sidebar:
    st.header("Explore your cohort")
    st.caption("Use synthetic records only. Uploaded data stays in this app session and is not written to disk.")
    upload = st.file_uploader("Upload synthetic CSV", type=["csv"], help="Maximum 10 MB, 100,000 records. Required schema is in the Data & methodology tab.")
    confirmed = st.checkbox("I confirm the uploaded file contains synthetic data only")

df = demo_data()
source = "Generated demo • seed 42"
if upload is not None:
    if not confirmed:
        st.warning("Confirm that your uploaded CSV is synthetic before it is analyzed. Showing demo data.")
    else:
        candidate, errors = load_csv(upload.getvalue())
        if errors:
            for error in errors:
                st.error(error)
            st.warning("Upload was rejected. Showing demo data; correct the CSV and try again.")
        else:
            df, source = candidate, "Uploaded synthetic CSV"
            st.success(f"Validated {len(df):,} synthetic records. Simulation scores were recomputed; supplied score columns are ignored.")

with st.sidebar:
    st.caption(f"Active source: {source}")
    ages = st.slider("Age range", 18, 90, (18, 90))
    statuses = st.multiselect("Smoking status", ["Never", "Former", "Current"], default=["Never", "Former", "Current"])
    sexes = st.multiselect("Sex", ["Female", "Male", "Other"], default=["Female", "Male", "Other"])
    bmi = st.slider("BMI range", 12.0, 60.0, (12.0, 60.0), step=.5)
    st.divider()
    st.caption("All observations are descriptive. Synthetic associations are influenced by generation and scoring rules.")

selected = filter_data(df, ages, statuses, sexes, bmi)
organ = st.radio("Select an organ system", list(ORGANS), horizontal=True)
key = organ_key(organ)
risk, score = f"{key}_risk", f"{key}_score"
cols = st.columns(4)
cols[0].metric("Selected records", f"{len(selected):,}", f"{len(selected)/len(df):.0%} of active dataset", delta_color="off")
cols[1].metric("Mean simulation score", f"{selected[score].mean():.1f} / 100" if len(selected) else "—")
cols[2].metric("Higher simulation label", f"{selected[risk].eq('Higher').mean():.1%}" if len(selected) else "—")
cols[3].metric("Mean age", f"{selected.age.mean():.1f} years" if len(selected) else "—")
explore, data_tab = st.tabs(["Overview & insights", "Data & methodology"])
COLORS = {"Lower":"#2DD4BF", "Moderate":"#60A5FA", "Higher":"#FB923C"}

def show_chart(fig):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=45,b=15), font=dict(color="#E6EEF7"), legend_title_text="Simulation label")
    st.plotly_chart(fig, use_container_width=True)

with explore:
    st.subheader(f"{organ} · anatomical explorer")
    static_models = st.toggle("Use static anatomical rendering (no WebGL)", value=False,
        help="Choose this if your browser or device cannot display interactive 3D.")
    if static_models:
        lower, higher = st.columns(2)
        for panel, label in [(lower, "Lower simulation label"), (higher, "Higher simulation label")]:
            with panel:
                st.markdown(f"**{label}**")
                st.image(str(fallback_path(organ)), use_container_width=True)
    else:
        st.plotly_chart(anatomy_figure(organ), use_container_width=True, key=f"anatomy-{organ}",
                        config={"scrollZoom": True, "displaylogo": False, "displayModeBar": True})
    st.caption("Drag to rotate · scroll or pinch to zoom · use the camera reset in the toolbar. Each panel rotates independently. Both panels use identical atlas geometry and colors; simulation labels do not alter organ anatomy.")
    st.caption("Atlas: Z-Anatomy / BodyParts3D. Kidney assets carry an upstream noncommercial attribution; see README and assets/anatomy/ATTRIBUTION.md for licenses. This reference anatomy does not represent selected patients or diagnoses.")
    left, right = st.columns([1, 1.2])
    with left:
        st.subheader(f"{organ} · simulation lens")
        weights = ORGANS[organ]
        st.markdown("This lens emphasizes " + ", ".join(f"**{name} ({weight:.0%})**" for name, weight in weights.items()) + ". Weights are invented for learning, with no clinical validation.")
    with right:
        st.subheader("Descriptive insights")
        st.caption("Automated using fixed summary rules • no LLM • no medical advice")
        for item in insights(selected, organ):
            st.markdown(f"- {item}")
    if selected.empty:
        st.warning("No records match the filters. Widen the ranges or select more categories.")
    else:
        a, b = st.columns(2)
        with a:
            show_chart(px.histogram(selected, x=score, color=risk, nbins=25, color_discrete_map=COLORS, category_orders={risk:CATEGORIES}, title="Distribution of arbitrary simulation scores", labels={score:"Simulation score (0–100)",risk:"Simulation label"}))
        with b:
            counts = selected.groupby(["smoking_status", risk], observed=True).size().rename("Records").reset_index()
            counts["Share (%)"] = counts.Records / counts.groupby("smoking_status").Records.transform("sum") * 100
            show_chart(px.bar(counts, x="smoking_status", y="Share (%)", color=risk, color_discrete_map=COLORS, category_orders={risk:CATEGORIES}, custom_data=["Records"], title="Label composition within smoking groups", labels={"smoking_status":"Smoking status",risk:"Simulation label"}))
        a, b = st.columns(2)
        with a:
            comparison = selected[selected[risk].isin(["Lower", "Higher"])]
            metric = st.selectbox("Compare groups by", ["bmi", "cholesterol", "systolic_bp", "smoking_duration", "age"])
            if comparison.empty:
                st.info("No Lower or Higher records in this cohort; select broader filters.")
            else:
                show_chart(px.box(comparison, x=risk, y=metric, color=risk, color_discrete_map=COLORS, category_orders={risk:CATEGORIES}, title="Lower vs Higher simulation groups", labels={risk:"Simulation label",metric:metric.replace('_',' ').title()}))
        with b:
            show_chart(px.scatter(selected, x="age", y=score, color=risk, opacity=.5, color_discrete_map=COLORS, category_orders={risk:CATEGORIES}, title="Age and simulation score", labels={score:"Simulation score",risk:"Simulation label"}))
    st.subheader("Export this view")
    filters = f"age={ages}; smoking={statuses}; sex={sexes}; BMI={bmi}"
    c1, c2 = st.columns(2)
    c1.download_button("↓ Filtered synthetic records · CSV", selected.to_csv(index=False), "healthrisk_filtered.csv", "text/csv", use_container_width=True)
    c2.download_button("↓ Summary report · Markdown", summary_report(selected, organ, source, filters), "healthrisk_report.md", "text/markdown", use_container_width=True)

with data_tab:
    st.subheader("Explore the records")
    st.caption(f"{source} • {len(selected):,} filtered records. All risk labels are recomputed locally.")
    st.dataframe(selected, use_container_width=True, hide_index=True)
    st.download_button("Download 2,500-record sample CSV", demo_data().to_csv(index=False), "healthrisk_sample.csv", "text/csv")
    st.subheader("Data dictionary & upload contract")
    from healthrisk.data import RANGES
    dictionary = [
        ("patient_id", "Unique nonempty identifier", "Synthetic identifier"),
        ("sex", "Female / Male / Other", "Synthetic demographic category; no scoring weight"),
        ("smoking_status", "Never / Former / Current", "Categorical history; duration drives scoring"),
    ] + [(col, f"Numeric {lo}–{hi}", {"age":"Whole years", "smoking_duration":"Years; ≤age−18; Never=0", "bmi":"kg/m²", "cholesterol":"mg/dL, total", "systolic_bp":"mmHg", "diastolic_bp":"mmHg; below systolic"}[col]) for col,(lo,hi) in RANGES.items()]
    st.dataframe(pd.DataFrame(dictionary, columns=["Column", "Required values", "Meaning / units"]), hide_index=True, use_container_width=True)
    st.markdown("Upload requires these ten columns, UTF-8 CSV, no missing values, at most 100,000 rows and 10 MB. Extra columns are ignored. Generated outputs: each organ's `_score` and `_risk`; `risk_category` aliases `whole_body_risk`.")
    st.subheader("How labels are generated")
    st.markdown("Each input is normalized and clipped to [0,1]: age=(age−18)/72; duration=years/60; BMI=(BMI−18)/22; cholesterol=(cholesterol−120)/180; pressure=(systolic−90)/90. The score is 100 × the weighted sum, rounded to one decimal. **Lower ≤35; Moderate >35–60; Higher >60.** These are arbitrary thresholds, not clinical cutoffs or probabilities. Diastolic pressure, sex, and smoking status have no direct scoring weight.")
    st.dataframe(pd.DataFrame(ORGANS).T.rename_axis("Organ"), use_container_width=True)
    st.subheader("Limitations")
    st.markdown("The demo uses NumPy seed 42. Age and smoking status are sampled; duration is constrained by age. BMI is sampled independently; cholesterol and pressure depend partly on age and BMI. These designed relationships and score inputs create expected patterns. No clinical outcomes, cessation effects, confounder adjustment, or causal inference are modeled. Organ names are illustrative lenses rather than physiological models. Uploaded synthetic records may follow different distributions. Never upload real patient information or use this prototype for care decisions.")
    st.caption(DISCLAIMER)
