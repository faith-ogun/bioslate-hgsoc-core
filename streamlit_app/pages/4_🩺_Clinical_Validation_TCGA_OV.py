# 7_Clinical_Validation_TCGA_OV.py
import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

# -------------------------- Page config & styling --------------------------
st.set_page_config(
    page_title="Clinical Validation | TCGA-OV",
    page_icon="🔬",
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
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
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
    
    /* Sidebar styling */
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
    
    /* Download buttons */
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
    <h1>🔬 Clinical Validation — TCGA-OV</h1>
    <div class="caption">Comprehensive survival analysis with Cox models, volcano plots, forest plots, and Kaplan-Meier curves</div>
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

# -------------------------- Utilities --------------------------
@st.cache_data(show_spinner=False)
def load_cox_results():
    """Load Cox regression results with improved error handling"""
    os_path = "streamlit_app/data/biomarker_cox_results_os_with_HGNC.csv"
    pfs_path = "streamlit_app/data/biomarker_cox_results_pfs_with_HGNC.csv"
    
    try:
        os_df = pd.read_csv(os_path) if os.path.exists(os_path) else pd.DataFrame()
        pfs_df = pd.read_csv(pfs_path) if os.path.exists(pfs_path) else pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading Cox results: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()
    
    # Normalize expected columns
    for df in (os_df, pfs_df):
        if not df.empty:
            # Backward compatibility for column names
            rename_map = {
                "Adjusted p": "Adjusted_p",
                "Adjusted p-value": "Adjusted_p", 
                "Adjusted HR": "Adjusted_HR",
                "Adjusted CI lower": "Adjusted_CI_lower",
                "Adjusted CI upper": "Adjusted_CI_upper",
                "Amp freq": "Amp_frequency",
                "Biomarker_HGNC_Symbol": "Biomarker_HGNC",
            }
            df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)
            
            # Ensure required cols exist
            required = ["Biomarker", "Biomarker_HGNC", "Adjusted_HR", "Adjusted_p",
                       "Adjusted_CI_lower", "Adjusted_CI_upper", "N_patients", "Amp_frequency"]
            for c in required:
                if c not in df.columns:
                    df[c] = np.nan
            
            # Add FDR column if missing
            if "Adjusted_FDR" not in df.columns:
                df["Adjusted_FDR"] = np.nan
                
            # Coerce types
            for c in ["Adjusted_HR", "Adjusted_p", "Adjusted_CI_lower", "Adjusted_CI_upper",
                     "N_patients", "Amp_frequency", "Adjusted_FDR"]:
                df[c] = pd.to_numeric(df[c], errors="coerce")
                
            # Provide HGNC fallback
            if df["Biomarker_HGNC"].isna().all():
                df["Biomarker_HGNC"] = df["Biomarker"].astype(str)
                
    return os_df, pfs_df

@st.cache_data(show_spinner=False)
def load_km_inputs():
    """Load Kaplan-Meier input data with improved error handling"""
    clinical_path = "streamlit_app/data/clinical_matched.csv"
    amp_path = "streamlit_app/data/biomarker_amplifications_matched.csv"
    hgnc_map_path = "streamlit_app/data/gene_with_protein_product.txt"

    try:
        clinical_df = pd.read_csv(clinical_path) if os.path.exists(clinical_path) else pd.DataFrame()
        amp_df = pd.read_csv(amp_path, index_col=0) if os.path.exists(amp_path) else pd.DataFrame()
        
        if not amp_df.empty:
            amp_df.index = amp_df.index.astype(str)
            amp_df.columns = [c.replace("-", "_") for c in amp_df.columns]

        if os.path.exists(hgnc_map_path):
            hgnc_df = pd.read_csv(hgnc_map_path, sep="\t")
            symbol_to_entrez = dict(zip(hgnc_df["symbol"], hgnc_df["entrez_id"].astype(str)))
            entrez_to_symbol = dict(zip(hgnc_df["entrez_id"].astype(str), hgnc_df["symbol"]))
        else:
            symbol_to_entrez, entrez_to_symbol = {}, {}
            
    except Exception as e:
        st.error(f"Error loading KM input data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), {}, {}

    return clinical_df, amp_df, symbol_to_entrez, entrez_to_symbol

def safe_log2(x):
    """Safe log2 calculation with error handling"""
    try:
        return math.log2(x) if x > 0 else np.nan
    except Exception:
        return np.nan

def volcano(ax, df, p_col="Adjusted_p", hr_col="Adjusted_HR", fdr_col="Adjusted_FDR",
           p_thresh=0.05, fdr_thresh=0.05, title="Volcano (OS)"):
    """Create professional volcano plot with blues color scheme"""
    plot_df = df.copy()
    plot_df["log2HR"] = plot_df[hr_col].apply(safe_log2)
    plot_df["neglog10p"] = -np.log10(plot_df[p_col].replace(0, np.nan))

    # Create significance categories for coloring
    plot_df["significant"] = "Non-significant"
    if fdr_col in plot_df.columns:
        plot_df.loc[plot_df[fdr_col] < fdr_thresh, "significant"] = "FDR significant"
    plot_df.loc[(plot_df[p_col] < p_thresh) & (plot_df["significant"] == "Non-significant"), "significant"] = "Nominally significant"

    # Color mapping
    color_map = {
        "Non-significant": "#94a3b8",
        "Nominally significant": "#3b82f6", 
        "FDR significant": "#1e40af"
    }
    
    # Plot points by significance
    for sig_type, color in color_map.items():
        mask = plot_df["significant"] == sig_type
        if mask.any():
            ax.scatter(plot_df.loc[mask, "log2HR"], plot_df.loc[mask, "neglog10p"], 
                      s=35, alpha=0.8, c=color, label=sig_type, edgecolors='white', linewidth=0.5)

    # Reference lines with professional styling
    ax.axhline(-math.log10(p_thresh), linestyle="--", linewidth=1.5, alpha=0.6, color=COLORS['primary'])
    ax.axvline(math.log2(1.25), linestyle="--", linewidth=1, alpha=0.4, color=COLORS['dark'])
    ax.axvline(math.log2(0.8), linestyle="--", linewidth=1, alpha=0.4, color=COLORS['dark'])

    # Highlight top genes with professional annotation
    top = plot_df.nsmallest(6, p_col)  # Reduced to avoid clutter
    for _, r in top.iterrows():
        label = r.get("Biomarker_HGNC") or str(r.get("Biomarker"))
        if pd.notna(r["log2HR"]) and pd.notna(r["neglog10p"]):
            ax.annotate(label, (r["log2HR"], r["neglog10p"]), 
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, fontweight='bold', color=COLORS['dark'],
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8, edgecolor=COLORS['primary']))

    # Professional styling
    ax.set_xlabel("log₂(Hazard Ratio)", fontsize=12, fontweight='600', color=COLORS['dark'])
    ax.set_ylabel("−log₁₀(p-value)", fontsize=12, fontweight='600', color=COLORS['dark'])
    ax.set_title(title, fontsize=14, fontweight='700', color=COLORS['primary'], pad=20)
    ax.grid(alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_facecolor('#fafbfc')

    # Professional legend
    ax.legend(frameon=True, fancybox=True, shadow=True, framealpha=0.9)

    # Summary statistics box
    n = len(plot_df)
    n_nom = int((plot_df[p_col] < p_thresh).sum())
    n_fdr = int((plot_df[fdr_col] < fdr_thresh).sum()) if fdr_col in plot_df.columns else 0
    
    summary_text = f"Total biomarkers: {n:,}\nNominal p<{p_thresh}: {n_nom:,}\nFDR<{fdr_thresh}: {n_fdr:,}"
    ax.text(0.02, 0.98, summary_text, transform=ax.transAxes, va="top", ha="left",
           bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.95, 
                    edgecolor=COLORS['primary'], linewidth=1.5),
           fontsize=10, fontweight='600')

def forest(ax, df, top_n=15, title="Top Biomarkers — Cox Regression"):
    """Create professional forest plot with confidence intervals"""
    d = df.nsmallest(top_n, "Adjusted_p").copy()
    d = d.sort_values("Adjusted_p", ascending=False)  # Bottom to top by significance
    y = np.arange(len(d))

    # Color gradient for bars
    colors = plt.cm.Blues_r(np.linspace(0.3, 0.8, len(d)))

    # Plot confidence intervals and point estimates
    for i, (_, r) in enumerate(d.iterrows()):
        lo, hi, hr = r["Adjusted_CI_lower"], r["Adjusted_CI_upper"], r["Adjusted_HR"]
        if pd.notna(lo) and pd.notna(hi) and pd.notna(hr):
            # CI line
            ax.plot([lo, hi], [i, i], linewidth=4, alpha=0.8, color=colors[i])
            # Point estimate
            ax.scatter([hr], [i], s=80, color='white', edgecolors=colors[i], 
                      linewidth=2.5, zorder=3)

    # Gene labels with amplification frequency
    labels = []
    for _, r in d.iterrows():
        name = r.get("Biomarker_HGNC") or str(r.get("Biomarker"))
        freq = r.get("Amp_frequency")
        p_val = r.get("Adjusted_p")
        freq_txt = f"{freq*100:.1f}%" if pd.notna(freq) else "NA"
        p_txt = f"p={p_val:.2e}" if pd.notna(p_val) else ""
        labels.append(f"{name} ({freq_txt}) {p_txt}")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Hazard Ratio (95% CI)", fontsize=12, fontweight='600', color=COLORS['dark'])
    ax.set_xscale("log")
    
    # Reference line at HR = 1
    ax.axvline(1.0, linestyle="--", alpha=0.7, color=COLORS['primary'], linewidth=2)
    ax.text(1.02, len(d)*0.95, "HR = 1", rotation=90, va="top", ha="left", 
           fontweight='600', color=COLORS['primary'])
    
    ax.set_title(title, fontsize=14, fontweight='700', color=COLORS['primary'], pad=20)
    ax.grid(alpha=0.3, axis="x", linestyle='-', linewidth=0.5)
    ax.set_facecolor('#fafbfc')
    
    # Professional x-axis formatting
    ax.tick_params(axis='x', labelsize=10)
    ax.tick_params(axis='y', labelsize=9)

def km_plot(ax, clinical_df, amp_df, symbol_to_entrez, gene_symbol):
    """Create professional Kaplan-Meier survival curves"""
    if gene_symbol not in symbol_to_entrez:
        ax.text(0.5, 0.5, f"{gene_symbol}: Not found in HGNC mapping", 
               ha='center', va='center', transform=ax.transAxes,
               fontsize=12, color=COLORS['danger'])
        ax.set_title(f"{gene_symbol} — Data Not Available", fontweight='700', color=COLORS['danger'])
        return
        
    entrez = str(symbol_to_entrez[gene_symbol])
    if entrez not in amp_df.index:
        ax.text(0.5, 0.5, f"{gene_symbol} ({entrez})\nNot found in amplification data", 
               ha='center', va='center', transform=ax.transAxes,
               fontsize=12, color=COLORS['danger'])
        ax.set_title(f"{gene_symbol} — Data Not Available", fontweight='700', color=COLORS['danger'])
        return

    amp_status = amp_df.loc[entrez].reset_index()
    amp_status.columns = ["PATIENT_ID_CLEAN", "AMP_STATUS"]
    df = clinical_df.merge(amp_status, on="PATIENT_ID_CLEAN", how="inner")
    df = df.dropna(subset=["OS_MONTHS", "OS_STATUS_BINARY", "AMP_STATUS"])

    if df["AMP_STATUS"].nunique() < 2:
        ax.text(0.5, 0.5, f"{gene_symbol}\nInsufficient group separation", 
               ha='center', va='center', transform=ax.transAxes,
               fontsize=12, color=COLORS['warning'])
        ax.set_title(f"{gene_symbol} — Insufficient Data", fontweight='700', color=COLORS['warning'])
        return

    # Split groups
    grpA = df[df["AMP_STATUS"] == 1]  # Amplified
    grpB = df[df["AMP_STATUS"] == 0]  # Not amplified

    # Fit Kaplan-Meier curves
    kmA = KaplanMeierFitter()
    kmB = KaplanMeierFitter()
    
    label_A = f"Amplified (n={len(grpA)})"
    label_B = f"Not amplified (n={len(grpB)})"
    
    kmA.fit(grpA["OS_MONTHS"], grpA["OS_STATUS_BINARY"], label=label_A)
    kmB.fit(grpB["OS_MONTHS"], grpB["OS_STATUS_BINARY"], label=label_B)

    # Plot with professional styling
    kmA.plot_survival_function(ax=ax, ci_show=True, ci_alpha=0.15, 
                              color=COLORS['primary'], linewidth=3)
    kmB.plot_survival_function(ax=ax, ci_show=True, ci_alpha=0.15, 
                              color=COLORS['secondary'], linewidth=3)

    # Statistical test
    try:
        res = logrank_test(grpA["OS_MONTHS"], grpB["OS_MONTHS"],
                          event_observed_A=grpA["OS_STATUS_BINARY"],
                          event_observed_B=grpB["OS_STATUS_BINARY"])
        p = res.p_value
        
        # Format p-value appropriately
        if p < 0.001:
            p_text = f"p < 0.001"
        else:
            p_text = f"p = {p:.3f}"
            
    except Exception:
        p_text = "p = N/A"

    # Professional styling
    ax.set_title(f"{gene_symbol} Amplification — Overall Survival\n{p_text}", 
                fontsize=12, fontweight='700', color=COLORS['primary'], pad=15)
    ax.set_xlabel("Time (Months)", fontsize=11, fontweight='600', color=COLORS['dark'])
    ax.set_ylabel("Overall Survival Probability", fontsize=11, fontweight='600', color=COLORS['dark'])
    ax.grid(alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_facecolor('#fafbfc')
    
    # Professional legend
    ax.legend(frameon=True, fancybox=True, shadow=True, framealpha=0.9, loc='best')
    
    # Set axis limits for better visualization
    ax.set_ylim(0, 1)
    ax.set_xlim(0, None)

# -------------------------- Load data --------------------------
with st.spinner("Loading Cox regression results and survival data..."):
    os_df, pfs_df = load_cox_results()
    clinical_df, amp_df, symbol_to_entrez, entrez_to_symbol = load_km_inputs()

# -------------------------- Sidebar controls --------------------------
with st.sidebar:
    st.markdown("### 📊 Analysis Settings")
    
    endpoint = st.radio(
        "**Primary Endpoint**", 
        ["OS", "PFS"], 
        help="Select Overall Survival (OS) or Progression-Free Survival (PFS) for Cox regression analysis",
        index=0
    )
    
    st.markdown("---")
    
    st.markdown("### 🎯 Statistical Thresholds")
    p_thresh = st.number_input(
        "**Nominal p-value threshold**", 
        value=0.05, step=0.01, min_value=0.0, max_value=1.0,
        help="Threshold for nominal statistical significance"
    )
    
    fdr_thresh = st.number_input(
        "**FDR threshold**", 
        value=0.05, step=0.01, min_value=0.0, max_value=1.0,
        help="False Discovery Rate threshold for multiple testing correction"
    )
    
    st.markdown("---")
    
    st.markdown("### 📈 Visualization Options")
    top_n = st.slider(
        "**Forest plot: Top N biomarkers**", 
        min_value=5, max_value=30, value=15, step=1,
        help="Number of top biomarkers to display in forest plot (ranked by adjusted p-value)"
    )
    
    st.markdown("---")
    
    st.markdown("### 🧬 Kaplan-Meier Analysis")
    default_genes = ["CCNE1", "ACTN4", "URI1"]
    genes = st.multiselect(
        "**Select genes for survival analysis**",
        options=list(symbol_to_entrez.keys()) if symbol_to_entrez else default_genes,
        default=default_genes,
        help="Choose HGNC gene symbols for Kaplan-Meier survival curve analysis"
    )

# Select appropriate DataFrame
df = os_df if endpoint == "OS" else pfs_df
other_df = pfs_df if endpoint == "OS" else os_df

if df.empty:
    st.error("❌ **Cox regression results not found.** Please ensure the expected CSV files are present in the data directory.")
    st.info("📁 Expected files: `biomarker_cox_results_os_with_HGNC.csv` and `biomarker_cox_results_pfs_with_HGNC.csv`")
    st.stop()

# Summary metrics at the top
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #1e40af; margin: 0;">Total Biomarkers</h3>
        <h2 style="color: #1e40af; margin: 0.5rem 0 0 0;">{:,}</h2>
    </div>
    """.format(len(df)), unsafe_allow_html=True)

with col2:
    n_nom_sig = int((df["Adjusted_p"] < p_thresh).sum())
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #1e40af; margin: 0;">Nominally Significant</h3>
        <h2 style="color: #1e40af; margin: 0.5rem 0 0 0;">{:,}</h2>
        <p style="color: #64748b; margin: 0.25rem 0 0 0; font-size: 0.9rem;">p < {}</p>
    </div>
    """.format(n_nom_sig, p_thresh), unsafe_allow_html=True)

with col3:
    endpoint_full = "Overall Survival" if endpoint == "OS" else "Progression-Free Survival"
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #1e40af; margin: 0;">Current Endpoint</h3>
        <h2 style="color: #1e40af; margin: 0.5rem 0 0 0; font-size: 1.5rem;">{}</h2>
    </div>
    """.format(endpoint_full), unsafe_allow_html=True)

st.markdown("---")

# -------------------------- Main visualizations --------------------------
st.markdown('<h2 class="section-header">📊 Exploratory Analysis</h2>', unsafe_allow_html=True)

col1, col2 = st.columns([1.1, 1.0], gap="large")

with col1:
    st.markdown(f"### 🌋 Volcano Plot — {endpoint}")
    fig, ax = plt.subplots(figsize=(10, 8))
    volcano(ax, df, p_col="Adjusted_p", hr_col="Adjusted_HR",
           fdr_col="Adjusted_FDR", p_thresh=p_thresh, fdr_thresh=fdr_thresh,
           title=f"Biomarker Association Analysis ({endpoint})")
    plt.tight_layout()
    st.pyplot(fig, clear_figure=True)

with col2:
    st.markdown(f"### 🌲 Forest Plot — {endpoint}")
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    forest(ax2, df, top_n=top_n, title=f"Top {top_n} Biomarkers — Cox Regression ({endpoint})")
    plt.tight_layout()
    st.pyplot(fig2, clear_figure=True)

st.markdown("---")

# -------------------------- Results table --------------------------
st.markdown('<h2 class="section-header">📋 Significant Results</h2>', unsafe_allow_html=True)

has_fdr_hits = ("Adjusted_FDR" in df.columns) and (df["Adjusted_FDR"] < fdr_thresh).any()

if has_fdr_hits:
    table_df = df[df["Adjusted_FDR"] < fdr_thresh].copy()
    sig_note = f"🎯 **FDR-corrected significant results** (FDR < {fdr_thresh})"
    alert_type = "success"
else:
    table_df = df[df["Adjusted_p"] < p_thresh].copy()
    sig_note = f"⚠️ **Nominally significant results** (p < {p_thresh}) — *Exploratory analysis; no FDR-significant findings*"
    alert_type = "warning"

# Display appropriate alert
if alert_type == "success":
    st.success(sig_note)
else:
    st.warning(sig_note)

# Table columns to display
show_cols = ["Biomarker_HGNC", "Biomarker", "N_patients", "Amp_frequency",
             "Adjusted_HR", "Adjusted_CI_lower", "Adjusted_CI_upper", "Adjusted_p", "Adjusted_FDR"]

if table_df.empty:
    st.info("📈 **No significant associations found** under current thresholds. Consider adjusting the statistical thresholds in the sidebar or review the exploratory plots above for trends.")
else:
    # Format the table for better presentation
    display_df = table_df[[c for c in show_cols if c in table_df.columns]].copy()
    
    # Round numeric columns appropriately
    if "Amp_frequency" in display_df.columns:
        display_df["Amp_frequency"] = display_df["Amp_frequency"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A")
    
    for col in ["Adjusted_HR", "Adjusted_CI_lower", "Adjusted_CI_upper"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "N/A")
    
    for col in ["Adjusted_p", "Adjusted_FDR"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2e}" if pd.notna(x) and x > 0 else "N/A")
    
    # Rename columns for better display
    column_rename = {
        "Biomarker_HGNC": "Gene Symbol",
        "Biomarker": "Biomarker ID", 
        "N_patients": "N Patients",
        "Amp_frequency": "Amplification Frequency",
        "Adjusted_HR": "Hazard Ratio",
        "Adjusted_CI_lower": "CI Lower",
        "Adjusted_CI_upper": "CI Upper", 
        "Adjusted_p": "P-value",
        "Adjusted_FDR": "FDR"
    }
    
    display_df = display_df.rename(columns=column_rename)
    display_df = display_df.sort_values(["FDR", "P-value"], na_position="last").reset_index(drop=True)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# -------------------------- Kaplan-Meier survival analysis --------------------------
st.markdown('<h2 class="section-header">📈 Kaplan-Meier Survival Analysis</h2>', unsafe_allow_html=True)

if clinical_df.empty or amp_df.empty:
    st.error("❌ **Survival analysis data not available.** Please ensure the following files are present:")
    st.info("📁 Required files: `clinical_matched.csv`, `biomarker_amplifications_matched.csv`, and `gene_with_protein_product.txt`")
else:
    if not genes:
        st.info("🧬 **Select genes in the sidebar** to generate Kaplan-Meier survival curves.")
    else:
        st.markdown(f"**Analyzing {len(genes)} selected gene(s) for amplification-based survival differences**")
        
        # Arrange plots in a responsive grid
        ncols = min(3, len(genes))  # Max 3 columns
        rows = math.ceil(len(genes) / ncols)
        
        for r in range(rows):
            cols = st.columns(ncols)
            for j in range(ncols):
                idx = r * ncols + j
                if idx >= len(genes):
                    break
                    
                gene = genes[idx]
                with cols[j]:
                    fig_km, ax_km = plt.subplots(figsize=(8, 6))
                    km_plot(ax_km, clinical_df, amp_df, symbol_to_entrez, gene)
                    plt.tight_layout()
                    st.pyplot(fig_km, clear_figure=True)

st.markdown("---")

# -------------------------- Methods and interpretation --------------------------
with st.expander("📚 **Methods, Interpretation & Important Caveats**", expanded=False):
    st.markdown("""
    #### 🔬 **Statistical Methods**
    
    **Cox Proportional Hazards Models:**
    - Individual biomarker analysis adjusted for age
    - Hazard ratios (HR) with 95% confidence intervals
    - Multiple testing correction using Benjamini-Hochberg FDR
    
    **Kaplan-Meier Analysis:**
    - Survival curves stratified by GISTIC deep amplification status (≥2 vs <2)
    - Log-rank test for group comparison
    - Overall survival (OS) as primary endpoint
    
    #### 📊 **Data Sources**
    - **Clinical Data:** TCGA-OV Pan-Cancer Atlas
    - **Genomic Data:** GISTIC copy number alterations
    - **Gene Mapping:** HGNC official gene symbols and Entrez IDs
    
    #### ⚠️ **Important Limitations & Caveats**
    
    **Statistical Considerations:**
    - **Multiple Testing:** Expect few/no FDR-significant hits in exploratory genomic screens
    - **Nominal Significance:** Use p<0.05 findings for hypothesis generation, not clinical decisions
    - **Association ≠ Causation:** Statistical associations do not imply biological causation
    
    **Clinical Interpretation:**
    - **No Treatment Recommendations:** Results are for research purposes only
    - **Validation Required:** Findings require independent validation in separate cohorts
    - **Population Specificity:** Results may not generalize beyond TCGA-OV population
    
    **Technical Notes:**
    - **Amplification Definition:** GISTIC score ≥2 (deep amplification)
    - **Sample Matching:** Analysis limited to patients with both clinical and genomic data
    - **Missing Data:** Patients with incomplete survival or genomic data excluded
    
    #### 🎯 **Best Practices for Interpretation**
    1. **Prioritize FDR-significant findings** for follow-up studies
    2. **Consider biological plausibility** of associations
    3. **Review amplification frequency** - very rare events may lack power
    4. **Cross-reference with literature** and pathway knowledge
    5. **Plan validation studies** for promising candidates
    """)

st.markdown("---")

# -------------------------- Data download section --------------------------
st.markdown('<h2 class="section-header">💾 Download Results</h2>', unsafe_allow_html=True)

st.markdown("**Export your analysis results for further investigation or reporting:**")

dl_col1, dl_col2 = st.columns(2)

with dl_col1:
    st.download_button(
        label="📥 Download OS Cox Results",
        data=os_df.to_csv(index=False).encode("utf-8") if not os_df.empty else "".encode("utf-8"),
        file_name=f"TCGA_OV_Cox_OS_Results_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        disabled=os_df.empty,
        help="Download Overall Survival Cox regression results with HGNC gene symbols"
    )

with dl_col2:
    st.download_button(
        label="📥 Download PFS Cox Results", 
        data=pfs_df.to_csv(index=False).encode("utf-8") if not pfs_df.empty else "".encode("utf-8"),
        file_name=f"TCGA_OV_Cox_PFS_Results_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        disabled=pfs_df.empty,
        help="Download Progression-Free Survival Cox regression results with HGNC gene symbols"
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
        Advancing precision oncology through computational genomics
    </div>
</div>
""", unsafe_allow_html=True)