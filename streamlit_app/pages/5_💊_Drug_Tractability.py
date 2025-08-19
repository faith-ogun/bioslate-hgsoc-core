# 5_💊_Drug_Tractability.py
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# -------------------------- Page config & styling --------------------------
st.set_page_config(
    page_title="Drug Tractability | Synthetic Lethal Targets",
    page_icon="💊",
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
    
    /* Header styling - Teal Blue Theme for Drug Discovery */
    .main-header {
        background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
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
        color: #cffafe !important;
        font-size: 1.1rem;
        margin-bottom: 0.25rem;
    }
    
    .last-updated {
        color: #a7f3d0 !important;
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
        border-left: 4px solid #0891b2;
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
    
    /* Highlight box for key findings */
    .key-findings {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #0891b2;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin: 2rem 0;
    }
    
    .key-findings h3 {
        color: #0c4a6e;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .key-findings ul {
        color: #164e63;
        line-height: 1.8;
    }
    
    .key-findings strong {
        color: #0c4a6e;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid #0891b2;
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
    
    /* Tier highlight */
    .tier-highlight {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        margin: 1.5rem 0;
    }
    
    .tier-highlight h4 {
        color: #92400e;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .tier-highlight p {
        color: #a16207;
        margin: 0;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header section
st.markdown("""
<div class="main-header">
    <h1>💊 Therapeutic Tractability of Synthetic Lethal Targets</h1>
    <div class="caption">Comprehensive analysis of druggability across small molecule and antibody therapeutic modalities</div>
    <div class="last-updated">Last updated: August 19th, 2025</div>
</div>
""", unsafe_allow_html=True)

# Set professional color palette
plt.style.use('default')
sns.set_palette("viridis")
COLORS = {
    'primary': '#0891b2',
    'secondary': '#06b6d4', 
    'accent': '#67e8f9',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'light': '#f8fafc',
    'dark': '#1e293b'
}

# -------------------------- Data loaders --------------------------
@st.cache_data(show_spinner=False)
def load_tractability():
    """
    Preferred input (generated in your GDSC/OT notebook):
      - streamlit_app/data/sl_pairs_opentargets_drug_info.csv
        Columns include:
          Biomarker, Target, Known_Drugs, Tractability_Interpretation,
          and binary flags (e.g., 'Approved Drug','Advanced Clinical','High-Quality Pocket', etc.)
    If a 'full' file with antibody modalities exists, we will detect those too.
    """
    default_paths = [
        "streamlit_app/data/sl_pairs_opentargets_drug_info.csv",
    ]
    full_paths = [
        "streamlit_app/data/sl_pairs_opentargets_drug_info_full.csv",
    ]

    df = pd.DataFrame()
    for p in default_paths:
        if os.path.exists(p):
            df = pd.read_csv(p)
            break

    df_full = pd.DataFrame()
    for p in full_paths:
        if os.path.exists(p):
            df_full = pd.read_csv(p)
            break

    return df, df_full

df, df_full = load_tractability()
if df.empty and df_full.empty:
    st.error("No Open Targets tractability file found. Expected one of:\n"
             "- streamlit_app/data/sl_pairs_opentargets_drug_info.csv\n"
             "- results/clinical_translation/sl_pairs_opentargets_drug_info.csv\n"
             "Optionally, provide a '*_full.csv' with antibody modality flags.")
    st.stop()

# Use full if present (includes antibody modality flags), else fallback
base = df_full.copy() if not df_full.empty else df.copy()

# Clean + normalise columns
for col in ["Biomarker", "Target", "Known_Drugs", "Tractability_Interpretation"]:
    if col not in base.columns:
        base[col] = np.nan
base["Target"] = base["Target"].astype(str).str.strip()
base["Biomarker"] = base["Biomarker"].astype(str).str.strip()

# Detect tractability flag columns
flag_cols = [c for c in base.columns if c.lower() in {
    "approved drug", "advanced clinical", "phase 1 clinical", "clinical precedence",
    "structure with ligand", "high-quality ligand", "high-quality pocket", "druggable family"
}]
# Also detect any prefixed flags (e.g., SM_*, AB_*)
flag_cols += [c for c in base.columns if c.startswith(("SM_", "AB_", "BIO_"))]
flag_cols = sorted(set(flag_cols), key=lambda x: str(x).lower())

# Small-molecule and antibody groups (robust to either plain flags or prefixed flags)
SM_HINTS = {"approved drug", "advanced clinical", "phase 1 clinical", "clinical precedence",
            "structure with ligand", "high-quality ligand", "high-quality pocket", "druggable family"}
AB_HINTS = {"antibody_tractable", "ab_approved", "ab_clinical", "extracellular", "cell_surface", "antibody"}

def is_flag_true(val):
    try:
        return int(val) == 1
    except Exception:
        # also consider True/'true'/'Yes' as positive
        return str(val).strip().lower() in {"1", "true", "yes", "y"}

def summarise_modality(df_in):
    # Per-target aggregation: any evidence per modality
    sm_cols = [c for c in flag_cols if (c.startswith("SM_") or c.lower() in SM_HINTS)]
    ab_cols = [c for c in flag_cols if (c.startswith("AB_") or any(h in c.lower() for h in AB_HINTS))]

    grp = df_in.groupby("Target", as_index=False).agg({
        **{c: (c, lambda s: any(is_flag_true(x) for x in s)) for c in sm_cols + ab_cols},
        "Known_Drugs": ("Known_Drugs", lambda s: any(isinstance(x, str) and len(x.strip()) > 0 for x in s)),
        "Tractability_Interpretation": ("Tractability_Interpretation", lambda s: pd.Series(s).mode().iloc[0] if len(pd.Series(s).dropna()) else np.nan),
    })
    grp.columns = [c[0] if isinstance(c, tuple) else c for c in grp.columns]
    # Create roll‑ups
    grp["SM_any"] = grp[sm_cols].any(axis=1) if sm_cols else False
    grp["AB_any"] = grp[ab_cols].any(axis=1) if ab_cols else False
    grp["HasKnownDrugs"] = grp["Known_Drugs"].astype(bool)
    return grp, sm_cols, ab_cols

per_target, sm_cols, ab_cols = summarise_modality(base)

# -------------------------- Key Research Findings --------------------------
st.markdown("""
<div class="key-findings">
    <h3>🎯 Key Research Findings</h3>
    <p style="color: #581c87; font-size: 1.1rem; margin-bottom: 1.5rem; font-weight: 600;">
        Comprehensive therapeutic tractability analysis of synthetic lethal targets reveals high druggability potential:
    </p>
    <ul style="margin: 0; padding-left: 1.5rem;">
        <li><strong>64.8% of targets (147/227)</strong> demonstrated tractability evidence across at least one therapeutic modality</li>
        <li><strong>Small molecule dominance:</strong> 7 targets with approved drugs, 13 with clinical precedence, 89 with discovery precedence</li>
        <li><strong>Antibody potential:</strong> 51 targets with high confidence tractability, 30 with medium confidence</li>
        <li><strong>Immediate therapeutic relevance:</strong> Tier 1 targets (KRAS, CDK4, RAF1, ACLY, TXNRD1) all show strong small molecule tractability</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Tier 1 targets highlight
st.markdown("""
<div class="tier-highlight">
    <h4>⭐ Tier 1 Priority Targets</h4>
    <p>Highest synthetic lethal effect sizes with approved drug availability: <strong>KRAS, CDK4, RAF1, ACLY, TXNRD1</strong></p>
</div>
""", unsafe_allow_html=True)

# -------------------------- Sidebar --------------------------
st.sidebar.title("Analysis Options")
view = st.sidebar.radio("Summary View", ["Overview", "Details table"])
if sm_cols:
    sm_flags_sel = st.sidebar.multiselect("Small‑molecule flags", sm_cols, default=sm_cols[:min(5, len(sm_cols))])
else:
    sm_flags_sel = []
if ab_cols:
    ab_flags_sel = st.sidebar.multiselect("Antibody flags", ab_cols, default=ab_cols[:min(5, len(ab_cols))])
else:
    ab_flags_sel = []

# -------------------------- Top metrics --------------------------
n_targets = per_target.shape[0]
n_sm = int(per_target["SM_any"].sum()) if "SM_any" in per_target else 0
n_ab = int(per_target["AB_any"].sum()) if "AB_any" in per_target else 0
n_known_drugs = int(per_target["HasKnownDrugs"].sum())
n_total_tractable = len(per_target[(per_target.get("SM_any", False)) | (per_target.get("AB_any", False))])

st.markdown('<h2 class="section-header">📊 Tractability Landscape Overview</h2>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #0891b2; margin: 0;">Total SL Targets</h3>
        <h2 style="color: #0891b2; margin: 0.25rem 0 0 0;">{:,}</h2>
        <p style="color: #64748b; margin: 0.25rem 0 0 0; font-size: 0.9rem;">Unique synthetic lethal targets</p>
    </div>
    """.format(n_targets), unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #0891b2; margin: 0;">Any Tractability</h3>
        <h2 style="color: #0891b2; margin: 0.25rem 0 0 0;">{:,}</h2>
        <p style="color: #64748b; margin: 0.25rem 0 0 0; font-size: 0.9rem;">{:.1f}% with any evidence</p>
    </div>
    """.format(n_total_tractable, (n_total_tractable/n_targets*100 if n_targets else 0)), unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #0891b2; margin: 0;">Small Molecule</h3>
        <h2 style="color: #0891b2; margin: 0.25rem 0 0 0;">{:,}</h2>
        <p style="color: #64748b; margin: 0.25rem 0 0 0; font-size: 0.9rem;">{:.1f}% tractable</p>
    </div>
    """.format(n_sm, (n_sm/n_targets*100 if n_targets else 0)), unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #0891b2; margin: 0;">Antibody Modality</h3>
        <h2 style="color: #0891b2; margin: 0.25rem 0 0 0;">{:,}</h2>
        <p style="color: #64748b; margin: 0.25rem 0 0 0; font-size: 0.9rem;">{:.1f}% tractable</p>
    </div>
    """.format(n_ab, (n_ab/n_targets*100 if n_targets else 0)), unsafe_allow_html=True)

# -------------------------- Visuals --------------------------
st.markdown('<h2 class="section-header">📈 Tractability Evidence Breakdown</h2>', unsafe_allow_html=True)

colA, colB = st.columns(2)

# A) Small-molecule flag counts
with colA:
    if sm_cols:
        sm_counts = per_target[sm_cols].apply(lambda s: s.sum(), axis=0).sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(9, 6))
        bars = sns.barplot(x=sm_counts.values, y=sm_counts.index, palette="viridis", ax=ax)
        ax.set_xlabel("Number of Targets with Evidence", fontsize=12, fontweight='600')
        ax.set_ylabel("Small Molecule Evidence Type", fontsize=12, fontweight='600')
        ax.set_title("Small Molecule Tractability Evidence", fontsize=14, fontweight='700', color=COLORS['primary'], pad=20)
        ax.grid(axis="x", alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(sm_counts.values):
            ax.text(v + 0.1, i, str(v), va='center', fontweight='600')
            
        plt.tight_layout()
        st.pyplot(fig, clear_figure=True)
    else:
        st.info("No explicit small‑molecule flag columns found. Provide the Open Targets flags file with SM_* or standard labels.")

# B) Antibody flag counts (if available)
with colB:
    if ab_cols:
        ab_counts = per_target[ab_cols].apply(lambda s: s.sum(), axis=0).sort_values(ascending=False)
        fig2, ax2 = plt.subplots(figsize=(9, 6))
        bars2 = sns.barplot(x=ab_counts.values, y=ab_counts.index, palette="plasma", ax=ax2)
        ax2.set_xlabel("Number of Targets with Evidence", fontsize=12, fontweight='600')
        ax2.set_ylabel("Antibody Evidence Type", fontsize=12, fontweight='600')
        ax2.set_title("Antibody Tractability Evidence", fontsize=14, fontweight='700', color=COLORS['primary'], pad=20)
        ax2.grid(axis="x", alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(ab_counts.values):
            ax2.text(v + 0.1, i, str(v), va='center', fontweight='600')
            
        plt.tight_layout()
        st.pyplot(fig2, clear_figure=True)
    else:
        st.warning("Antibody tractability flags not detected. If you have a file with antibody modality (e.g. AB_* columns), drop it into "
                   "`streamlit_app/data/sl_pairs_opentargets_drug_info_full.csv` and refresh.")

# Modality coverage summary
if "SM_any" in per_target.columns and "AB_any" in per_target.columns:
    st.markdown('<h2 class="section-header">🎯 Therapeutic Modality Coverage</h2>', unsafe_allow_html=True)
    
    # Calculate overlaps
    sm_only = int(((per_target["SM_any"]) & (~per_target["AB_any"])).sum())
    ab_only = int(((~per_target["SM_any"]) & (per_target["AB_any"])).sum())
    both = int(((per_target["SM_any"]) & (per_target["AB_any"])).sum())
    neither = int(((~per_target["SM_any"]) & (~per_target["AB_any"])).sum())
    
    stack_df = pd.DataFrame({
        "Modality": ["Small Molecule Only", "Antibody Only", "Both Modalities", "No Evidence"],
        "Count": [sm_only, ab_only, both, neither],
        "Percentage": [sm_only/n_targets*100, ab_only/n_targets*100, both/n_targets*100, neither/n_targets*100]
    })
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        colors = ['#0891b2', '#06b6d4', '#67e8f9', '#e2e8f0']
        bars = sns.barplot(data=stack_df, x="Modality", y="Count", palette=colors, ax=ax3)
        ax3.set_title("Targets by Therapeutic Modality", fontsize=16, fontweight='700', color=COLORS['primary'], pad=20)
        ax3.set_xlabel("Tractability Category", fontsize=12, fontweight='600')
        ax3.set_ylabel("Number of Targets", fontsize=12, fontweight='600')
        ax3.grid(axis="y", alpha=0.3)
        
        # Add value labels on bars
        for i, (count, pct) in enumerate(zip(stack_df["Count"], stack_df["Percentage"])):
            ax3.text(i, count + 1, f'{count}\n({pct:.1f}%)', ha='center', va='bottom', fontweight='600')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig3, clear_figure=True)
    
    with col2:
        st.markdown("### Summary Statistics")
        st.metric("Tractable Targets", f"{sm_only + ab_only + both}", f"{(sm_only + ab_only + both)/n_targets*100:.1f}%")
        st.metric("Multi-modal Targets", f"{both}", f"{both/n_targets*100:.1f}%")
        st.metric("SM Priority", f"{sm_only + both}", f"{(sm_only + both)/n_targets*100:.1f}%")
        st.metric("AB Priority", f"{ab_only + both}", f"{(ab_only + both)/n_targets*100:.1f}%")

# -------------------------- Details table --------------------------
st.markdown('<h2 class="section-header">📋 Detailed Tractability Analysis</h2>', unsafe_allow_html=True)

if view == "Overview":
    # Condensed per-target view
    show_cols = ["Target", "SM_any", "AB_any", "HasKnownDrugs", "Tractability_Interpretation"]
    show_cols += [c for c in (sm_flags_sel + ab_flags_sel) if c in per_target.columns]
    show_cols = [c for c in show_cols if c in per_target.columns]
    
    # Rename columns for better display
    display_df = per_target[show_cols].copy()
    column_rename = {
        "SM_any": "Small Molecule Tractable",
        "AB_any": "Antibody Tractable", 
        "HasKnownDrugs": "Known Drugs Available",
        "Tractability_Interpretation": "Overall Assessment"
    }
    display_df = display_df.rename(columns=column_rename)
    
    st.dataframe(
        display_df.sort_values(["Small Molecule Tractable", "Antibody Tractable", "Known Drugs Available"], ascending=False),
        use_container_width=True,
        hide_index=True
    )
else:
    # Pair-level full view
    show_cols = ["Biomarker", "Target", "Known_Drugs", "Tractability_Interpretation"] + flag_cols
    show_cols = [c for c in show_cols if c in base.columns]
    st.dataframe(base[show_cols].sort_values(["Target"]).reset_index(drop=True), use_container_width=True)

# -------------------------- Downloads --------------------------
st.markdown('<h2 class="section-header">💾 Export Analysis Results</h2>', unsafe_allow_html=True)

c_dl1, c_dl2 = st.columns(2)
with c_dl1:
    # Per-target summary
    csv1 = per_target.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Per-Target Summary",
        csv1, 
        f"tractability_per_target_{pd.Timestamp.now().strftime('%Y%m%d')}.csv", 
        "text/csv",
        help="Download aggregated tractability data per target gene"
    )
with c_dl2:
    csv2 = base.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Complete Dataset", 
        csv2, 
        f"tractability_complete_{pd.Timestamp.now().strftime('%Y%m%d')}.csv", 
        "text/csv",
        help="Download full tractability dataset including all biomarker-target pairs"
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
