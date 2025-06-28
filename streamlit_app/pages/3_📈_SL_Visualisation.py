import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# --- Page config ---
st.set_page_config(page_title="Synthetic Lethality Visualisation", layout="wide")
st.title("🧬 Visualising Synthetic Lethality in Amplified Genes")
st.caption("Last updated: June 2025")

# --- Load Data ---
@st.cache_data
def load_data():
    file_id = "1Wy7rWBtLYDxjEFc61DTdfcTlD_UwMGdB"  # file ID
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    df = pd.read_csv(url)
    df["–log10(FDR)"] = -np.log10(df["FDR"] + 1e-10)
    df["SL_Hit"] = (df["EffectSize"] < -0) & (df["FDR"] < 0.05)
    df["OncogeneAddiction"] = df["Biomarker"] == df["TargetGene"]
    return df

results_df = load_data()

# --- Tabs ---
tab1, tab2 = st.tabs(["📈 Volcano Plot", "🔬 Heatmap"])

# === 📈 Volcano Plot ===
with tab1:
    st.subheader("📈 Volcano Plot: Effect Size vs FDR")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=results_df,
        x="EffectSize",
        y="–log10(FDR)",
        hue="SL_Hit",
        size="OncogeneAddiction",
        sizes=(20, 200),
        palette={True: "#e74c3c", False: "#bdc3c7"},
        alpha=0.7,
        edgecolor="black"
    )
    ax.axhline(y=-np.log10(0.05), linestyle="--", color="gray", label="FDR = 0.05")
    ax.axvline(x=0, linestyle="--", color="gray", label="Effect Size = 0")
    ax.set_xlabel("Cohen's d (Effect Size)")
    ax.set_ylabel("–log₁₀(FDR)")
    ax.set_title("Volcano Plot: Synthetic Lethality in Amplified Biomarkers")
    ax.legend()
    st.pyplot(fig)

# === 🔬 Heatmap ===
with tab2:
    st.subheader("🔬 Heatmap of SL Hits")

    metric = st.selectbox(
        "Select Metric to Visualise",
        ["EffectSize", "–log10(FDR)", "MeanEffect_Amplified"]
    )

    # --- Filter SL hits ---
    filtered = results_df[
        (results_df["EffectSize"] < 0) & (results_df["FDR"] < 0.05)
    ].copy()

    all_biomarkers = sorted(filtered["Biomarker"].unique())
    all_targets = sorted(filtered["TargetGene"].unique())

    selected_biomarkers = st.multiselect(
        "Filter by Biomarkers",
        options=all_biomarkers,
        default=all_biomarkers
    )

    selected_targets = st.multiselect(
        "Filter by Target Genes",
        options=all_targets,
        default=all_targets
    )

    filtered = filtered[
        filtered["Biomarker"].isin(selected_biomarkers) &
        filtered["TargetGene"].isin(selected_targets)
    ]

    value_column = "–log10(FDR)" if metric == "–log10(FDR)" else metric
    heatmap_df = filtered.pivot(index="TargetGene", columns="Biomarker", values=value_column)

    st.markdown(f"Showing: **{metric}** for hits with EffectSize < 0 and FDR < 0.05")

    fig2, ax2 = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        heatmap_df.clip(-3, 0) if "EffectSize" in metric else heatmap_df,
        cmap="coolwarm" if "EffectSize" in metric else "YlGnBu",
        center=0 if "EffectSize" in metric else None,
        linewidths=0.5,
        linecolor="gray"
    )
    ax2.set_title(f"Heatmap: {metric} across SL hits")
    ax2.set_xlabel("Amplified Biomarkers")
    ax2.set_ylabel("Target Genes")
    st.pyplot(fig2)

    # --- Download Button ---
    csv = heatmap_df.to_csv().encode("utf-8")
    st.download_button(
        label="⬇️ Download Heatmap Matrix (.csv)",
        data=csv,
        file_name=f"heatmap_{metric.replace(' ', '_')}.csv",
        mime="text/csv"
    )
