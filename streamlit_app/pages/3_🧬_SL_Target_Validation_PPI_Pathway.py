import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import holoviews as hv
from holoviews import opts, dim
from holoviews.element.graphs import Chord
hv.extension('bokeh')
import streamlit.components.v1 as components
import tempfile
import os

# --- Page config ---
st.set_page_config(page_title="PPI & Pathway Analysis of SL Targets", layout="wide")
st.title("Network & Pathway Analysis of Potent Synthetic Lethal Targets")
st.caption("Last updated: August 1st 2025")

# --- Load data ---
@st.cache_data
def load_ppi_and_pathway_data():
    ppi_df = pd.read_csv("streamlit_app/data/potent_hits_STRING_PPI_check.csv")
    gprofiler_biomarkers = pd.read_csv("streamlit_app/data/gprofiler_enrichment_biomarkers.csv")
    gprofiler_targets = pd.read_csv("streamlit_app/data/gprofiler_enrichment_targets.csv")
    mapping_biomarkers = pd.read_csv("streamlit_app/data/gene_to_pathway_map_biomarkers.csv")
    mapping_targets = pd.read_csv("streamlit_app/data/gene_to_pathway_map_targets.csv")
    return ppi_df, gprofiler_biomarkers, gprofiler_targets, mapping_biomarkers, mapping_targets

ppi_df, gprofiler_biomarkers, gprofiler_targets, mapping_biomarkers, mapping_targets = load_ppi_and_pathway_data()

# --- Sidebar radio ---
view_option = st.sidebar.radio(
    "Choose View",
    ["Top Pathways (Barplot)", "Pathway × Gene (Dotplot)", "Biomarker Network (Chord)", "Target Network (Chord)"]
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
    
    # Create side-by-side plots
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Biomarkers - Top 15 Enriched Pathways**")
        bio_sig = gprofiler_biomarkers[gprofiler_biomarkers['significant'] == True].copy()
        bio_top = bio_sig.nsmallest(15, 'p_value')
        
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        sns.barplot(y='name', x=-np.log10(bio_top['p_value']), data=bio_top, color='#235b91', ax=ax1)
        ax1.set_xlabel('-log₁₀(p-value)')
        ax1.set_ylabel('Pathway')
        ax1.set_title('Biomarkers – Top 15 Enriched Pathways')
        ax1.invert_yaxis()
        st.pyplot(fig1)
    
    with col2:
        st.markdown("**Targets - Top 15 Enriched Pathways**")
        tar_sig = gprofiler_targets[gprofiler_targets['significant'] == True].copy()
        tar_top = tar_sig.nsmallest(15, 'p_value')
        
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        sns.barplot(y='name', x=-np.log10(tar_top['p_value']), data=tar_top, color='#a8323c', ax=ax2)
        ax2.set_xlabel('-log₁₀(p-value)')
        ax2.set_ylabel('Pathway')
        ax2.set_title('Targets – Top 15 Enriched Pathways')
        ax2.invert_yaxis()
        st.pyplot(fig2)
    
    # Download buttons
    col1, col2 = st.columns(2)
    with col1:
        csv_bio = gprofiler_biomarkers.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Biomarker Enrichment (.csv)", csv_bio, "gprofiler_biomarkers.csv", mime="text/csv")
    
    with col2:
        csv_tar = gprofiler_targets.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Target Enrichment (.csv)", csv_tar, "gprofiler_targets.csv", mime="text/csv")

# --- View 2: Dotplot ---
elif view_option == "Pathway × Gene (Dotplot)":
    st.subheader("Gene × Pathway Dot Plot")
    
    # Biomarkers dotplot
    st.markdown("**Biomarkers - Genes in Top 5 Enriched Pathways**")
    bio_sig = gprofiler_biomarkers[gprofiler_biomarkers['significant'] == True].copy()
    bio_top_paths = bio_sig.nsmallest(5, 'p_value')["name"].tolist()
    bio_filtered = mapping_biomarkers[mapping_biomarkers["Pathway"].isin(bio_top_paths)]
    bio_dot = bio_filtered.groupby(['Pathway', 'Gene']).size().unstack(fill_value=0)
    
    fig1, ax1 = plt.subplots(figsize=(12, 8))
    sns.heatmap(bio_dot.T, cmap=sns.color_palette(["white", "#235b91"]), cbar=False, 
                linewidths=0.5, linecolor="black", ax=ax1)
    ax1.set_xlabel("Pathway")
    ax1.set_ylabel("Gene")
    ax1.set_title("Biomarkers – Genes in Top 5 Enriched Pathways")
    st.pyplot(fig1)
    
    # Targets dotplot
    st.markdown("**Targets - Genes in Top 5 Enriched Pathways**")
    tar_sig = gprofiler_targets[gprofiler_targets['significant'] == True].copy()
    tar_top_paths = tar_sig.nsmallest(5, 'p_value')["name"].tolist()
    tar_filtered = mapping_targets[mapping_targets["Pathway"].isin(tar_top_paths)]
    tar_dot = tar_filtered.groupby(['Pathway', 'Gene']).size().unstack(fill_value=0)
    
    fig2, ax2 = plt.subplots(figsize=(12, 8))
    sns.heatmap(tar_dot.T, cmap=sns.color_palette(["white", "#a8323c"]), cbar=False, 
                linewidths=0.5, linecolor="black", ax=ax2)
    ax2.set_xlabel("Pathway")
    ax2.set_ylabel("Gene")
    ax2.set_title("Targets – Genes in Top 5 Enriched Pathways")
    st.pyplot(fig2)

# --- View 3: Biomarker Chord diagram ---
elif view_option == "Biomarker Network (Chord)":
    st.subheader("Chord Diagram: Biomarker Gene–Pathway Network")
    
    # Collapse map for biomarkers (transport-related processes)
    collapse_map_bio = {
        'nitrogen compound transport': 'Molecular transport',
        'protein transport': 'Molecular transport',
        'intracellular transport': 'Molecular transport',
        'Golgi vesicle transport': 'Molecular transport',
        'cellular localization': 'Molecular transport',
        'establishment of localization in cell': 'Molecular transport',
        'establishment of protein localization': 'Molecular transport',
        'macromolecule localization': 'Molecular transport',
        'RNA localization': 'Molecular transport',
        'regulation of RNA splicing': 'RNA metabolism',
        'positive regulation of RNA metabolic process': 'RNA metabolism',
    }
    
    # Process biomarker data
    mapping_biomarkers['CollapsedPathway'] = mapping_biomarkers['Pathway'].replace(collapse_map_bio)
    keep_terms_bio = set(collapse_map_bio.values())
    subset_bio = mapping_biomarkers[mapping_biomarkers['CollapsedPathway'].isin(keep_terms_bio)]
    
    # Remove underpowered pathways
    counts_bio = subset_bio['CollapsedPathway'].value_counts()
    valid_pathways_bio = counts_bio[counts_bio >= 3].index
    subset_bio = subset_bio[subset_bio['CollapsedPathway'].isin(valid_pathways_bio)]
    
    edges_bio = subset_bio[['Gene', 'CollapsedPathway']].drop_duplicates()
    edges_bio.columns = ['Gene', 'Pathway']
    
    if len(edges_bio) == 0:
        st.warning("No pathway-gene connections found for biomarkers with current filters.")
    else:
        # Prepare nodes and edges
        unique_pathways_bio = edges_bio['Pathway'].unique().tolist()
        unique_genes_bio = edges_bio['Gene'].unique().tolist()
        nodes_df_bio = pd.DataFrame({'name': unique_pathways_bio + unique_genes_bio})
        nodes_df_bio['type'] = ['Pathway'] * len(unique_pathways_bio) + ['Gene'] * len(unique_genes_bio)
        
        color_dict_bio = {
            'Molecular transport': '#1f77b4',
            'RNA metabolism': '#ff7f0e',
        }
        
        edges_named_bio = edges_bio.copy()
        edges_named_bio.columns = ['source', 'target']
        
        # Create chord diagram
        chord_bio = Chord((edges_named_bio, hv.Dataset(nodes_df_bio, 'name'))).opts(
            opts.Chord(
                labels='name',
                node_color=dim('name').categorize(color_dict_bio, default='#9edae5'),
                edge_color=dim('target').categorize(color_dict_bio, default='#9edae5'),
                width=900,
                height=900,
                title="Biomarker Genes in Enriched Pathways"
            )
        )
        
        # Save to temporary HTML file and display
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            temp_filename = f.name
        
        hv.save(chord_bio, temp_filename, backend='bokeh')
        
        with open(temp_filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        components.html(html_content, height=1200, width=1000, scrolling=True)
        
        # Clean up temp file
        os.unlink(temp_filename)

# --- View 4: Target Chord diagram ---
elif view_option == "Target Network (Chord)":
    st.subheader("Chord Diagram: Target Gene–Pathway Network")
    
    # Collapse map for targets (comprehensive biological processes)
    collapse_map_targets = {
        # Mitochondrial processes
        'mitochondrial translation': 'Mitochondrial gene expression & translation',
        'Mitochondrial translation': 'Mitochondrial gene expression & translation',
        'Mitochondrial translation initiation': 'Mitochondrial gene expression & translation',
        'Mitochondrial translation elongation': 'Mitochondrial gene expression & translation',
        'Mitochondrial translation termination': 'Mitochondrial gene expression & translation',
        'mitochondrial gene expression': 'Mitochondrial gene expression & translation',
        
        # Cell cycle & checkpoints
        'cell cycle': 'Cell cycle',
        'mitotic cell cycle': 'Cell cycle',
        'mitotic cell cycle process': 'Cell cycle',
        'cell cycle process': 'Cell cycle',
        'cell cycle phase transition': 'Cell cycle',
        'mitotic cell cycle phase transition': 'Cell cycle',
        'G1/S transition of mitotic cell cycle': 'Cell cycle checkpoints',
        'regulation of mitotic cell cycle phase transition': 'Cell cycle checkpoints',
        'positive regulation of mitotic cell cycle phase transition': 'Cell cycle checkpoints',
        'regulation of cell cycle': 'Cell cycle checkpoints',
        'regulation of cell cycle process': 'Cell cycle checkpoints',
        'positive regulation of cell cycle': 'Cell cycle checkpoints',
        'regulation of cell cycle phase transition': 'Cell cycle checkpoints',
        'regulation of cell population proliferation': 'Cell cycle checkpoints',
        
        # DNA replication, repair, synthesis
        'DNA repair': 'DNA repair & synthesis',
        'double-strand break repair': 'DNA repair & synthesis',
        'double-strand break repair via homologous recombination': 'DNA repair & synthesis',
        'DNA damage response': 'DNA repair & synthesis',
        'DNA metabolic process': 'DNA repair & synthesis',
        'regulation of DNA repair': 'DNA repair & synthesis',
        'regulation of DNA metabolic process': 'DNA repair & synthesis',
        'S Phase': 'DNA repair & synthesis',
        'DNA-templated transcription': 'DNA repair & synthesis',
        'regulation of DNA-templated transcription': 'DNA repair & synthesis',
        'positive regulation of DNA-templated transcription': 'DNA repair & synthesis',
        
        # Chromatin
        'chromatin organization': 'Chromatin organization',
        'chromatin remodeling': 'Chromatin organization',
        'nuclear chromosome segregation': 'Chromatin organization',
        'chromosome organization': 'Chromatin organization',
        'chromosome segregation': 'Chromatin organization',
        'mitotic sister chromatid segregation': 'Chromatin organization',
        'sister chromatid segregation': 'Chromatin organization',
        
        # Metabolic process regulation
        'regulation of primary metabolic process': 'Metabolic process regulation',
        'positive regulation of metabolic process': 'Metabolic process regulation',
        'positive regulation of macromolecule metabolic process': 'Metabolic process regulation',
        'positive regulation of cellular process': 'Metabolic process regulation',
        'positive regulation of nucleobase-containing compound metabolic process': 'Metabolic process regulation',
        'regulation of nucleobase-containing compound metabolic process': 'Metabolic process regulation',
        'regulation of macromolecule metabolic process': 'Metabolic process regulation',
        'regulation of metabolic process': 'Metabolic process regulation',
        'positive regulation of RNA metabolic process': 'Metabolic process regulation',
        'negative regulation of RNA metabolic process': 'Metabolic process regulation',
        'negative regulation of nucleobase-containing compound metabolic process': 'Metabolic process regulation',
        'negative regulation of DNA-templated transcription': 'Metabolic process regulation',
        'regulation of RNA biosynthetic process': 'Metabolic process regulation',
        'positive regulation of RNA biosynthetic process': 'Metabolic process regulation',
        'negative regulation of RNA biosynthetic process': 'Metabolic process regulation',
        'regulation of biosynthetic process': 'Metabolic process regulation',
        'positive regulation of biosynthetic process': 'Metabolic process regulation',
        
        # Protein synthesis & degradation
        'translation': 'Protein synthesis & degradation',
        'Ribosome': 'Protein synthesis & degradation',
        'protein metabolic process': 'Protein synthesis & degradation',
        'regulation of protein metabolic process': 'Protein synthesis & degradation',
        'proteasome-mediated ubiquitin-dependent protein catabolic process': 'Protein synthesis & degradation',
        'ubiquitin-dependent protein catabolic process': 'Protein synthesis & degradation',
        'modification-dependent protein catabolic process': 'Protein synthesis & degradation',
        'modification-dependent macromolecule catabolic process': 'Protein synthesis & degradation',
        'proteasomal protein catabolic process': 'Protein synthesis & degradation',
        
        # Stress & apoptosis
        'response to stress': 'Stress response & apoptosis',
        'cellular response to stress': 'Stress response & apoptosis',
        'programmed cell death': 'Stress response & apoptosis',
        'cell death': 'Stress response & apoptosis',
        'apoptotic process': 'Stress response & apoptosis',
    }
    
    # Process target data
    mapping_targets['CollapsedPathway'] = mapping_targets['Pathway'].replace(collapse_map_targets)
    keep_terms_targets = set(collapse_map_targets.values())
    subset_targets = mapping_targets[mapping_targets['CollapsedPathway'].isin(keep_terms_targets)]
    
    # Remove underpowered pathways
    counts_targets = subset_targets['CollapsedPathway'].value_counts()
    valid_pathways_targets = counts_targets[counts_targets >= 3].index
    subset_targets = subset_targets[subset_targets['CollapsedPathway'].isin(valid_pathways_targets)]
    
    edges_targets = subset_targets[['Gene', 'CollapsedPathway']].drop_duplicates()
    edges_targets.columns = ['Gene', 'Pathway']
    
    if len(edges_targets) == 0:
        st.warning("No pathway-gene connections found for targets with current filters.")
    else:
        # Prepare nodes and edges
        unique_pathways_targets = edges_targets['Pathway'].unique().tolist()
        unique_genes_targets = edges_targets['Gene'].unique().tolist()
        nodes_df_targets = pd.DataFrame({'name': unique_pathways_targets + unique_genes_targets})
        nodes_df_targets['type'] = ['Pathway'] * len(unique_pathways_targets) + ['Gene'] * len(unique_genes_targets)
        
        color_dict_targets = {
            'Mitochondrial gene expression & translation': '#1f77b4',
            'Cell cycle': '#2ca02c',
            'Cell cycle checkpoints': '#98df8a',
            'DNA repair & synthesis': '#ff7f0e',
            'Chromatin organization': '#ffbb78',
            'Metabolic process regulation': '#9467bd',
            'Protein synthesis & degradation': '#8c564b',
            'Stress response & apoptosis': '#d62728',
        }
        
        edges_named_targets = edges_targets.copy()
        edges_named_targets.columns = ['source', 'target']
        
        # Create chord diagram
        chord_targets = Chord((edges_named_targets, hv.Dataset(nodes_df_targets, 'name'))).opts(
            opts.Chord(
                labels='name',
                node_color=dim('name').categorize(color_dict_targets, default='#9edae5'),
                edge_color=dim('target').categorize(color_dict_targets, default='#9edae5'),
                width=900,
                height=900,
                title="Synthetic Lethal Target-Pathway Network"
            )
        )
        
        # Save to temporary HTML file and display
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            temp_filename = f.name
        
        hv.save(chord_targets, temp_filename, backend='bokeh')
        
        with open(temp_filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        components.html(html_content, height=1200, width=1000, scrolling=True)
        
        # Clean up temp file
        os.unlink(temp_filename)