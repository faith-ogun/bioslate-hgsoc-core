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
sns.set_palette("Blues_r")
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
    """Load the actual tractability data files"""
    # Primary file: sl_pairs_opentargets_drug_info.csv
    primary_path = "streamlit_app/data/sl_pairs_opentargets_drug_info.csv"
    
    # Comprehensive file: tractability_api_fallback.tsv  
    comprehensive_path = "streamlit_app/data/tractability_api_fallback.tsv"
    
    df = pd.DataFrame()
    comprehensive_df = pd.DataFrame()
    
    # Load primary file
    if os.path.exists(primary_path):
        df = pd.read_csv(primary_path)
        st.sidebar.success(f"✅ Loaded primary data: {len(df)} biomarker-target pairs")
    
    # Load comprehensive file  
    if os.path.exists(comprehensive_path):
        comprehensive_df = pd.read_csv(comprehensive_path, sep='\t')
        st.sidebar.success(f"✅ Loaded comprehensive data: {len(comprehensive_df)} genes")
    
    if df.empty and comprehensive_df.empty:
        st.error("No tractability data files found. Expected files:\n"
                 "- streamlit_app/data/sl_pairs_opentargets_drug_info.csv\n"
                 "- streamlit_app/data/tractability_api_fallback.tsv")
        st.stop()
    
    return df, comprehensive_df

df, comprehensive_df = load_tractability()

# Use primary file if available, otherwise comprehensive
if not df.empty:
    base = df.copy()
    data_source = "Synthetic Lethal Pairs"
    st.sidebar.info("📊 Using SL pairs tractability data")
else:
    base = comprehensive_df.copy()
    data_source = "Comprehensive Gene Set"
    st.sidebar.info("📊 Using comprehensive tractability data")

# -------------------------- Data Processing --------------------------

# Clean and normalize columns for primary data
if not df.empty:
    # Standardize column names
    base["Target"] = base["Target"].astype(str).str.strip() if "Target" in base.columns else base["Biomarker"].astype(str).str.strip()
    base["Biomarker"] = base["Biomarker"].astype(str).str.strip() if "Biomarker" in base.columns else ""
    
    # Identify tractability flag columns
    flag_cols = [c for c in base.columns if c in [
        "Approved Drug", "Advanced Clinical", "Phase 1 Clinical", "Clinical Precedence",
        "Structure with Ligand", "High-Quality Ligand", "High-Quality Pocket", "Druggable Family"
    ]]
    
    sm_cols = flag_cols  # All flags are small molecule for this dataset
    ab_cols = []  # No antibody flags in primary dataset
    
else:
    # Process comprehensive data
    base = base.rename(columns={"approved_symbol": "Target"})
    base["Target"] = base["Target"].astype(str).str.strip()
    
    # Small molecule flags
    sm_cols = [c for c in base.columns if c.startswith("SM_")]
    # Antibody flags  
    ab_cols = [c for c in base.columns if c.startswith("AB_")]
    
    flag_cols = sm_cols + ab_cols

def is_flag_true(val):
    """Check if a flag value represents True"""
    try:
        return int(val) == 1
    except:
        return str(val).strip().lower() in {"1", "true", "yes", "y"}

# Create per-target summary
if not df.empty:
    # For SL pairs data
    per_target = base.groupby("Target").agg({
        **{col: lambda x: any(is_flag_true(v) for v in x) for col in flag_cols},
        "Known_Drugs": lambda x: any(isinstance(v, str) and len(str(v).strip()) > 0 and str(v).strip().lower() != 'nan' for v in x),
        "Tractability_Interpretation": lambda x: pd.Series(x).mode().iloc[0] if len(pd.Series(x).dropna()) > 0 else "Unknown"
    }).reset_index()
    
    # Add summary columns
    per_target["SM_any"] = per_target[sm_cols].any(axis=1) if sm_cols else False
    per_target["AB_any"] = False  # No antibody data in primary file
    per_target["HasKnownDrugs"] = per_target["Known_Drugs"].astype(bool)
    
else:
    # For comprehensive data  
    per_target = base.copy()
    per_target["SM_any"] = per_target[sm_cols].any(axis=1) if sm_cols else False
    per_target["AB_any"] = per_target[ab_cols].any(axis=1) if ab_cols else False
    per_target["HasKnownDrugs"] = False  # Not available in comprehensive data
    per_target["Known_Drugs"] = False

# -------------------------- Key Research Findings --------------------------
st.markdown("""
<div class="key-findings">
    <h3>🎯 Key Research Findings</h3>
    <p style="color: #164e63; font-size: 1.1rem; margin-bottom: 1.5rem; font-weight: 600;">
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

# Filter options based on available columns
if sm_cols:
    sm_flags_sel = st.sidebar.multiselect(
        "Small molecule flags", 
        sm_cols, 
        default=sm_cols[:min(5, len(sm_cols))],
        help="Select small molecule tractability evidence types to display"
    )
else:
    sm_flags_sel = []

if ab_cols:
    ab_flags_sel = st.sidebar.multiselect(
        "Antibody flags", 
        ab_cols, 
        default=ab_cols[:min(5, len(ab_cols))],
        help="Select antibody tractability evidence types to display"
    )
else:
    ab_flags_sel = []

# -------------------------- Top metrics --------------------------
n_targets = len(per_target)
n_sm = int(per_target["SM_any"].sum()) if "SM_any" in per_target.columns else 0
n_ab = int(per_target["AB_any"].sum()) if "AB_any" in per_target.columns else 0
n_known_drugs = int(per_target["HasKnownDrugs"].sum()) if "HasKnownDrugs" in per_target.columns else 0
n_total_tractable = len(per_target[(per_target.get("SM_any", False)) | (per_target.get("AB_any", False))])

st.markdown('<h2 class="section-header">📊 Tractability Landscape Overview</h2>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #0891b2; margin: 0;">Total Targets</h3>
        <h2 style="color: #0891b2; margin: 0.25rem 0 0 0;">{:,}</h2>
        <p style="color: #64748b; margin: 0.25rem 0 0 0; font-size: 0.9rem;">{}</p>
    </div>
    """.format(n_targets, data_source), unsafe_allow_html=True)

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
    if ab_cols:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #0891b2; margin: 0;">Antibody Modality</h3>
            <h2 style="color: #0891b2; margin: 0.25rem 0 0 0;">{:,}</h2>
            <p style="color: #64748b; margin: 0.25rem 0 0 0; font-size: 0.9rem;">{:.1f}% tractable</p>
        </div>
        """.format(n_ab, (n_ab/n_targets*100 if n_targets else 0)), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #0891b2; margin: 0;">Known Drugs</h3>
            <h2 style="color: #0891b2; margin: 0.25rem 0 0 0;">{:,}</h2>
            <p style="color: #64748b; margin: 0.25rem 0 0 0; font-size: 0.9rem;">{:.1f}% have drugs</p>
        </div>
        """.format(n_known_drugs, (n_known_drugs/n_targets*100 if n_targets else 0)), unsafe_allow_html=True)

# -------------------------- Visuals --------------------------
st.markdown('<h2 class="section-header">📈 Tractability Evidence Breakdown</h2>', unsafe_allow_html=True)

if sm_cols or ab_cols:
    colA, colB = st.columns(2)
    
    # A) Small-molecule flag counts
    with colA:
        if sm_cols:
            sm_counts = per_target[sm_cols].sum().sort_values(ascending=False)
            if sm_counts.sum() > 0:
                fig, ax = plt.subplots(figsize=(9, 6))
                bars = sns.barplot(x=sm_counts.values, y=sm_counts.index, palette="Blues_r", ax=ax)
                ax.set_xlabel("Number of Targets with Evidence", fontsize=12, fontweight='600')
                ax.set_ylabel("Small Molecule Evidence Type", fontsize=12, fontweight='600')
                ax.set_title("Small Molecule Tractability Evidence", fontsize=14, fontweight='700', color=COLORS['primary'], pad=20)
                ax.grid(axis="x", alpha=0.3)
                
                # Add value labels on bars
                for i, v in enumerate(sm_counts.values):
                    ax.text(v + 0.1, i, str(int(v)), va='center', fontweight='600')
                    
                plt.tight_layout()
                st.pyplot(fig, clear_figure=True)
            else:
                st.info("No small molecule tractability evidence found in current dataset.")
        else:
            st.info("No small molecule flags available in this dataset.")

    # B) Antibody flag counts (if available)
    with colB:
        if ab_cols:
            ab_counts = per_target[ab_cols].sum().sort_values(ascending=False)
            if ab_counts.sum() > 0:
                fig2, ax2 = plt.subplots(figsize=(9, 6))
                bars2 = sns.barplot(x=ab_counts.values, y=ab_counts.index, palette="viridis", ax=ax2)
                ax2.set_xlabel("Number of Targets with Evidence", fontsize=12, fontweight='600')
                ax2.set_ylabel("Antibody Evidence Type", fontsize=12, fontweight='600')
                ax2.set_title("Antibody Tractability Evidence", fontsize=14, fontweight='700', color=COLORS['primary'], pad=20)
                ax2.grid(axis="x", alpha=0.3)
                
                # Add value labels on bars
                for i, v in enumerate(ab_counts.values):
                    ax2.text(v + 0.1, i, str(int(v)), va='center', fontweight='600')
                    
                plt.tight_layout()
                st.pyplot(fig2, clear_figure=True)
            else:
                st.info("No antibody tractability evidence found in current dataset.")
        else:
            st.info("💡 **Antibody data available in comprehensive dataset**\n\nSwitch to comprehensive tractability data to see antibody modality analysis.")

    # Modality coverage summary
    if sm_cols and ab_cols and (per_target["SM_any"].sum() > 0 or per_target["AB_any"].sum() > 0):
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

else:
    st.warning("No tractability flag columns found in the dataset.")

# -------------------------- Details table --------------------------
st.markdown('<h2 class="section-header">📋 Detailed Tractability Analysis</h2>', unsafe_allow_html=True)

if view == "Overview":
    # Condensed per-target view
    show_cols = ["Target"]
    if "SM_any" in per_target.columns:
        show_cols.append("SM_any")
    if "AB_any" in per_target.columns:
        show_cols.append("AB_any")
    if "HasKnownDrugs" in per_target.columns:
        show_cols.append("HasKnownDrugs")
    if "Tractability_Interpretation" in per_target.columns:
        show_cols.append("Tractability_Interpretation")
    
    # Add selected flags
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
    
    # Sort by tractability
    sort_cols = [col for col in ["Small Molecule Tractable", "Antibody Tractable", "Known Drugs Available"] if col in display_df.columns]
    if sort_cols:
        display_df = display_df.sort_values(sort_cols, ascending=False)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
else:
    # Full detailed view
    show_cols = ["Target"]
    if "Biomarker" in base.columns:
        show_cols.insert(0, "Biomarker")
    if "Known_Drugs" in base.columns:
        show_cols.append("Known_Drugs")
    if "Tractability_Interpretation" in base.columns:
        show_cols.append("Tractability_Interpretation")
    
    show_cols += flag_cols
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