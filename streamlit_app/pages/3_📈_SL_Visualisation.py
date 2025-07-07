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
    df = pd.read_csv("results/synthetic_lethality_screen_with_HGNC.csv")
    df["Biomarker_HGNC"] = df["Biomarker_HGNC"].astype(str).str.strip()
    df["TargetGene_HGNC"] = df["TargetGene_HGNC"].astype(str).str.strip()
    df["–log10(FDR)"] = -np.log10(df["FDR"] + 1e-10)
    df["SL_Hit"] = (df["EffectSize"] < 0) & (df["FDR"] < 0.05)
    df["OncogeneAddiction"] = df["Biomarker_HGNC"] == df["TargetGene_HGNC"]
    return df

# --- Load CRISPR & CNA data ---
@st.cache_data
def load_crispr_and_cna():
    crispr = pd.read_csv("results/depmap_crispr_gene_effect.csv", index_col=0).astype(float)
    cna = pd.read_csv("results/cna_depmap_hgsoc.csv", index_col=0).astype(float)
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
    ax.axhline(y=-np.log10(0.05), linestyle="--", color="gray")
    ax.axvline(x=0, linestyle="--", color="gray")
    ax.set_xlabel("Cohen's d (Effect Size)")
    ax.set_ylabel("–log₁₀(FDR)")
    ax.set_title("Volcano Plot: Synthetic Lethality in Amplified Biomarkers")
    ax.legend()
    st.pyplot(fig)

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300)
    st.download_button("⬇️ Download Volcano Plot (.png)", buf.getvalue(), "volcano_plot.png", "image/png")

# === Heatmap ===
elif plot_option == "Heatmap":
    st.subheader("Heatmap of SL Hits")
    metric = st.selectbox("Select Metric", ["EffectSize", "–log10(FDR)", "MeanEffect_Amplified"])

    filtered = results_df[(results_df["EffectSize"] < 0) & (results_df["FDR"] < 0.05)].copy()
    biomarker_opts = sorted(filtered["Biomarker_HGNC"].unique())
    target_opts = sorted(filtered["TargetGene_HGNC"].unique())

    selected_biomarkers = st.multiselect("Biomarkers", biomarker_opts, default=biomarker_opts)
    selected_targets = st.multiselect("Target Genes", target_opts, default=target_opts)

    filtered = filtered[
        filtered["Biomarker_HGNC"].isin(selected_biomarkers) &
        filtered["TargetGene_HGNC"].isin(selected_targets)
    ]

    value_column = "–log10(FDR)" if metric == "–log10(FDR)" else metric
    heatmap_df = filtered.pivot(index="TargetGene_HGNC", columns="Biomarker_HGNC", values=value_column)

    fig2, ax2 = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        heatmap_df.clip(-3, 0) if "EffectSize" in metric else heatmap_df,
        cmap="coolwarm" if "EffectSize" in metric else "YlGnBu",
        center=0 if "EffectSize" in metric else None,
        linewidths=0.5,
        linecolor="gray"
    )
    ax2.set_title(f"Heatmap: {metric}")
    st.pyplot(fig2)

    st.download_button(
        "⬇️ Download Heatmap (.csv)",
        heatmap_df.to_csv().encode("utf-8"),
        f"heatmap_{metric}.csv",
        "text/csv"
    )

# === Boxplot ===
elif plot_option == "Boxplot (TargetGene vs CNA Status)":
    st.subheader("Boxplot of Gene Effect by CNA Status")

    crispr_df, cna_df = load_crispr_and_cna()
    amp_threshold = 4.0
    min_group_size = 3
    effect_threshold = -0.6

    valid_df = results_df[
        (results_df["FDR"] < 0.05) &
        (results_df["EffectSize"] < 0) &
        (results_df["MeanEffect_WT"] > -1)
    ].copy()

    valid_df = valid_df[valid_df["TargetGene"].isin([
        g for g in crispr_df.columns if (crispr_df[g] < effect_threshold).any()
    ])]

    valid_df["pair"] = valid_df["Biomarker_HGNC"] + " → " + valid_df["TargetGene_HGNC"]
    selected_pair = st.selectbox("Select SL Gene Pair (HGNC)", options=valid_df["pair"].unique())

    sel = valid_df[valid_df["pair"] == selected_pair].iloc[0]
    biomarker_entrez = sel["Biomarker"]
    target_entrez = sel["TargetGene"]
    biomarker_hgnc = sel["Biomarker_HGNC"]
    target_hgnc = sel["TargetGene_HGNC"]

    if biomarker_entrez not in cna_df.columns or target_entrez not in crispr_df.columns:
        st.warning("Selected genes not found in data.")
    else:
        status = cna_df[biomarker_entrez].apply(lambda x: "Amplified" if x > amp_threshold else "WT")
        common = crispr_df.index.intersection(status.index)

        df_plot = pd.DataFrame({
            "GeneEffect": crispr_df.loc[common, target_entrez],
            "CNA_Status": status.loc[common]
        }).dropna()

        df_plot = df_plot[df_plot["CNA_Status"].isin(["Amplified", "WT"])]
        if df_plot["CNA_Status"].value_counts().min() < min_group_size:
            st.warning("Too few samples per group.")
        else:
            fig3, ax3 = plt.subplots(figsize=(6, 5))
            sns.boxplot(data=df_plot, x="CNA_Status", y="GeneEffect", hue="CNA_Status",
                        palette={"Amplified": "#e74c3c", "WT": "#3498db"}, legend=False)
            sns.stripplot(data=df_plot, x="CNA_Status", y="GeneEffect", color="black", alpha=0.4, jitter=True, size=4)
            ax3.set_title(f"{target_hgnc} Dependency in {biomarker_hgnc}-Amplified vs WT")
            ax3.set_ylabel("CRISPR Gene Effect Score")
            ax3.set_xlabel("CNA Status")
            ax3.axhline(0, linestyle="--", color="gray")
            st.pyplot(fig3)

            buf3 = BytesIO()
            fig3.savefig(buf3, format="png", dpi=300)
            st.download_button(
                "⬇️ Download Boxplot (.png)",
                buf3.getvalue(),
                f"boxplot_{biomarker_hgnc}_{target_hgnc}.png",
                "image/png"
            )
