import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

# -------------------------- Page config & styling --------------------------
st.set_page_config(
    page_title="Synthetic Lethality Visualization",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main background and text */
    .stApp {
        background-color: #fafbfc;
    }
    
    /* Header styling - Light Blue Theme */
    .main-header {
        background: linear-gradient(135deg, #60a5fa 0%, #93c5fd 100%);
        padding: 2rem 1rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 15px 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white !important;
        margin-bottom: 0.5rem;
        font-weight: 700;
        font-size: 2.5rem;
    }
    
    .main-header .caption {
        color: #e0e7ff !important;
        font-size: 1.1rem;
        margin-bottom: 0.25rem;
    }
    
    .last-updated {
        color: #cbd5e1 !important;
        font-size: 0.9rem;
        font-style: italic;
    }
    
    /* Sidebar styling - Consistent across all pages */
    .stSidebar {
        background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
    }
    
    .stSidebar .stSelectbox label,
    .stSidebar .stRadio label,
    .stSidebar .stNumberInput label,
    .stSidebar .stSlider label,
    .stSidebar .stMultiSelect label {
        color: #1e40af !important;
        font-weight: 600;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    
    /* Section headers */
    .section-header {
        color: #1e40af;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
    }
    
    /* Download buttons - Consistent across all pages */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
    
    /* Tables */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Header section
st.markdown("""
<div class="main-header">
    <h1>📈 Visualizing Synthetic Lethality in Amplified Genes</h1>
    <div class="caption">Interactive volcano plots, heatmaps, and regression analysis of synthetic lethal interactions</div>
    <div class="last-updated">Last updated: August 19th, 2025</div>
</div>
""", unsafe_allow_html=True)

# Set professional color palette
plt.style.use('default')
sns.set_palette("Blues_r")
COLORS = {
    'primary': '#1e40af',
    'secondary': '#3b82f6', 
    'accent': '#60a5fa',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'light': '#f8fafc',
    'dark': '#1e293b'
}

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
        <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                    padding: 1.5rem; 
                    border-radius: 10px; 
                    border-left: 4px solid #0ea5e9; 
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); 
                    margin-bottom: 1.5rem;">
            <div style="color: #0c4a6e; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.75rem;">
                ℹ️ Context
            </div>
            <div style="color: #164e63; line-height: 1.6;">
                This view shows linear relationships between CNA and CRISPR dependency scores across a high-confidence subset of synthetic lethal gene pairs.<br><br>
                The following filters were applied from an initial screen of <b>521,374 gene pairs</b>:
                <ul style="margin: 0.75rem 0; padding-left: 1.25rem;">
                    <li style="margin-bottom: 0.5rem;"><b>FDR &lt; 0.05</b> → <b>3,476</b> hits</li>
                    <li style="margin-bottom: 0.5rem;"><b>Strong SL hits</b> (FDR &lt; 0.05 &amp; EffectSize &lt; 0) → <b>1,601</b> hits</li>
                    <li style="margin-bottom: 0.5rem;"><b>Selective hits</b> (PredictedEffect_CNA2 &gt; –1) → <b>1,075</b> hits</li>
                    <li style="margin-bottom: 0.5rem;"><b>Potent hits</b> (DeltaEffect_CNA6minusPred2 ≤ –0.2) → <b>735 hits</b></li>
                </ul>
                These <b>735 potent pairs</b> are shown in the dropdown below for regression visualization.
            </div>
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

# -------------------------- Footer --------------------------
st.markdown("---")

st.markdown("""
<div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); margin: 2rem -1rem -1rem -1rem; border-radius: 15px 15px 0 0;">
    <div style="font-size: 1.2rem; font-weight: 600; color: #1e40af; margin-bottom: 0.5rem;">
        🔬 BioSLATE Clinical Translation Platform
    </div>
    <div style="color: #64748b; font-size: 1rem;">
        Developed in collaboration with <strong style="color: #1e40af;">Breakthrough Cancer Research</strong>
    </div>
    <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem;">
        Advancing precision oncology through computational genomics and artificial intelligence
    </div>
</div>
""", unsafe_allow_html=True)