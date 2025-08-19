import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np
import io

# -------------------------- Page config & styling --------------------------
st.set_page_config(
    page_title="BioSLATE Gene–Protein Explorer",
    page_icon="🔎",
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
    
    /* Header styling - Sky Blue Theme */
    .main-header {
        background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%);
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
        color: #e0f2fe !important;
        font-size: 1.1rem;
        margin-bottom: 0.25rem;
    }
    
    .last-updated {
        color: #bae6fd !important;
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
    <h1>🔬 Interactive Viewer of CNA and Protein Expression Dynamics</h1>
    <div class="caption">Statistical analysis and visualization of copy number alterations and protein expression relationships</div>
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

@st.cache_data
def load_data():
    # Load CNA-protein data with gene symbols
    cnv_prot_df = pd.read_csv(
        "streamlit_app/data/cnv_prot_boxplot_with_hgnc.csv",
        usecols=["Gene", "Gene_HGNC", "Sample", "CNA", "Protein"]
    )

    # Load raw stats files
    t_test_stats_df_raw = pd.read_csv("streamlit_app/data/per_gene_stats_filtered.csv")
    linear_regression_df_raw = pd.read_csv("streamlit_app/data/per_gene_linear_regression.csv")

    # Rename Entrez 'Gene' to HGNC symbol column
    t_test_stats_df = t_test_stats_df_raw.rename(columns={"Gene": "Gene_HGNC"})
    linear_regression_df = linear_regression_df_raw.rename(columns={"Gene": "Gene_HGNC"})

    return cnv_prot_df, t_test_stats_df, linear_regression_df

cnv_prot_df, t_test_stats_df, linear_regression_df = load_data()

# Sidebar
st.sidebar.title("Settings")
mode = st.sidebar.radio("Select Analysis Mode:", ["T-test + Cohen's d", "Linear Regression", "Advanced Mode"])
if mode == "Advanced Mode":
    comp_mode = "Single Gene"  # Force single gene mode
else:
    comp_mode = st.sidebar.radio("Comparison Mode:", ["Single Gene", "Compare Two Genes"])

if mode != "Advanced Mode":
    p_thresh = st.sidebar.slider("P-value cutoff", 0.0, 0.1, 0.05, 0.005)

# Filter gene list
if mode == "T-test + Cohen's d":
    stats_df = t_test_stats_df[
    (t_test_stats_df["P-value (Amplification vs Neutral)"] < p_thresh) |
    (t_test_stats_df["P-value (Deletion vs Neutral)"] < p_thresh)
    ]
    stats_df = stats_df.dropna(subset=["Gene_HGNC"])
    gene_list = sorted(stats_df["Gene_HGNC"].unique())

elif mode == "Linear Regression":
    stats_df = linear_regression_df.dropna(subset=["P-value"])
    stats_df = stats_df[stats_df["P-value"] < p_thresh]
    gene_list = sorted(stats_df["Gene_HGNC"].unique())

else:  # Advanced Mode
    stats_df = cnv_prot_df[["Gene_HGNC"]].drop_duplicates()
    gene_list = sorted(stats_df["Gene_HGNC"].unique())

# Sidebar gene selection
if comp_mode == "Single Gene":
    if mode == "Advanced Mode":
        gene_cna = st.sidebar.selectbox("Select gene for CNA", gene_list, key="gene_cna")
        gene_prot = st.sidebar.selectbox("Select gene for Protein", gene_list, key="gene_prot")
    else:
        gene = st.sidebar.selectbox("Choose a gene", gene_list)
else:
    gene1 = st.sidebar.selectbox("Choose Gene A:", gene_list, index=0)
    gene2 = st.sidebar.selectbox("Choose Gene B:", gene_list, index=1 if len(gene_list) > 1 else 0)

# Plotting functions
def plot_boxplot(gene, data):
    gene_df = data[data["Gene_HGNC"] == gene].copy()
    gene_df["Protein"] = pd.to_numeric(gene_df["Protein"], errors="coerce")
    gene_df["CNA"] = pd.to_numeric(gene_df["CNA"], errors="coerce")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(
    x="CNA", 
    y="Protein", 
    data=gene_df, 
    order=[-2, -1, 0, 1, 2],  # Ensure GISTIC CNA order
    showfliers=False, 
    palette="Blues", 
    ax=ax
    )
    ax.set_title(f"Protein Expression vs CNA for {gene}")
    ax.yaxis.set_major_locator(plt.MaxNLocator(6))
    st.pyplot(fig)

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    st.download_button(
        label="Download Plot",
        data=buf.getvalue(),
        file_name=f"{gene}_boxplot.png",
        mime="image/png"
    )

def plot_regression(gene, data):
    gene_df = data[data["Gene_HGNC"] == gene].copy()
    gene_df["Protein"] = pd.to_numeric(gene_df["Protein"], errors="coerce")
    gene_df = gene_df.dropna(subset=["CNA", "Protein"])
    gene_df["CNA"] = gene_df["CNA"].astype(float)
    gene_df["Protein"] = gene_df["Protein"].astype(float)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(x="CNA", y="Protein", data=gene_df, ax=ax)
    sns.regplot(x="CNA", y="Protein", data=gene_df, scatter=False, ax=ax, color="red")
    ax.set_title(f"Protein Expression vs CNA with Regression Line for {gene}")
    ax.set_xticks(sorted(gene_df["CNA"].dropna().unique()))
    st.pyplot(fig)

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    st.download_button(
        label="Download Plot",
        data=buf.getvalue(),
        file_name=f"{gene}_regression.png",
        mime="image/png"
    )

# Main content
if mode == "T-test + Cohen's d":
    if comp_mode == "Single Gene":
        st.title(f"Gene: {gene}")
        gene_stats = t_test_stats_df[t_test_stats_df["Gene_HGNC"] == gene].iloc[0]
        st.markdown("### Statistical Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**T-statistic (Amplification vs Neutral):** {gene_stats['T-statistic (Amplification vs Neutral)']:.3f}")
            st.write(f"**P-value (Amplification vs Neutral):** {gene_stats['P-value (Amplification vs Neutral)']:.2e}")
            st.write(f"**Cohen's d (Amplification vs Neutral):** {gene_stats['Cohen\'s d (Amplification vs Neutral)']:.3f}")
        with col2:
            st.write(f"**T-statistic (Deletion vs Neutral):** {gene_stats['T-statistic (Deletion vs Neutral)']:.3f}")
            st.write(f"**P-value (Deletion vs Neutral):** {gene_stats['P-value (Deletion vs Neutral)']:.2e}")
            st.write(f"**Cohen's d (Deletion vs Neutral):** {gene_stats['Cohen\'s d (Deletion vs Neutral)']:.3f}")
        st.markdown("### Protein Expression by CNA GISTIC Score")
        plot_boxplot(gene, cnv_prot_df)

    else:
        st.title("Compare Two Genes")
        col1, col2 = st.columns(2)
        for col, g in zip([col1, col2], [gene1, gene2]):
            gene_stats = t_test_stats_df[t_test_stats_df["Gene_HGNC"] == g].iloc[0]
            col.markdown(f"### {g}")
            col.write(f"**T-statistic (Amplification vs Neutral):** {gene_stats['T-statistic (Amplification vs Neutral)']:.3f}")
            col.write(f"**P-value (Amplification vs Neutral):** {gene_stats['P-value (Amplification vs Neutral)']:.2e}")
            col.write(f"**Cohen's d (Amplification vs Neutral):** {gene_stats['Cohen\'s d (Amplification vs Neutral)']:.3f}")
            col.write(f"**T-statistic (Deletion vs Neutral):** {gene_stats['T-statistic (Deletion vs Neutral)']:.3f}")
            col.write(f"**P-value (Deletion vs Neutral):** {gene_stats['P-value (Deletion vs Neutral)']:.2e}")
            col.write(f"**Cohen's d (Deletion vs Neutral):** {gene_stats['Cohen\'s d (Deletion vs Neutral)']:.3f}")
        st.markdown("### Protein Expression by CNA GISTIC Score")
        plot_col1, plot_col2 = st.columns(2)
        for plot_col, g in zip([plot_col1, plot_col2], [gene1, gene2]):
            with plot_col:
                plot_boxplot(g, cnv_prot_df)

elif mode == "Linear Regression":
    if comp_mode == "Single Gene":
        st.title(f"Gene: {gene}")
        gene_stats = linear_regression_df[linear_regression_df["Gene_HGNC"] == gene].iloc[0]
        st.markdown("### Linear Regression Summary")
        st.write(f"**Regression Coefficient:** {gene_stats['Regression Coefficient (Effect Size)']:.3f}")
        st.write(f"**P-value:** {gene_stats['P-value']:.2e}")
        st.write(f"**R-squared:** {gene_stats['R-squared']:.3f}")
        st.markdown("### Protein Expression vs CNA with Regression Line")
        plot_regression(gene, cnv_prot_df)
    else:
        st.title("Compare Two Genes")
        col1, col2 = st.columns(2)
        for col, g in zip([col1, col2], [gene1, gene2]):
            gene_stats = linear_regression_df[linear_regression_df["Gene_HGNC"] == g].iloc[0]
            col.markdown(f"### {g}")
            col.write(f"**Regression Coefficient:** {gene_stats['Regression Coefficient (Effect Size)']:.3f}")
            col.write(f"**P-value:** {gene_stats['P-value']:.2e}")
            col.write(f"**R-squared:** {gene_stats['R-squared']:.3f}")
        st.markdown("### Protein Expression vs CNA with Regression Line")
        plot_col1, plot_col2 = st.columns(2)
        for plot_col, g in zip([plot_col1, plot_col2], [gene1, gene2]):
            with plot_col:
                plot_regression(g, cnv_prot_df)

else:  # Advanced Mode
    st.title("🔍 Advanced Mode: Explore Any Gene Pair")

    df_cna = cnv_prot_df[cnv_prot_df["Gene_HGNC"] == gene_cna][["Sample", "CNA"]].rename(columns={"CNA": "CNA_val"})
    df_prot = cnv_prot_df[cnv_prot_df["Gene_HGNC"] == gene_prot][["Sample", "Protein"]].rename(columns={"Protein": "Prot_val"})

    merged = pd.merge(df_cna, df_prot, on="Sample").dropna()
    merged["CNA_val"] = pd.to_numeric(merged["CNA_val"], errors="coerce")
    merged["Prot_val"] = pd.to_numeric(merged["Prot_val"], errors="coerce")
    merged = merged.dropna()

    if len(merged) < 6:
        st.warning("Not enough samples with data for both genes.")
    else:
        slope, intercept, r_value, p_value, std_err = linregress(merged["CNA_val"], merged["Prot_val"])
        st.markdown("### Cross-Gene Regression Summary")
        st.write(f"**CNA Gene:** {gene_cna}")
        st.write(f"**Protein Gene:** {gene_prot}")
        st.write(f"**Regression coefficient (slope):** {slope:.3f}")
        st.write(f"**P-value:** {p_value:.2e}")
        st.write(f"**R-squared:** {r_value**2:.3f}")

        fig, ax = plt.subplots(figsize=(8, 5))

        # Set consistent GISTIC order
        merged["CNA_val"] = pd.Categorical(merged["CNA_val"], categories=[-2, -1, 0, 1, 2], ordered=True)

        sns.regplot(
            x="CNA_val",
            y="Prot_val",
            data=merged,
            scatter=True,
            ci=95,
            line_kws={"color": "red", "linewidth": 2},
            scatter_kws={"s": 40, "alpha": 0.7, "color": "steelblue"},
            ax=ax
        )

        ax.set_title(f"Protein Expression vs CNA for {gene_prot}", fontsize=12)
        ax.set_xlabel(f"CNA (GISTIC Score) for {gene_cna}", fontsize=11)
        ax.set_ylabel(f"Protein Expression (log ratio) for {gene_prot}", fontsize=11)
        ax.set_xticks([-2, -1, 0, 1, 2])
        ax.tick_params(axis='both', labelsize=10)

        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        st.download_button(
            label="Download Plot",
            data=buf.getvalue(),
            file_name=f"{gene_cna}_{gene_prot}_advanced_regression.png",
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