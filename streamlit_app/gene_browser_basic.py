import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load your merged dataframe
merged_df = pd.read_csv("../results/cnv_prot_boxplot.csv")

# Dropdown for gene selection
gene = st.selectbox("Select a gene:", merged_df["Gene"].unique())

# Filter data
gene_df = merged_df[merged_df["Gene"] == gene]

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(x="CNA", y="Protein", data=gene_df, showfliers=False, ax=ax)
ax.set_title(f"Protein vs CNA for {gene}")
st.pyplot(fig)
