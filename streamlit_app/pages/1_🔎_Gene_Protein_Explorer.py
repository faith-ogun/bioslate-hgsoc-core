import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np
import io

# Page config
st.set_page_config(page_title="BioSLATE Gene–Protein Explorer", layout="wide")

@st.cache_data
def load_data():
    cnv_prot_df = pd.read_csv("streamlit_app/data/cnv_prot_boxplot.csv")
    t_test_stats_df = pd.read_csv("streamlit_app/data/per_gene_stats_filtered.csv")
    linear_regression_df = pd.read_csv("streamlit_app/data/per_gene_linear_regression.csv")
    return cnv_prot_df, t_test_stats_df, linear_regression_df

cnv_prot_df, t_test_stats_df, linear_regression_df = load_data()

# Sidebar
st.sidebar.title("Settings")
mode = st.sidebar.radio("Select Analysis Mode:", ["T-test + Cohen's d", "Linear Regression", "Advanced Mode"])
if mode == "Advanced Mode":
    comp_mode = "Single Gene"
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
elif mode == "Linear Regression":
    stats_df = linear_regression_df.dropna(subset=["P-value"])
    stats_df = stats_df[stats_df["P-value"] < p_thresh]
else:
    stats_df = cnv_prot_df[["Gene"]].drop_duplicates()

gene_list = sorted(stats_df["Gene"].unique())

# Sidebar gene selection
if comp_mode == "Single Gene":
    if mode == "Advanced Mode":
        gene_cna = st.sidebar.selectbox("Select gene for CNA (Entrez ID)", gene_list, key="gene_cna")
        gene_prot = st.sidebar.selectbox("Select gene for Protein (Entrez ID)", gene_list, key="gene_prot")
    else:
        gene = st.sidebar.selectbox("Choose a gene (Entrez ID)", gene_list)
else:
    gene1 = st.sidebar.selectbox("Choose Gene A (Entrez ID):", gene_list, index=0)
    gene2 = st.sidebar.selectbox("Choose Gene B (Entrez ID):", gene_list, index=1 if len(gene_list) > 1 else 0)

# Define alternating blue palette
custom_palette = {
    -2: "#198ae5",
    -1: "#75b9eb",
     0: "#198ae5",
     1: "#75b9eb",
     2: "#198ae5"
}

# Plotting functions
def plot_boxplot(gene, data):
    gene_df = data[data["Gene"] == gene].copy()
    gene_df["Protein"] = pd.to_numeric(gene_df["Protein"], errors="coerce")
    gene_df["CNA"] = pd.to_numeric(gene_df["CNA"], errors="coerce").astype("Int64")

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(x="CNA", y="Protein", data=gene_df, showfliers=False, palette=custom_palette, ax=ax)
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
    gene_df = data[data["Gene"] == gene].copy()
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

# Footer
st.markdown("---")
st.markdown("🔬 Built for **BioSLATE**, in collaboration with **Breakthrough Cancer Research**")
