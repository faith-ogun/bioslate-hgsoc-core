import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm

# Page config
st.set_page_config(page_title="BioSLATE Gene-Protein Explorer", layout="wide")

# Load datasets once
@st.cache_data
def load_data():
    cnv_prot_df = pd.read_csv("streamlit_app/data/cnv_prot_boxplot.csv")
    t_test_stats_df = pd.read_csv("streamlit_app/data/per_gene_stats_filtered.csv")
    linear_regression_df = pd.read_csv("streamlit_app/data/per_gene_linear_regression.csv")
    return cnv_prot_df, t_test_stats_df, linear_regression_df

cnv_prot_df, t_test_stats_df, linear_regression_df = load_data()

# Sidebar controls
st.sidebar.title("Settings")

mode = st.sidebar.radio("Select Analysis Mode:", ["T-test + Cohen's d", "Linear Regression", "Advanced Mode"])

p_thresh = st.sidebar.slider("P-value cutoff", 0.0, 0.1, 0.05, 0.005)

comp_mode = st.sidebar.radio("Comparison Mode:", ["Single Gene", "Compare Two Genes"])

# Prepare filtered stats based on mode and p-value cutoff
if mode == "T-test + Cohen's d":
    filtered_stats = t_test_stats_df.dropna(subset=[
        "P-value (Amplification vs Neutral)", "P-value (Deletion vs Neutral)",
        "Cohen's d (Amplification vs Neutral)", "Cohen's d (Deletion vs Neutral)"])
    filtered_stats = filtered_stats[
        (filtered_stats["P-value (Amplification vs Neutral)"] < p_thresh) |
        (filtered_stats["P-value (Deletion vs Neutral)"] < p_thresh)]
elif mode == "Linear Regression":
    filtered_stats = linear_regression_df.dropna(subset=["P-value"])
    filtered_stats = filtered_stats[linear_regression_df["P-value"] < p_thresh]
else:
    filtered_stats = None  # No filtering in Advanced Mode

# Determine gene lists for selectors
if filtered_stats is not None:
    gene_list = filtered_stats["Gene"].tolist()
else:
    gene_list = cnv_prot_df["Gene"].unique().tolist()

# Sidebar gene selectors
if comp_mode == "Single Gene":
    gene = st.sidebar.selectbox("Choose a gene:", gene_list)
else:
    gene1 = st.sidebar.selectbox("Choose Gene A:", gene_list, index=0)
    gene2 = st.sidebar.selectbox("Choose Gene B:", gene_list, index=1 if len(gene_list) > 1 else 0)
