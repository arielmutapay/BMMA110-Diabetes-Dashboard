
import io
import urllib.request

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="BMMA110 Diabetes Health Indicators",
    page_icon="🩺",
    layout="wide",
)

DATA_URL = (
    "https://raw.githubusercontent.com/BabsMatt/Diabetes-Health-Indicators/"
    "master/diabetes_012_health_indicators_BRFSS2015.csv"
)

st.title("🩺 Diabetes Health Indicators Dashboard")
st.caption("BMMA110 – Medical Mathematics 1 | Scenario 4")

st.markdown(
    """
    This interactive dashboard analyses the 2015 BRFSS Diabetes Health
    Indicators dataset used for Scenario 4. It provides descriptive statistics
    and the visualisations required for Question 4(C).
    """
)

@st.cache_data
def load_public_data():
    return pd.read_csv(DATA_URL)

@st.cache_data
def load_uploaded_data(file_bytes):
    return pd.read_csv(io.BytesIO(file_bytes))

# Sidebar
st.sidebar.header("Data")
source = st.sidebar.radio(
    "Choose data source:",
    ["Use the 2015 dataset automatically", "Upload a CSV"],
)

try:
    if source == "Upload a CSV":
        uploaded = st.sidebar.file_uploader("Upload the populated CSV", type=["csv"])
        if uploaded is None:
            st.info("Upload a populated diabetes_012_health_indicators_BRFSS2015.csv file to begin.")
            st.stop()
        df = load_uploaded_data(uploaded.getvalue())
    else:
        with st.spinner("Loading the 2015 dataset..."):
            df = load_public_data()
except Exception as e:
    st.error("The dataset could not be loaded.")
    st.exception(e)
    st.stop()

required = ["Diabetes_012", "BMI", "MentHlth", "PhysHlth", "HighBP", "PhysActivity", "Fruits"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"Your dataset is missing these required columns: {', '.join(missing)}")
    st.stop()

# Make a clean numeric copy for analysis
for col in required:
    df[col] = pd.to_numeric(df[col], errors="coerce")

st.success(f"Dataset loaded successfully: {len(df):,} survey responses and {df.shape[1]} columns.")

# Top metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Survey responses", f"{len(df):,}")
c2.metric("BMI mean", f"{df['BMI'].mean():.2f}")
c3.metric("MentHlth mean", f"{df['MentHlth'].mean():.2f}")
c4.metric("PhysHlth mean", f"{df['PhysHlth'].mean():.2f}")

tab1, tab2, tab3, tab4 = st.tabs(
    ["📋 Overview", "📈 Location & Dispersion", "🥧 Categorical Charts", "📦 Box Plots"]
)

with tab1:
    st.subheader("Dataset overview")
    st.write("Each row represents a survey respondent and each column represents a variable.")

    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Selected variables**")
        st.dataframe(
            pd.DataFrame({
                "Variable": required,
                "Type / use": [
                    "Categorical outcome",
                    "Continuous numerical",
                    "Count (0–30 days)",
                    "Count (0–30 days)",
                    "Binary categorical",
                    "Binary categorical",
                    "Binary categorical",
                ],
            }),
            use_container_width=True,
            hide_index=True,
        )
    with col_b:
        st.write("**First five rows**")
        st.dataframe(df[required].head(), use_container_width=True)

    st.info(
        "Diabetes_012 coding: 0 = no diabetes or diabetes only during pregnancy; "
        "1 = prediabetes; 2 = diabetes."
    )

with tab2:
    st.subheader("Question 4(C)(i): Measures of location and dispersion")

    continuous = ["BMI", "MentHlth", "PhysHlth"]
    summary = pd.DataFrame(index=continuous)
    selected = df[continuous]

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

    st.markdown("### Interpretation")
    st.write(
        f"**BMI:** mean = {summary.loc['BMI','Mean']:.2f}, median = "
        f"{summary.loc['BMI','Median']:.2f}, SD = {summary.loc['BMI','Standard deviation']:.2f}, "
        f"IQR = {summary.loc['BMI','IQR']:.2f}, range = {summary.loc['BMI','Range']:.2f}. "
        "The mean is above the median and the upper tail is long, indicating positive/right skewness."
    )
    st.write(
        f"**MentHlth:** mean = {summary.loc['MentHlth','Mean']:.2f} days, median = "
        f"{summary.loc['MentHlth','Median']:.2f} days, SD = {summary.loc['MentHlth','Standard deviation']:.2f}, "
        f"IQR = {summary.loc['MentHlth','IQR']:.2f} days. Most observations are concentrated near zero, "
        "with a long upper tail."
    )
    st.write(
        f"**PhysHlth:** mean = {summary.loc['PhysHlth','Mean']:.2f} days, median = "
        f"{summary.loc['PhysHlth','Median']:.2f} days, SD = {summary.loc['PhysHlth','Standard deviation']:.2f}, "
        f"IQR = {summary.loc['PhysHlth','IQR']:.2f} days. Most observations are concentrated near zero, "
        "with a long upper tail."
    )

    csv = summary.round(2).to_csv().encode("utf-8")
    st.download_button(
        "⬇️ Download statistics as CSV",
        data=csv,
        file_name="BMMA110_statistics.csv",
        mime="text/csv",
    )

with tab3:
    st.subheader("Question 4(C)(ii): Categorical variables")

    # Diabetes pie chart
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
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(
            diabetes_counts.values,
            labels=diabetes_labels,
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        )
        ax.set_title("Distribution of Diabetes Status")
        st.pyplot(fig)
        plt.close(fig)

        st.write(
            "The chart shows that the sample is dominated by respondents with no "
            "diabetes/gestational-only coding, followed by diabetes and then prediabetes."
        )

    with col2:
        binary = df[["HighBP", "PhysActivity", "Fruits"]].mean() * 100
        fig, ax = plt.subplots(figsize=(7, 5))
        binary.plot(kind="bar", ax=ax)
        ax.set_title("Prevalence of Selected Health Indicators")
        ax.set_ylabel("Percentage (%)")
        ax.set_ylim(0, 100)
        ax.tick_params(axis="x", rotation=0)
        st.pyplot(fig)
        plt.close(fig)

        st.dataframe(
            binary.round(2).rename("Percentage (%)").to_frame(),
            use_container_width=True,
        )

    st.warning(
        "These percentages describe the survey sample. They do not, by themselves, "
        "show that one variable causes another."
    )

with tab4:
    st.subheader("Question 4(C)(iii): Box-and-whisker plot")

    fig, ax = plt.subplots(figsize=(9, 5))
    df[["BMI", "MentHlth", "PhysHlth"]].plot(
        kind="box", ax=ax, patch_artist=True
    )
    ax.set_title("Spread and Outliers of Key Health Metrics")
    ax.set_ylabel("Value / Days")
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("### Interpretation")
    st.write(
        "BMI shows a wider central spread and many high-value outliers. "
        "MentHlth and PhysHlth both have medians at 0 and long upper tails, "
        "indicating that most respondents reported few or no poor-health days "
        "while a smaller group reported substantially more days."
    )

st.divider()
st.caption("BMMA110 Scenario 4 • Built as an interactive presentation of the Python analysis.")
