import io
import urllib.request

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# Page setup
# ------------------------------------------------------------
st.set_page_config(
    page_title="Ariel Diabetes | BMMA110",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_URL = (
    "https://raw.githubusercontent.com/BabsMatt/Diabetes-Health-Indicators/"
    "master/diabetes_012_health_indicators_BRFSS2015.csv"
)

REQUIRED = [
    "Diabetes_012",
    "BMI",
    "MentHlth",
    "PhysHlth",
    "HighBP",
    "PhysActivity",
    "Fruits",
]

CONTINUOUS = ["BMI", "MentHlth", "PhysHlth"]

# ------------------------------------------------------------
# Visual styling
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Main page */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Hero */
    .hero {
        padding: 2rem 2.2rem;
        border-radius: 22px;
        background: linear-gradient(135deg, #0f766e 0%, #0e7490 100%);
        color: white;
        margin-bottom: 1.4rem;
        box-shadow: 0 10px 30px rgba(15, 118, 110, 0.18);
    }
    .hero-kicker {
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        opacity: 0.88;
        margin-bottom: 0.55rem;
    }
    .hero-title {
        font-size: 2.55rem;
        line-height: 1.08;
        font-weight: 800;
        margin: 0;
    }
    .hero-subtitle {
        font-size: 1.08rem;
        margin-top: 0.65rem;
        opacity: 0.94;
        max-width: 800px;
    }
    .hero-credit {
        margin-top: 1rem;
        font-size: 0.88rem;
        opacity: 0.82;
    }

    /* Section headings */
    .section-label {
        color: #0f766e;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.11em;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    .section-title {
        font-size: 1.55rem;
        font-weight: 750;
        margin-top: 0;
        margin-bottom: 0.35rem;
    }
    .section-text {
        color: #64748b;
        margin-bottom: 1.1rem;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        border: 1px solid rgba(100, 116, 139, 0.18);
        border-radius: 16px;
        padding: 1rem 1.1rem;
        background: rgba(255, 255, 255, 0.72);
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.05);
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 650;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-weight: 650;
    }

    /* Info cards */
    .info-card {
        border: 1px solid rgba(100, 116, 139, 0.18);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        background: rgba(248, 250, 252, 0.82);
        height: 100%;
    }
    .info-card h4 {
        margin-top: 0;
        margin-bottom: 0.45rem;
    }
    .info-card p {
        margin-bottom: 0;
        color: #475569;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(100, 116, 139, 0.12);
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.82rem;
        padding-top: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Data loading
# ------------------------------------------------------------
@st.cache_data

def load_public_data():
    return pd.read_csv(DATA_URL)


@st.cache_data

def load_uploaded_data(file_bytes):
    return pd.read_csv(io.BytesIO(file_bytes))


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">BMMA110 · Medical Mathematics 1 · Scenario 4</div>
        <div class="hero-title">🩺 Ariel Diabetes</div>
        <div class="hero-subtitle">
            An interactive exploration of the 2015 U.S. Diabetes Health Indicators dataset,
            with descriptive statistics and visualisations for selected health variables.
        </div>
        <div class="hero-credit">Built by Ariel Mutapay</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------
st.sidebar.markdown("## 🩺 Ariel Diabetes")
st.sidebar.caption("BMMA110 · Scenario 4")
st.sidebar.markdown("---")

st.sidebar.markdown("### Data source")
source = st.sidebar.radio(
    "Choose how to load the dataset:",
    ["Use the 2015 dataset automatically", "Upload a CSV"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About this app")
st.sidebar.info(
    "This dashboard presents the statistical analysis required for Scenario 4(C): "
    "measures of location and dispersion, categorical charts, and a box-and-whisker plot."
)
st.sidebar.markdown("**Selected variables**")
st.sidebar.write("Diabetes_012 · BMI · MentHlth · PhysHlth · HighBP · PhysActivity · Fruits")

try:
    if source == "Upload a CSV":
        uploaded = st.sidebar.file_uploader(
            "Upload a populated diabetes CSV", type=["csv"]
        )
        if uploaded is None:
            st.info("👈 Upload a populated CSV from the sidebar to begin.")
            st.stop()
        df = load_uploaded_data(uploaded.getvalue())
    else:
        with st.spinner("Loading the 2015 dataset..."):
            df = load_public_data()
except Exception as exc:
    st.error("The dataset could not be loaded.")
    st.exception(exc)
    st.stop()

missing = [column for column in REQUIRED if column not in df.columns]
if missing:
    st.error(f"Your dataset is missing: {', '.join(missing)}")
    st.stop()

for column in REQUIRED:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# ------------------------------------------------------------
# At-a-glance metrics
# ------------------------------------------------------------
st.markdown('<div class="section-label">At a glance</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">What is in the dataset?</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-text">A quick summary of the survey and the three continuous variables used in the analysis.</div>',
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("👥 Survey responses", f"{len(df):,}")
m2.metric("⚖️ Mean BMI", f"{df['BMI'].mean():.2f}")
m3.metric("🧠 Mean MentHlth", f"{df['MentHlth'].mean():.2f} days")
m4.metric("🏃 Mean PhysHlth", f"{df['PhysHlth'].mean():.2f} days")

st.success(f"Dataset loaded successfully · {len(df):,} survey responses · {df.shape[1]} variables")

# ------------------------------------------------------------
# Main navigation
# ------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📋 Overview",
        "📈 Location & Dispersion",
        "🥧 Categorical Charts",
        "📦 Box Plots",
    ]
)

# ------------------------------------------------------------
# Overview
# ------------------------------------------------------------
with tab1:
    st.markdown('<div class="section-label">Explore the data</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Dataset overview</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-text">Each row represents a survey respondent, while each column represents a measured or coded variable.</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1.25])

    with left:
        st.markdown(
            """
            <div class="info-card">
                <h4>🎯 What this dashboard examines</h4>
                <p>
                The analysis focuses on BMI, mental-health days, physical-health days,
                diabetes status, high blood pressure, physical activity and fruit consumption.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.dataframe(
            pd.DataFrame(
                {
                    "Variable": REQUIRED,
                    "Type / use": [
                        "Categorical outcome",
                        "Continuous numerical",
                        "Count (0–30 days)",
                        "Count (0–30 days)",
                        "Binary categorical",
                        "Binary categorical",
                        "Binary categorical",
                    ],
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    with right:
        st.markdown("**Preview of selected variables**")
        st.dataframe(df[REQUIRED].head(10), use_container_width=True, hide_index=True)
        st.info(
            "Diabetes_012 coding: 0 = no diabetes or diabetes only during pregnancy; "
            "1 = prediabetes; 2 = diabetes."
        )

# ------------------------------------------------------------
# Location & dispersion
# ------------------------------------------------------------
with tab2:
    st.markdown('<div class="section-label">Question 4(C)(i)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Measures of location and dispersion</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-text">Compare the centre and spread of BMI, MentHlth and PhysHlth.</div>',
        unsafe_allow_html=True,
    )

    selected = df[CONTINUOUS]
    summary = pd.DataFrame(index=CONTINUOUS)
    summary["Mean"] = selected.mean()
    summary["Median"] = selected.median()
    summary["Standard deviation"] = selected.std()
    summary["Minimum"] = selected.min()
    summary["Q1"] = selected.quantile(0.25)
    summary["Q3"] = selected.quantile(0.75)
    summary["IQR"] = summary["Q3"] - summary["Q1"]
    summary["Maximum"] = selected.max()
    summary["Range"] = summary["Maximum"] - summary["Minimum"]

    st.dataframe(summary.round(2), use_container_width=True)

    st.markdown("### 💡 Interpretation")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="info-card">
            <h4>⚖️ BMI</h4>
            <p>Mean = <b>{summary.loc['BMI','Mean']:.2f}</b>, median = <b>{summary.loc['BMI','Median']:.2f}</b>,
            SD = <b>{summary.loc['BMI','Standard deviation']:.2f}</b>, IQR = <b>{summary.loc['BMI','IQR']:.2f}</b>.
            The mean is above the median and the upper tail is long, indicating positive/right skewness.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="info-card">
            <h4>🧠 MentHlth</h4>
            <p>Mean = <b>{summary.loc['MentHlth','Mean']:.2f}</b> days, median = <b>{summary.loc['MentHlth','Median']:.2f}</b> days,
            SD = <b>{summary.loc['MentHlth','Standard deviation']:.2f}</b>. Most observations are concentrated near zero,
            with a long upper tail.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="info-card">
            <h4>🏃 PhysHlth</h4>
            <p>Mean = <b>{summary.loc['PhysHlth','Mean']:.2f}</b> days, median = <b>{summary.loc['PhysHlth','Median']:.2f}</b> days,
            SD = <b>{summary.loc['PhysHlth','Standard deviation']:.2f}</b>. Most observations are concentrated near zero,
            with a long upper tail.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    csv = summary.round(2).to_csv().encode("utf-8")
    st.download_button(
        "⬇️ Download statistics as CSV",
        data=csv,
        file_name="BMMA110_statistics.csv",
        mime="text/csv",
    )

# ------------------------------------------------------------
# Categorical charts
# ------------------------------------------------------------
with tab3:
    st.markdown('<div class="section-label">Question 4(C)(ii)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Categorical variables</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-text">Visualise diabetes status and selected binary health indicators.</div>',
        unsafe_allow_html=True,
    )

    labels = {
        0: "No diabetes / gestational only",
        1: "Prediabetes",
        2: "Diabetes",
    }
    diabetes_counts = df["Diabetes_012"].value_counts().sort_index()
    diabetes_counts = diabetes_counts[diabetes_counts.index.isin(labels.keys())]
    diabetes_labels = [labels.get(int(x), str(x)) for x in diabetes_counts.index]

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(6, 5.5))
        ax.pie(
            diabetes_counts.values,
            labels=diabetes_labels,
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        )
        ax.set_title("Distribution of Diabetes Status", pad=14, fontweight="bold")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.caption(
            "The sample is dominated by respondents coded as having no diabetes / gestational-only, "
            "followed by diabetes and then prediabetes."
        )

    with col2:
        binary = df[["HighBP", "PhysActivity", "Fruits"]].mean() * 100
        fig, ax = plt.subplots(figsize=(7, 5.5))
        binary.plot(kind="bar", ax=ax)
        ax.set_title("Prevalence of Selected Health Indicators", pad=14, fontweight="bold")
        ax.set_ylabel("Percentage (%)")
        ax.set_ylim(0, 100)
        ax.tick_params(axis="x", rotation=0)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.dataframe(
            binary.round(2).rename("Percentage (%)").to_frame(),
            use_container_width=True,
        )

    st.warning(
        "These percentages describe the survey sample. They do not, by themselves, show that one variable causes another."
    )

# ------------------------------------------------------------
# Box plots
# ------------------------------------------------------------
with tab4:
    st.markdown('<div class="section-label">Question 4(C)(iii)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Box-and-whisker plot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-text">Compare variability, medians and potential outliers across the three continuous variables.</div>',
        unsafe_allow_html=True,
    )

    fig, ax = plt.subplots(figsize=(10, 5.5))
    df[CONTINUOUS].plot(kind="box", ax=ax, patch_artist=True)
    ax.set_title("Spread and Outliers of Key Health Metrics", pad=14, fontweight="bold")
    ax.set_ylabel("Value / Days")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown("### 💡 What the plot shows")
    st.markdown(
        """
        - **BMI** has a wider central spread and many high-value outliers, consistent with right skewness.
        - **MentHlth** and **PhysHlth** both have medians at 0 and long upper tails.
        - The box plot shows that most respondents reported few or no poor-health days, while a smaller group reported substantially more days.
        """
    )

# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------
st.divider()
st.markdown(
    '<div class="footer">🩺 <b>Ariel Diabetes</b> · BMMA110 Scenario 4 · Built by Ariel Mutapay · Interactive presentation of the Python analysis</div>',
    unsafe_allow_html=True,
)
