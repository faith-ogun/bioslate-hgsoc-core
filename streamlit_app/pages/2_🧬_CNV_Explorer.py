import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# Page config
st.set_page_config(
    page_title="CNV Explorer | BioSLATE",
    layout="wide",
)

st.title("🧬 DepMap CNV Explorer — Amplification & Deletion Calls")
st.caption("Last updated: June 2025")

# --- Load Data ---
@st.cache_data
def load_cnv_data():
    df = pd.read_csv("streamlit_app/data/cna_depmap_hgsoc.csv", index_col=0)
    return df

cna_df = load_cnv_data()  # rows: cell lines, columns: genes

# --- Sidebar Threshold Inputs ---
st.sidebar.header("🛠 Threshold Settings")

amp_threshold = st.sidebar.number_input(
    "High-level Amplification Threshold (CN >)",
    min_value=3.0, max_value=10.0, value=4.0, step=0.1
)
del_threshold = st.sidebar.number_input(
    "Deep Deletion Threshold (CN <)",
    min_value=0.0, max_value=3.0, value=1.0, step=0.1
)

min_cell_lines = st.sidebar.slider(
    "Minimum # of Cell Lines per Gene (for Amplified/Deleted)",
    min_value=1, max_value=len(cna_df), value=5
)

# --- Flatten for Histogram ---
flattened_values = cna_df.to_numpy().flatten()
num_deletions = np.sum(flattened_values < del_threshold)
num_amplifications = np.sum(flattened_values > amp_threshold)

# --- Histogram Plot ---
st.subheader("📊 Absolute CN Value Distribution")
fig, ax = plt.subplots()
ax.hist(flattened_values, bins=50, color="blue", edgecolor="black", alpha=0.7)
ax.axvline(x=del_threshold, color="red", linestyle="--", label=f"Deletion Threshold ({del_threshold})")
ax.axvline(x=amp_threshold, color="green", linestyle="--", label=f"Amplification Threshold ({amp_threshold})")
ax.set_title("Absolute Copy Number Frequencies")
ax.set_xlabel("Absolute CN Value")
ax.set_ylabel("Frequency")
ax.set_xlim(0, 15)
ax.legend()
st.pyplot(fig)

# --- Display Summary Stats ---
st.markdown(f"""
### 📌 Threshold Summary:
- **Deep deletions (< {del_threshold}):** {num_deletions:,}
- **Amplifications (> {amp_threshold}):** {num_amplifications:,}
- **Total Cell Lines:** {len(cna_df)}
- **Total Genes:** {len(cna_df.columns)}
""")

# --- Count Amplified / Deleted Genes ---
amplified_counts = (cna_df > amp_threshold).sum(axis=0)
deleted_counts = (cna_df < del_threshold).sum(axis=0)

amp_genes = amplified_counts[amplified_counts >= min_cell_lines].sort_values(ascending=False)
del_genes = deleted_counts[deleted_counts >= min_cell_lines].sort_values(ascending=False)

# --- Display Tables ---
st.subheader(f"🔥 Amplified Genes (≥ {min_cell_lines} cell lines)")
st.dataframe(amp_genes.to_frame("Amplified Cell Line Count"))

st.subheader(f"❄️ Deleted Genes (≥ {min_cell_lines} cell lines)")
st.dataframe(del_genes.to_frame("Deleted Cell Line Count"))

# --- Download Buttons ---
def convert_df_to_csv(df):
    return df.to_csv(index=True).encode("utf-8")

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        label="⬇️ Download Amplified Genes CSV",
        data=convert_df_to_csv(amp_genes.to_frame("Amplified Cell Line Count")),
        file_name="amplified_genes_depmap.csv",
        mime="text/csv"
    )
with col2:
    st.download_button(
        label="⬇️ Download Deleted Genes CSV",
        data=convert_df_to_csv(del_genes.to_frame("Deleted Cell Line Count")),
        file_name="deleted_genes_depmap.csv",
        mime="text/csv"
    )

# --- Markdown Explainer ---
with st.expander("📚 What do these thresholds mean?"):
    st.markdown("""
**Thresholds are inspired by GISTIC-like CNV scoring.**

| CNV Category            | Absolute CN Range | GISTIC-Like Score | Interpretation                    |
|------------------------|-------------------|-------------------|-----------------------------------|
| Deep deletion          | < 1               | –2                | Likely homozygous deletion        |
| Shallow deletion       | 1.0 – 1.5         | –1                | Single-copy loss                  |
| Diploid (neutral)      | 1.5 – 2.5         | 0                 | Normal copy number                |
| Low-level gain         | 2.5 – 4.0         | +1                | Extra copy (non-focal amp)        |
| High-level amplification | ≥ 4.0           | +2                | Strong focal amplification        |

These thresholds are adjustable in the sidebar to explore how amplification and deletion counts change.
""")
