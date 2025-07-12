import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from io import BytesIO

# --- Page setup ---
st.set_page_config(page_title="SL Target Drug Sensitivity", layout="wide")
st.title("Expression–Drug Sensitivity Validation of SL Targets")
st.caption("Validating Synthetic Lethal Targets Via Expression–AUC Correlation in HGSOC\nLast Updated: July 12th 2025")

# --- Load data ---
@st.cache_data(show_spinner=False)
def load_all_top_hits():
    pi4kb = pd.read_csv("streamlit_app/data/pi4kb_hgsoc_top_drug_hits.csv")
    spag5 = pd.read_csv("streamlit_app/data/spag5_hgsoc_top_drug_hits.csv")
    ythdc1 = pd.read_csv("streamlit_app/data/ythdc1_hgsoc_top_drug_hits.csv")
    pi4kb["Gene"] = "PI4KB"
    spag5["Gene"] = "SPAG5"
    ythdc1["Gene"] = "YTHDC1"
    return pd.concat([pi4kb, spag5, ythdc1])

@st.cache_data(show_spinner=False)
def load_raw_data():
    expr = pd.read_csv("streamlit_app/data/expression_hgsoc.csv", index_col=0)
    auc = pd.read_csv("streamlit_app/data/gdsc_hgsoc.csv", index_col=0)
    return expr, auc

top_hits_df = load_all_top_hits()
expression_df, gdsc_df = load_raw_data()

# --- Sidebar filters ---
st.sidebar.title("Plot Options")
selected_gene = st.sidebar.selectbox("Select SL Target Gene", sorted(top_hits_df["Gene"].unique()))
filtered_hits = top_hits_df[top_hits_df["Gene"] == selected_gene]
selected_drug = st.sidebar.selectbox("Select Drug", sorted(filtered_hits["Drug"].unique()))

# --- Plot section ---
st.subheader(f"{selected_drug} sensitivity vs {selected_gene} expression")

# Get AUC values for selected drug
drug_data = gdsc_df[gdsc_df["DRUG_NAME"] == selected_drug][["AUC_PUBLISHED"]].copy()
expr_data = expression_df[selected_gene]

# Merge
merged = drug_data.merge(expr_data, left_index=True, right_index=True)
merged = merged.dropna(subset=["AUC_PUBLISHED", selected_gene])

if merged.shape[0] < 3:
    st.warning("Not enough overlapping HGSOC cell lines for correlation.")
else:
    r, p = pearsonr(merged[selected_gene], merged["AUC_PUBLISHED"])

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.regplot(
        data=merged, x=selected_gene, y="AUC_PUBLISHED",
        scatter_kws={'s': 60, 'alpha': 0.8}, line_kws={'color': 'black'}
    )
    ax.set_title(f"{selected_drug} vs {selected_gene} Expression\nPearson r = {r:.2f}, p = {p:.3g}")
    ax.set_xlabel(f"{selected_gene} Expression (log1p TPM)")
    ax.set_ylabel("AUC (Drug Sensitivity)")
    ax.axhline(0, linestyle="--", color="gray", linewidth=1)
    st.pyplot(fig)

    # Download option
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300)
    st.download_button(
        label="⬇️ Download Plot (.png)",
        data=buf.getvalue(),
        file_name=f"{selected_gene}_{selected_drug}_scatter.png",
        mime="image/png"
    )

# --- Data table ---
with st.expander("📊 Show All Top Hits Table"):
    st.dataframe(top_hits_df.sort_values("P_value"), use_container_width=True)
    csv = top_hits_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Full Table (.csv)", csv, "all_top_hits_drugs.csv", mime="text/csv")
