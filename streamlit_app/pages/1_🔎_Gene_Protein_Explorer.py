from io import BytesIO
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np

st.set_page_config(page_title="BioSLATE Gene-Protein Explorer", layout="wide")

@st.cache_data
def load_data():
    cnv_prot_df = pd.read_csv("streamlit_app/data/cnv_prot_boxplot.csv")
    t_test_stats_df = pd.read_csv("streamlit_app/data/per_gene_stats_filtered.csv")
    linear_regression_df = pd.read_csv("streamlit_app/data/per_gene_linear_regression.csv")
    return cnv_prot_df, t_test_stats_df, linear_regression_df

cnv_prot_df, t_test_stats_df, linear_regression_df = load_data()

st.sidebar.title("Settings")
st.sidebar.markdown("### Select gene by Entrez ID")

mode = st.sidebar.radio("Select Analysis Mode:", ["T-test + Cohen's d", "Linear Regression", "Advanced Mode"])
p_thresh = st.sidebar.slider("P-value cutoff", 0.0, 0.1, 0.05, 0.005)
comp_mode = st.sidebar.radio("Comparison Mode:", ["Single Gene", "Compare Two Genes"])

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
    filtered_stats = None

gene_list = filtered_stats["Gene"].tolist() if filtered_stats is not None else cnv_prot_df["Gene"].unique().tolist()

if comp_mode == "Single Gene":
    gene = st.sidebar.selectbox("Choose a gene (Entrez ID):", gene_list)
else:
    gene1 = st.sidebar.selectbox("Choose Gene A (Entrez ID):", gene_list, index=0)
    gene2 = st.sidebar.selectbox("Choose Gene B (Entrez ID):", gene_list, index=1 if len(gene_list) > 1 else 0)

def download_button(fig, filename, label="Download plot"):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    st.download_button(label=label, data=buf, file_name=filename, mime="image/png", use_container_width=True)

def plot_boxplot(gene, data):
    gene_df = data[data["Gene"] == gene].copy()
    gene_df["Protein"] = pd.to_numeric(gene_df["Protein"], errors="coerce")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(x="CNA", y="Protein", data=gene_df, showfliers=False, palette="Set1", ax=ax)
    ax.set_title(f"Protein Expression vs CNA for {gene}")
    ax.yaxis.set_major_locator(plt.MaxNLocator(6))
    st.pyplot(fig)
    download_button(fig, f"{gene}_boxplot.png", label="Download Plot")

def plot_regression(gene, data):
    gene_df = data[data["Gene"] == gene].copy()
    gene_df["CNA"] = pd.to_numeric(gene_df["CNA"], errors="coerce")
    gene_df["Protein"] = pd.to_numeric(gene_df["Protein"], errors="coerce")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(x="CNA", y="Protein", data=gene_df, ax=ax)
    sns.regplot(x="CNA", y="Protein", data=gene_df, scatter=False, ax=ax, color="red")
    ax.set_title(f"Protein Expression vs CNA with Regression Line for {gene}")
    st.pyplot(fig)
    download_button(fig, f"{gene}_regression.png", label="Download Plot")

if mode == "T-test + Cohen's d":
    if comp_mode == "Single Gene":
        gene_stats = t_test_stats_df[t_test_stats_df["Gene"] == gene].iloc[0]
        st.title(f"🧬 Gene: {gene}")
        st.markdown("### 📊 Statistical Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**T-statistic (Amplification vs Neutral):** {gene_stats['T-statistic (Amplification vs Neutral)']:.3f}")
            st.write(f"**P-value (Amplification vs Neutral):** {gene_stats['P-value (Amplification vs Neutral)']:.2e}")
            st.write(f"**Effect size (Cohen's d):** {gene_stats['Cohen\'s d (Amplification vs Neutral)']:.3f}")
        with col2:
            st.write(f"**T-statistic (Deletion vs Neutral):** {gene_stats['T-statistic (Deletion vs Neutral)']:.3f}")
            st.write(f"**P-value (Deletion vs Neutral):** {gene_stats['P-value (Deletion vs Neutral)']:.2e}")
            st.write(f"**Effect size (Cohen's d):** {gene_stats['Cohen\'s d (Deletion vs Neutral)']:.3f}")
        st.markdown("### 🧪 Protein Expression by CNA GISTIC Score")
        plot_boxplot(gene, cnv_prot_df)

    else:
        col1, col2 = st.columns(2)
        for col, g in zip([col1, col2], [gene1, gene2]):
            gene_stats = t_test_stats_df[t_test_stats_df["Gene"] == g].iloc[0]
            col.markdown(f"### 🧬 {g}")
            col.write(f"**T-statistic (Amp vs Neutral):** {gene_stats['T-statistic (Amplification vs Neutral)']:.3f}")
            col.write(f"**P-value (Amp vs Neutral):** {gene_stats['P-value (Amplification vs Neutral)']:.2e}")
            col.write(f"**Cohen's d (Amp):** {gene_stats['Cohen\'s d (Amplification vs Neutral)']:.3f}")
            col.write(f"**T-statistic (Del vs Neutral):** {gene_stats['T-statistic (Deletion vs Neutral)']:.3f}")
            col.write(f"**P-value (Del vs Neutral):** {gene_stats['P-value (Deletion vs Neutral)']:.2e}")
            col.write(f"**Cohen's d (Del):** {gene_stats['Cohen\'s d (Deletion vs Neutral)']:.3f}")
        pc1, pc2 = st.columns(2)
        with pc1:
            plot_boxplot(gene1, cnv_prot_df)
        with pc2:
            plot_boxplot(gene2, cnv_prot_df)

elif mode == "Linear Regression":
    if comp_mode == "Single Gene":
        gene_stats = linear_regression_df[linear_regression_df["Gene"] == gene].iloc[0]
        st.title(f"🧬 Gene: {gene}")
        st.markdown("### 📊 Linear Regression Summary")
        st.write(f"**Regression Coefficient:** {gene_stats['Regression Coefficient (Effect Size)']:.3f}")
        st.write(f"**P-value:** {gene_stats['P-value']:.2e}")
        st.write(f"**Sample Size:** {gene_stats['Sample Size']}")
        st.write(f"**R-squared:** {gene_stats['R-squared']:.3f}")
        st.markdown("### 🧪 Regression Plot")
        plot_regression(gene, cnv_prot_df)

    else:
        col1, col2 = st.columns(2)
        for col, g in zip([col1, col2], [gene1, gene2]):
            gene_stats = linear_regression_df[linear_regression_df["Gene"] == g].iloc[0]
            col.markdown(f"### 🧬 {g}")
            col.write(f"**Regression Coefficient:** {gene_stats['Regression Coefficient (Effect Size)']:.3f}")
            col.write(f"**P-value:** {gene_stats['P-value']:.2e}")
            col.write(f"**Sample Size:** {gene_stats['Sample Size']}")
            col.write(f"**R-squared:** {gene_stats['R-squared']:.3f}")
        pc1, pc2 = st.columns(2)
        with pc1:
            plot_regression(gene1, cnv_prot_df)
        with pc2:
            plot_regression(gene2, cnv_prot_df)

else:
    st.title("Advanced Mode: CNA vs Protein Correlation")
    gene_cna = st.selectbox("Select Gene for CNA:", cnv_prot_df["Gene"].unique())
    gene_prot = st.selectbox("Select Gene for Protein:", cnv_prot_df["Gene"].unique())

    df_cna = cnv_prot_df[cnv_prot_df["Gene"] == gene_cna][["Sample", "CNA"]].copy()
    df_prot = cnv_prot_df[cnv_prot_df["Gene"] == gene_prot][["Sample", "Protein"]].copy()

    # Convert to numeric (important!)
    df_cna["CNA"] = pd.to_numeric(df_cna["CNA"], errors="coerce")
    df_prot["Protein"] = pd.to_numeric(df_prot["Protein"], errors="coerce")

    merged = pd.merge(df_cna, df_prot, on="Sample").dropna()

    if len(merged) < 6:
        st.warning("Not enough samples with data for both genes to perform regression.")
    else:
        slope, intercept, r_value, p_value, std_err = linregress(merged["CNA"], merged["Protein"])
        st.markdown("### 📈 Regression Summary")
        st.write(f"**CNA of {gene_cna} vs Protein of {gene_prot}**")
        st.write(f"**Slope:** {slope:.3f} | **P-value:** {p_value:.2e} | **R-squared:** {r_value**2:.3f}")

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(x="CNA", y="Protein", data=merged, ax=ax)
        x_vals = np.array(ax.get_xlim())
        y_vals = intercept + slope * x_vals
        ax.plot(x_vals, y_vals, color="red")
        ax.set_title(f"CNA of {gene_cna} vs Protein of {gene_prot}")
        st.pyplot(fig)

        # Optional download
        from io import BytesIO
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        st.download_button(
            label="Download Plot",
            data=buf,
            file_name=f"{gene_cna}_{gene_prot}_advanced_regression.png",
            mime="image/png",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown("🔬 Built for **BioSLATE**, in collaboration with **Breakthrough Cancer Research**")
