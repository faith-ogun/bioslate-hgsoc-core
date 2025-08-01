import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import holoviews as hv
from holoviews import opts, dim
from holoviews.element.graphs import Chord
hv.extension('bokeh')
from bokeh.embed import components
from bokeh.resources import CDN
from streamlit.components.v1 import html

# --- Page config ---
st.set_page_config(page_title="PPI & Pathway Analysis of SL Targets", layout="wide")
st.title("Network & Pathway Analysis of Potent Synthetic Lethal Targets")
st.caption("Last updated: August 1st 2025")

# --- Load data ---
@st.cache_data
def load_ppi_and_pathway_data():
    ppi_df = pd.read_csv("streamlit_app/data/potent_hits_STRING_PPI_check.csv")
    gprofiler_df = pd.read_csv("streamlit_app/data/gprofiler_enrichment.csv")
    mapping_df = pd.read_csv("streamlit_app/data/gene_to_pathway_map.csv")
    return ppi_df, gprofiler_df, mapping_df

ppi_df, gprofiler_df, mapping_df = load_ppi_and_pathway_data()

# --- Sidebar radio ---
view_option = st.sidebar.radio(
    "Choose View",
    ["Top Pathways (Barplot)", "Pathway × Gene (Dotplot)", "Pathway Network (Chord Diagram)"]
)

# --- Shared PPI summary section ---
st.subheader("🔗 PPI Check (STRING database)")
n_total = len(ppi_df)
n_with_ppi = ppi_df["PPI_found"].sum()
st.markdown(f"Out of 197 SL pairs, **{n_with_ppi}** show direct STRING-supported protein–protein interactions (combined score ≥ 400).")

with st.expander("📄 View All PPI-Annotated Pairs"):
    st.dataframe(ppi_df, use_container_width=True)
    csv_ppi = ppi_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download PPI Table (.csv)", csv_ppi, "ppi_hits.csv", mime="text/csv")

# --- View 1: Barplot ---
if view_option == "Top Pathways (Barplot)":
    st.subheader("Top Enriched Pathways (g:Profiler)")
    sig = gprofiler_df[gprofiler_df['significant'] == True].copy()
    top = sig.nsmallest(15, 'p_value')

    fig1, ax1 = plt.subplots(figsize=(8, 6))
    sns.barplot(y='name', x=-np.log10(top['p_value']), data=top, color='#235b91', ax=ax1)
    ax1.set_xlabel('-log₁₀(p-value)')
    ax1.set_ylabel('Pathway')
    ax1.set_title('Top 15 Enriched Pathways')
    ax1.invert_yaxis()
    st.pyplot(fig1)

    csv_gprof = gprofiler_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Enrichment Table (.csv)", csv_gprof, "gprofiler_enrichment.csv", mime="text/csv")

# --- View 2: Dotplot ---
elif view_option == "Pathway × Gene (Dotplot)":
    st.subheader("Gene × Pathway Dot Plot")
    sig = gprofiler_df[gprofiler_df['significant'] == True].copy()
    top_pathways = sig.nsmallest(15, 'p_value')["name"].tolist()
    dot_data = mapping_df[mapping_df["Pathway"].isin(top_pathways)]
    dot_matrix = dot_data.groupby(['Pathway', 'Gene']).size().unstack(fill_value=0)

    fig2, ax2 = plt.subplots(figsize=(10, 12))
    sns.heatmap(dot_matrix.T, cmap=sns.color_palette(["white", "#235b91"]),
                cbar=False, linewidths=0.5, linecolor="gray", ax=ax2)
    ax2.set_xlabel("Pathway")
    ax2.set_ylabel("Gene")
    ax2.set_title("Genes Involved in Top 15 Enriched Pathways")
    st.pyplot(fig2)

# --- View 3: Chord diagram ---
elif view_option == "Pathway Network (Chord Diagram)":
    st.subheader("Chord Diagram: Curated Pathway–Gene Network")

    collapse_map = {
        'cell cycle': 'Cell cycle', 'cell cycle process': 'Cell cycle',
        'regulation of cell cycle': 'Cell cycle', 'regulation of cell cycle process': 'Cell cycle',
        'regulation of cell cycle G1/S transition': 'Cell cycle',
        'G1/S transition of mitotic cell cycle': 'Cell cycle',
        'Mitotic G1 phase and G1/S transition': 'Cell cycle',
        'mitotic cell cycle': 'Cell cycle', 'mitotic cell cycle process': 'Cell cycle',
        'Diseases of mitotic cell cycle': 'Cell cycle',
        'Aberrant regulation of mitotic cell cycle due to RB1 defects': 'Cell cycle',
        'Apoptosis': 'Apoptosis', 'apoptotic process': 'Apoptosis',
        'programmed cell death': 'Apoptosis', 'cell death': 'Apoptosis',
        'regulation of apoptotic process': 'Apoptosis',
        'PI3K-Akt signaling pathway': 'PI3K-Akt signaling',
        'mTOR signaling pathway': 'mTOR signaling',
        'FoxO signaling pathway': 'FoxO signaling',
        'VEGF signaling pathway': 'VEGF signaling',
        'Pathways in cancer': 'Pathways in cancer',
        'Breast cancer': 'Breast cancer'
    }

    mapping_df['CollapsedPathway'] = mapping_df['Pathway'].replace(collapse_map)
    keep_terms = set(collapse_map.values())
    subset = mapping_df[mapping_df['CollapsedPathway'].isin(keep_terms)]
    counts = subset['CollapsedPathway'].value_counts()
    valid_pathways = counts[counts >= 3].index
    subset = subset[subset['CollapsedPathway'].isin(valid_pathways)]

    edges = subset[['Gene', 'CollapsedPathway']].drop_duplicates()
    edges.columns = ['Gene', 'Pathway']

    unique_pathways = edges['Pathway'].unique().tolist()
    unique_genes = edges['Gene'].unique().tolist()
    nodes_df = pd.DataFrame({'name': unique_pathways + unique_genes})
    nodes_df['type'] = ['Pathway'] * len(unique_pathways) + ['Gene'] * len(unique_genes)
    nodes_df['index'] = range(len(nodes_df))

    color_dict = {
        'Cell cycle': '#1f77b4', 'Apoptosis': '#d62728', 'PI3K-Akt signaling': '#ff7f0e',
        'mTOR signaling': '#ffbb78', 'FoxO signaling': '#2ca02c', 'VEGF signaling': '#98df8a',
        'Pathways in cancer': '#7f7f7f', 'Breast cancer': '#c7c7c7'
    }

    edges_named = edges.copy()
    edges_named.columns = ['source', 'target']

    chord = Chord((edges_named, hv.Dataset(nodes_df, 'name'))).opts(
        opts.Chord(
            labels='name',
            node_color=dim('name').categorize(color_dict, default='#9edae5'),
            edge_color=dim('target').categorize(color_dict, default='#9edae5'),
            width=950, height=950,
            title="Gene–Pathway Interactions (Curated List)"
        )
    )
    bokeh_obj = hv.render(chord, backend='bokeh')
    script, div = components(bokeh_obj, CDN)
    html(script + div, height=1000, width=1000)
