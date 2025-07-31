import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np
import io

# Page config
st.set_page_config(page_title="BioSLATE Gene–Protein Explorer", layout="wide")
st.title("Interactive Viewer of CNA and Protein Expression Dynamics")
st.caption("Last updated: July 13th 2025")

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
    stats_df = t_test_stats_df.dropna(subset=[
        "P-value (Amplification vs Neutral)", "P-value (Deletion vs Neutral)",
        "Cohen's d (Amplification vs Neutral)", "Cohen's d (Deletion vs Neutral)"])
    stats_df = stats_df[
        (stats_df["P-value (Amplification vs Neutral)"] < p_thresh) |
        (stats_df["P-value (Deletion vs Neutral)"] < p_thresh)]
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
        sns.scatterplot(x="CNA_val", y="Prot_val", data=merged, ax=ax)
        x_vals = np.array(ax.get_xlim())
        y_vals = intercept + slope * x_vals
        ax.plot(x_vals, y_vals, color="red")
        ax.set_title(f"CNA of {gene_cna} vs Protein of {gene_prot}")
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        st.download_button(
            label="Download Plot",
            data=buf.getvalue(),
            file_name=f"{gene_cna}_{gene_prot}_advanced_regression.png",
            mime="image/png"
        )

# Footer
st.markdown("---")
st.markdown("🔬 Built for **BioSLATE**, in collaboration with **Breakthrough Cancer Research**")