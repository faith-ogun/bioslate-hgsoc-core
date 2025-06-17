import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="Gene Biomarker Explorer", layout="wide")

# Load data - GitHub
merged_df = pd.read_csv("streamlit_app/data/cnv_prot_boxplot.csv")
stats_df = pd.read_csv("streamlit_app/data/per_gene_stats_filtered.csv")

# Sidebar: filtering
st.sidebar.title("🔍 Filter Options")
p_thresh = st.sidebar.slider("P-value cutoff", 0.0, 0.1, 0.05, 0.005)
d_thresh = st.sidebar.slider("Effect size (Cohen’s d)", 0.0, 2.0, 0.3, 0.1)

# Drop NaN values
filtered_stats = stats_df.dropna(subset=[
    "P-value (Amplification vs Neutral)", 
    "P-value (Deletion vs Neutral)",
    "Cohen's d (Amplification vs Neutral)",
    "Cohen's d (Deletion vs Neutral)"
])

# Filtering criteria
filtered_stats = filtered_stats[
    ((filtered_stats["P-value (Amplification vs Neutral)"] < p_thresh) & 
     (filtered_stats["Cohen's d (Amplification vs Neutral)"].abs() >= d_thresh)) |
    ((filtered_stats["P-value (Deletion vs Neutral)"] < p_thresh) & 
     (filtered_stats["Cohen's d (Deletion vs Neutral)"].abs() >= d_thresh))
]

# Find the more significant p-value
filtered_stats["Min P-value"] = filtered_stats[[
    "P-value (Amplification vs Neutral)", 
    "P-value (Deletion vs Neutral)"
]].min(axis=1)
filtered_stats = filtered_stats.sort_values("Min P-value")

# Choose comparison mode
mode = st.sidebar.radio("Mode:", ["Single Gene", "Compare Two Genes"])

if mode == "Single Gene":
    gene_list = filtered_stats["Gene"].tolist()
    gene = st.sidebar.selectbox("Choose a gene:", gene_list)

    gene_df = merged_df[merged_df["Gene"] == gene]
    gene_stats = stats_df[stats_df["Gene"] == gene].iloc[0]

    st.title(f"🧬 Gene: {gene}")
    st.markdown("### 📊 Statistical Summary")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**T-stat (Amp vs Neutral):** {gene_stats['T-statistic (Amplification vs Neutral)']:.3f}")
        st.write(f"**P-value (Amp vs Neutral):** {gene_stats['P-value (Amplification vs Neutral)']:.2e}")
        st.write(f"**Cohen's d (Amp vs Neutral):** {gene_stats['Cohen\'s d (Amplification vs Neutral)']:.3f}")
    with col2:
        st.write(f"**T-stat (Del vs Neutral):** {gene_stats['T-statistic (Deletion vs Neutral)']:.3f}")
        st.write(f"**P-value (Del vs Neutral):** {gene_stats['P-value (Deletion vs Neutral)']:.2e}")
        st.write(f"**Cohen's d (Del vs Neutral):** {gene_stats['Cohen\'s d (Deletion vs Neutral)']:.3f}")

    st.markdown("### 🧪 Protein Expression by CNA GISTIC Score")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(x="CNA", y="Protein", data=gene_df, showfliers=False, palette="Set1", ax=ax, legend=False, hue="CNA")
    ax.set_title(f"Protein Expression vs CNA for {gene}")
    st.pyplot(fig)

else:
    gene_list = filtered_stats["Gene"].tolist()
    gene1 = st.sidebar.selectbox("Gene A", gene_list, index=0)
    gene2 = st.sidebar.selectbox("Gene B", gene_list, index=1 if len(gene_list) > 1 else 0)

    col1, col2 = st.columns(2)

    # Loop through two columns (col1, col2) and the selected genes (gene1, gene2)
    for col, gene in zip([col1, col2], [gene1, gene2]):
    # Filter merged_df to get data for the current gene
        gene_df = merged_df[merged_df["Gene"] == gene]
    
    # Get the stats row for the current gene
        gene_stats = stats_df[stats_df["Gene"] == gene].iloc[0]

        col.markdown(f"### 🧬 {gene}")
        col.write(f"**T-stat (Amp vs Neutral):** {gene_stats['T-statistic (Amplification vs Neutral)']:.3f}")
        col.write(f"**P-value (Amp vs Neutral):** {gene_stats['P-value (Amplification vs Neutral)']:.2e}")
        col.write(f"**Cohen's d (Amp vs Neutral):** {gene_stats['Cohen\'s d (Amplification vs Neutral)']:.3f}")
        col.write(f"**T-stat (Del vs Neutral):** {gene_stats['T-statistic (Deletion vs Neutral)']:.3f}")
        col.write(f"**P-value (Del vs Neutral):** {gene_stats['P-value (Deletion vs Neutral)']:.2e}")
        col.write(f"**Cohen's d (Del vs Neutral):** {gene_stats['Cohen\'s d (Deletion vs Neutral)']:.3f}")

    st.markdown("### 📊 Side-by-side Boxplots")
    plot_col1, plot_col2 = st.columns(2)

    for plot_col, gene in zip([plot_col1, plot_col2], [gene1, gene2]):
        gene_df = merged_df[merged_df["Gene"] == gene]
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(x="CNA", y="Protein", data=gene_df, showfliers=False, palette="Set1", ax=ax, legend=False, hue="CNA")
        ax.set_title(f"{gene}")
        ax.set_xlabel("CNA GISTIC Score")
        ax.set_ylabel("Protein Expression")
        plot_col.pyplot(fig)

# Footer
st.markdown("---")
st.markdown("🔬 Built for **BioSLATE**, in collaboration with **Breakthrough Cancer Research**")
