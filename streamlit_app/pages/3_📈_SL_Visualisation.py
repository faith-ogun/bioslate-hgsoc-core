import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO

# --- Page config ---
st.set_page_config(page_title="Synthetic Lethality Visualisation", layout="wide")
st.title("Visualising Synthetic Lethality in Amplified Genes")
st.caption("Last updated: June 2025")

# --- Load SL Results ---
@st.cache_data
def load_results():
    synthetic_id = "1jXmfqrqAhMcOR0ExlJytzHBJ3GsFQpWG"
    url = f"https://drive.google.com/uc?export=download&id={synthetic_id}"
    df = pd.read_csv(url)
    df["Biomarker_HGNC"] = df["Biomarker_HGNC"].astype(str).str.strip()
    df["TargetGene_HGNC"] = df["TargetGene_HGNC"].astype(str).str.strip()
    df["–log10(FDR)"] = -np.log10(df["FDR"] + 1e-10)
    df["SL_Hit"] = (df["EffectSize"] < 0) & (df["FDR"] < 0.05)
    df["OncogeneAddiction"] = df["Biomarker_HGNC"] == df["TargetGene_HGNC"]
    return df

# --- Load CRISPR & CNA data ---
@st.cache_data
def load_crispr_and_cna():
    crispr_id = "1VbQkrqJgqTIQuLMtluQWZMy9DKqaAoMu"
    cna_id = "18jtotzZSaFS-fbM4U8GDGHvkr44pRjTF"
    crispr_url = f"https://drive.google.com/uc?export=download&id={crispr_id}"
    cna_url = f"https://drive.google.com/uc?export=download&id={cna_id}"
    crispr = pd.read_csv(crispr_url, index_col=0).astype(str).astype(float)
    cna = pd.read_csv(cna_url, index_col=0).astype(str).astype(float)
    crispr.columns = crispr.columns.astype(str).str.strip()
    cna.columns = cna.columns.astype(str).str.strip()
    return crispr, cna

results_df = load_results()

# --- Select View ---
plot_option = st.radio(
    "Select Visualisation",
    ["Volcano Plot", "Heatmap", "Boxplot (TargetGene vs CNA Status)"]
)

# === Volcano Plot ===
if plot_option == "Volcano Plot":
    st.subheader("Volcano Plot: Effect Size vs FDR")

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

    # Volcano download
    buf_volcano = BytesIO()
    fig.savefig(buf_volcano, format="png", dpi=300)
    st.download_button(
        label="⬇️ Download Volcano Plot (.png)",
        data=buf_volcano.getvalue(),
        file_name="volcano_plot.png",
        mime="image/png"
    )

# === Heatmap ===
elif plot_option == "Heatmap":
    st.subheader("Heatmap of SL Hits")

    metric = st.selectbox(
        "Select Metric to Visualise",
        ["EffectSize", "–log10(FDR)", "MeanEffect_Amplified"]
    )

    filtered = results_df[
        (results_df["EffectSize"] < 0) & (results_df["FDR"] < 0.05)
    ].copy()

    all_biomarkers = sorted(filtered["Biomarker_HGNC"].unique())
    all_targets = sorted(filtered["TargetGene_HGNC"].unique())

    selected_biomarkers = st.multiselect("Filter by Biomarkers", all_biomarkers, default=all_biomarkers)
    selected_targets = st.multiselect("Filter by Target Genes", all_targets, default=all_targets)

    filtered = filtered[
        filtered["Biomarker_HGNC"].isin(selected_biomarkers) &
        filtered["TargetGene_HGNC"].isin(selected_targets)
    ]

    value_column = "–log10(FDR)" if metric == "–log10(FDR)" else metric
    heatmap_df = filtered.pivot(index="TargetGene_HGNC", columns="Biomarker_HGNC", values=value_column)

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

    csv = heatmap_df.to_csv().encode("utf-8")
    st.download_button(
        label="⬇️ Download Heatmap Matrix (.csv)",
        data=csv,
        file_name=f"heatmap_{metric.replace(' ', '_')}.csv",
        mime="text/csv"
    )

# === Boxplot View ===
elif plot_option == "Boxplot (TargetGene vs CNA Status)":
    st.subheader("Boxplot of Gene Effect by CNA Status")

    crispr_df, cna_df = load_crispr_and_cna()
    amp_threshold = 4.0
    min_group_size = 3
    effect_threshold = -0.6

    # Filter results
    valid_df = results_df[
        (results_df["FDR"] < 0.05) &
        (results_df["EffectSize"] < 0) &
        (results_df["MeanEffect_WT"] > -1)
    ].copy()

    # Restrict to target genes with at least one cell line with dependency < threshold
    valid_df = valid_df[valid_df["TargetGene"].isin([
        g for g in crispr_df.columns if (crispr_df[g] < effect_threshold).any()
    ])]

    # Define HGNC display pairs
    valid_df["pair_display"] = valid_df["Biomarker_HGNC"] + " → " + valid_df["TargetGene_HGNC"]
    pair_options = valid_df["pair_display"].unique()
    selected_display = st.selectbox("Select SL Gene Pair (Biomarker → Target):", options=pair_options)

    # Find matching row
    sel_row = valid_df[valid_df["pair_display"] == selected_display].iloc[0]
    biomarker = sel_row["Biomarker"]  # Entrez
    target = sel_row["TargetGene"]    # Entrez
    biomarker_hgnc = sel_row["Biomarker_HGNC"]
    target_hgnc = sel_row["TargetGene_HGNC"]

    if biomarker not in cna_df.columns or target not in crispr_df.columns:
        st.warning("Selected gene not found in CNA/CRISPR data.")
    else:
        cna_status = cna_df[biomarker].apply(lambda x: "Amplified" if x > amp_threshold else "WT")
        common = crispr_df.index.intersection(cna_status.index)
        df_plot = pd.DataFrame({
            "GeneEffect": crispr_df.loc[common, target],
            "CNA_Status": cna_status.loc[common]
        }).dropna()

        df_plot = df_plot[df_plot["CNA_Status"].isin(["Amplified", "WT"])]
        if df_plot["CNA_Status"].value_counts().min() < min_group_size:
            st.warning("Too few samples per group to show boxplot.")
        else:
            fig3, ax3 = plt.subplots(figsize=(6, 5))
            sns.boxplot(data=df_plot, x="CNA_Status", y="GeneEffect", hue="CNA_Status",
                        palette={"Amplified": "#e74c3c", "WT": "#3498db"}, legend=False)
            sns.stripplot(data=df_plot, x="CNA_Status", y="GeneEffect", color="black", alpha=0.4, jitter=True, size=4)
            ax3.set_title(f"{target_hgnc} Dependency in {biomarker_hgnc}-Amplified vs WT")
            ax3.set_ylabel("CRISPR Gene Effect Score")
            ax3.set_xlabel("CNA Status")
            ax3.axhline(0, linestyle="--", color="gray", linewidth=1)
            st.pyplot(fig3)

            buf3 = BytesIO()
            fig3.savefig(buf3, format="png", dpi=300)
            st.download_button(
                label="⬇️ Download Boxplot (.png)",
                data=buf3.getvalue(),
                file_name=f"boxplot_{biomarker_hgnc}_{target_hgnc}.png",
                mime="image/png"
            )
