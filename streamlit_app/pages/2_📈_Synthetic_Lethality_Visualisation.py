import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

# --- Page config ---
st.set_page_config(page_title="Synthetic Lethality Visualisation", layout="wide")
st.title("Visualising Synthetic Lethality in Amplified Genes")
st.caption("Last updated: August 1st 2025")

# --- Sidebar options ---
st.sidebar.title("Visualisation Options")
plot_option = st.sidebar.radio(
    "Choose a view:",
    ["Volcano Plot", "Heatmap", "Boxplot (TargetGene vs CNA Status)"]
)

# --- Load all shared data in one go ---
@st.cache_data(show_spinner=False)
def load_all_data():
    full_screen = pd.read_csv("streamlit_app/data/synthetic_lethality_screen_with_HGNC.csv")
    full_screen["Biomarker_HGNC"] = full_screen["Biomarker_HGNC"].astype(str).str.strip()
    full_screen["TargetGene_HGNC"] = full_screen["TargetGene_HGNC"].astype(str).str.strip()
    full_screen["–log10(FDR)"] = -np.log10(full_screen["FDR"] + 1e-10)
    full_screen["SL_Hit"] = (full_screen["EffectSize"] < 0) & (full_screen["FDR"] < 0.1)
    full_screen["OncogeneAddiction"] = full_screen["Biomarker_HGNC"] == full_screen["TargetGene_HGNC"]

    selective_hits = pd.read_csv("streamlit_app/data/potent_synthetic_lethal_hits_with_HGNC.csv")
    selective_hits["Biomarker_HGNC"] = selective_hits["Biomarker_HGNC"].astype(str).str.strip()
    selective_hits["TargetGene_HGNC"] = selective_hits["TargetGene_HGNC"].astype(str).str.strip()

    amp_biomarkers = pd.read_csv("streamlit_app/data/cross_val_amp_sig_genes.csv")
    amp_set = set(amp_biomarkers["Gene"].astype(str).str.strip())

    crispr_url = "https://drive.google.com/uc?export=download&id=1VbQkrqJgqTIQuLMtluQWZMy9DKqaAoMu"
    cna_url = "https://drive.google.com/uc?export=download&id=18jtotzZSaFS-fbM4U8GDGHvkr44pRjTF"
    crispr_df = pd.read_csv(crispr_url, index_col=0).astype(str).astype(float)
    cna_df = pd.read_csv(cna_url, index_col=0).astype(str).astype(float)
    crispr_df.columns = crispr_df.columns.astype(str).str.strip()
    cna_df.columns = cna_df.columns.astype(str).str.strip()

    return full_screen, selective_hits, amp_set, crispr_df, cna_df

full_screen_df, selective_hits_df, amp_biomarkers, crispr_df, cna_df = load_all_data()

# === Volcano Plot ===
if plot_option == "Volcano Plot":
    st.subheader("Volcano Plot: Effect Size vs FDR")
    
    image = Image.open("streamlit_app/assets/volcano_plot_static.png")
    st.image(image, caption="Volcano Plot: Synthetic Lethality in Amplified Biomarkers", use_container_width=True)

    with open("streamlit_app/assets/volcano_plot_static.png", "rb") as f:
        st.download_button(
            label="⬇️ Download Volcano Plot (.png)",
            data=f,
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
    filtered = full_screen_df[
        (full_screen_df["EffectSize"] < 0) & (full_screen_df["FDR"] < 0.1)
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

# === Boxplot ===
elif plot_option == "Boxplot (TargetGene vs CNA Status)":
    st.subheader("Boxplot of Gene Effect by CNA Status")

    st.markdown(
    """
    <div style="background-color:#eaf4fb; padding:12px; border-radius:6px;">
        ℹ️ <b>Context:</b> This view shows the most selective synthetic lethal interactions identified from a large-scale screen.
        We initially tested <b>1,486,950 gene pairs</b> and applied the following filters:
        <ul>
            <li><b>P-value &lt; 0.05</b> → 81,451 hits</li>
            <li><b>FDR &lt; 0.05</b> → 22 hits</li>
            <li><b>Strong SL hits</b> (FDR &lt; 0.1 &amp; EffectSize &lt; 0) → 20 hits</li>
            <li><b>Selective hits</b> (WT MeanEffect &gt; -1 to exclude pan-essential genes) → <b>12 hits</b></li>
        </ul>
        These 12 high-confidence pairs are shown in the dropdown below for CRISPR-CNA boxplot comparison.
    </div>
    """,
    unsafe_allow_html=True
    )

    amp_threshold = 4.0
    min_group_size = 3
    effect_threshold = -0.6  # fixed

    selective_hits_df["pair_display"] = selective_hits_df["Biomarker_HGNC"] + " → " + selective_hits_df["TargetGene_HGNC"]
    selected_display = st.selectbox("Select SL Gene Pair (Biomarker → Target):", options=sorted(selective_hits_df["pair_display"].unique()))

    row = selective_hits_df[selective_hits_df["pair_display"] == selected_display].iloc[0]
    biomarker = str(row["Biomarker"])
    target = str(row["TargetGene"])
    biomarker_hgnc = row["Biomarker_HGNC"]
    target_hgnc = row["TargetGene_HGNC"]

    if biomarker not in cna_df.columns:
        st.warning(f"CNA data for biomarker {biomarker} not found.")
        st.stop()
    if target not in crispr_df.columns:
        st.warning(f"CRISPR data for target {target} not found.")
        st.stop()

    cna_status = cna_df[biomarker].apply(lambda x: "Amplified" if x > amp_threshold else "WT")
    common = crispr_df.index.intersection(cna_status.index)
    gene_effect = crispr_df.loc[common, target]
    cna_status = cna_status.loc[common]

    df_plot = pd.DataFrame({
        "GeneEffect": gene_effect,
        "CNA_Status": cna_status
    }).dropna()
    df_plot = df_plot[df_plot["CNA_Status"].isin(["Amplified", "WT"])]

    if df_plot["CNA_Status"].value_counts().min() < min_group_size:
        st.warning("Too few samples per group to show boxplot.")
        st.stop()

    fig3, ax3 = plt.subplots(figsize=(6, 5))
    sns.boxplot(
        data=df_plot, x="CNA_Status", y="GeneEffect", hue="CNA_Status",
        palette={"Amplified": "#e74c3c", "WT": "#3498db"},
        order=["Amplified", "WT"], legend=False
    )
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
