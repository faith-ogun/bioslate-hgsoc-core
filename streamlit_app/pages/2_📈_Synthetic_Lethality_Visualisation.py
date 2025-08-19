import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

# --- Page config ---
st.set_page_config(page_title="Synthetic Lethality Visualisation", layout="wide")
st.title("Visualising Synthetic Lethality in Amplified Genes")
st.caption("Last updated: August 19th 2025")

# --- Sidebar options ---
st.sidebar.title("Visualisation Options")
plot_option = st.sidebar.radio(
    "Choose a view:",
    ["Volcano Plot", "Heatmap", "Regression (TargetGene ~ CNA)"]
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

    potent_hits = pd.read_csv("streamlit_app/data/potent_synthetic_lethal_hits_with_HGNC_ppi_validated.csv")
    potent_hits["Biomarker_HGNC"] = potent_hits["Biomarker_HGNC"].astype(str).str.strip()
    potent_hits["TargetGene_HGNC"] = potent_hits["TargetGene_HGNC"].astype(str).str.strip()

    amp_biomarkers = pd.read_csv("streamlit_app/data/cross_val_amp_sig_genes.csv")
    amp_set = set(amp_biomarkers["Gene"].astype(str).str.strip())

    crispr_url = "https://drive.google.com/uc?export=download&id=1VbQkrqJgqTIQuLMtluQWZMy9DKqaAoMu"
    cna_url = "https://drive.google.com/uc?export=download&id=18jtotzZSaFS-fbM4U8GDGHvkr44pRjTF"
    crispr_df = pd.read_csv(crispr_url, index_col=0).astype(str).astype(float)
    cna_df = pd.read_csv(cna_url, index_col=0).astype(str).astype(float)
    crispr_df.columns = crispr_df.columns.astype(str).str.strip()
    cna_df.columns = cna_df.columns.astype(str).str.strip()

    return full_screen, potent_hits, amp_set, crispr_df, cna_df

full_screen_df, potent_hits, amp_biomarkers, crispr_df, cna_df = load_all_data()

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

    # Metric selection
    metric = st.selectbox(
        "Select Metric to Visualise",
        ["EffectSize", "–log10(FDR)"]
    )

    # Pre-filter
    filtered = full_screen_df[
        (full_screen_df["EffectSize"] < 0) & (full_screen_df["FDR"] < 0.05)
    ].copy()

    all_biomarkers = sorted(filtered["Biomarker_HGNC"].unique())
    all_targets = sorted(filtered["TargetGene_HGNC"].unique())

    # Set max allowed
    max_biomarkers = 50
    max_targets = 50

    # Selection UI with defaults
    selected_biomarkers = st.multiselect(
        f"Filter by Biomarkers (max {max_biomarkers})",
        all_biomarkers,
        default=all_biomarkers[:max_biomarkers]
    )
    selected_targets = st.multiselect(
        f"Filter by Target Genes (max {max_targets})",
        all_targets,
        default=all_targets[:max_targets]
    )

    # Enforce selection limits
    if len(selected_biomarkers) > max_biomarkers or len(selected_targets) > max_targets:
        st.warning(f"Please select ≤ {max_biomarkers} biomarkers and ≤ {max_targets} target genes.")
        st.stop()

    # Apply selection filter
    filtered = filtered[
        filtered["Biomarker_HGNC"].isin(selected_biomarkers) &
        filtered["TargetGene_HGNC"].isin(selected_targets)
    ]

    # Pivot matrix
    value_column = "–log10(FDR)" if metric == "–log10(FDR)" else metric
    heatmap_df = filtered.pivot(index="TargetGene_HGNC", columns="Biomarker_HGNC", values=value_column)

    st.markdown(f"Showing: **{metric}** for hits with EffectSize < 0 and FDR < 0.05")

    # Plot heatmap
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

    # CSV export
    csv = heatmap_df.to_csv().encode("utf-8")
    st.download_button(
        label="⬇️ Download Heatmap Matrix (.csv)",
        data=csv,
        file_name=f"heatmap_{metric.replace(' ', '_')}.csv",
        mime="text/csv"
    )


# === Regression ===
elif plot_option == "Regression (TargetGene ~ CNA)":
    st.subheader("Regression Plot: CNA vs Gene Dependency")

    st.markdown(
    f"""
    <div style="background-color:#9ecae1; padding:12px; border-radius:6px;">
        ℹ️ <b>Context:</b> This view shows linear relationships between CNA and CRISPR dependency scores across a high-confidence subset of synthetic lethal gene pairs.<br><br>
        The following filters were applied from an initial screen of <b>521,374 gene pairs</b>:
        <ul>
            <li><b>FDR &lt; 0.05</b> → <b>3476</b> hits</li>
            <li><b>Strong SL hits</b> (FDR &lt; 0.05 &amp; EffectSize &lt; 0) → <b>1601</b> hits</li>
            <li><b>Selective hits</b> (PredictedEffect_CNA2 &gt; –1) → <b>1075</b> hits</li>
            <li><b>Potent hits</b> (DeltaEffect_CNA6minusPred2 ≤ –0.2) → <b>735 hits</b></li>
        </ul>
        These 735 potent pairs are shown in the dropdown below for regression visualisation.
    </div>
    """,
    unsafe_allow_html=True
    )

    potent_hits_df = potent_hits.copy()

    potent_hits_df["pair_display"] = potent_hits_df["Biomarker_HGNC"] + " → " + potent_hits_df["TargetGene_HGNC"]
    selected_display = st.selectbox("Select SL Gene Pair (Biomarker → Target):", sorted(potent_hits_df["pair_display"].unique()))

    row = potent_hits_df[potent_hits_df["pair_display"] == selected_display].iloc[0]
    biomarker = str(row["Biomarker"])
    target = str(row["TargetGene"])
    biomarker_hgnc = row["Biomarker_HGNC"]
    target_hgnc = row["TargetGene_HGNC"]

    if biomarker not in cna_df.columns or target not in crispr_df.columns:
        st.warning("CNA or CRISPR data not found for this pair.")
        st.stop()

    x = cna_df[biomarker].dropna()
    y = crispr_df[target].dropna()
    common = x.index.intersection(y.index)

    if len(common) < 3:
        st.warning("Too few overlapping cell lines to compute regression.")
        st.stop()

    r, p = pearsonr(x[common], y[common])

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.regplot(
        x=x[common],
        y=y[common],
        scatter_kws={"s": 50, "alpha": 0.8, "color": "#3498db"},
        line_kws={"color": "black", "linewidth": 1.5},
        ax=ax
    )
    ax.set_xlabel(f"{biomarker_hgnc} CNA", fontsize=11)
    ax.set_ylabel(f"{target_hgnc} Dependency Score", fontsize=11)
    ax.set_title(f"{biomarker_hgnc} → {target_hgnc}\nPearson r = {r:.2f}, p = {p:.4f}", fontsize=12)
    ax.axhline(0, linestyle="--", color="gray", linewidth=1)
    st.pyplot(fig)

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300)
    st.download_button(
        label="⬇️ Download Regression Plot (.png)",
        data=buf.getvalue(),
        file_name=f"regression_{biomarker_hgnc}_{target_hgnc}.png",
        mime="image/png"
    )
