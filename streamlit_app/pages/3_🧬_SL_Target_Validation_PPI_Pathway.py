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
st.caption("Last updated: August 19th 2025")

# --- Load data ---
@st.cache_data
def load_ppi_and_pathway_data():
    ppi_df = pd.read_csv("streamlit_app/data/potent_hits_STRING_PPI_check.csv")
    biogrid_df = pd.read_csv("streamlit_app/data/fet_ppi_overlap_biomarker_query_representative.csv")
    gprofiler_biomarkers = pd.read_csv("streamlit_app/data/gprofiler_enrichment_biomarkers.csv")
    gprofiler_targets = pd.read_csv("streamlit_app/data/gprofiler_enrichment_targets.csv")
    mapping_biomarkers = pd.read_csv("streamlit_app/data/gene_to_pathway_map_biomarkers.csv")
    mapping_targets = pd.read_csv("streamlit_app/data/gene_to_pathway_map_targets.csv")
    return ppi_df, biogrid_df, gprofiler_biomarkers, gprofiler_targets, mapping_biomarkers, mapping_targets

ppi_df, biogrid_df, gprofiler_biomarkers, gprofiler_targets, mapping_biomarkers, mapping_targets = load_ppi_and_pathway_data()

# --- Sidebar radio ---
view_option = st.sidebar.radio(
    "Choose View",
    ["Top Pathways (Barplot)", "Pathway × Gene (Dotplot)", "Biomarker Network (Chord)", "Target Network (Chord)", "PPI Network Analysis"]
)

# --- Enhanced PPI Analysis Section ---
st.subheader("🔗 Protein-Protein Interaction Analysis")

# Calculate key metrics
n_total_string = len(ppi_df)
n_with_ppi_string = ppi_df["PPI_found"].sum()

n_total_biogrid = len(biogrid_df)
n_direct_biogrid = biogrid_df["interact"].sum()
n_shared_interactors = (biogrid_df["n_shared_ppi"] > 0).sum()
n_significant_overlap = (biogrid_df["fet_ppi_overlap"] < 0.05).sum()

# Create metrics display
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Direct PPI (STRING)", 
        f"{n_with_ppi_string}/{n_total_string}",
        f"{n_with_ppi_string/n_total_string*100:.1f}%"
    )

with col2:
    st.metric(
        "Direct PPI (BioGRID)", 
        f"{n_direct_biogrid}/{n_total_biogrid}",
        f"{n_direct_biogrid/n_total_biogrid*100:.1f}%"
    )

with col3:
    st.metric(
        "Shared Interactors", 
        f"{n_shared_interactors}/{n_total_biogrid}",
        f"{n_shared_interactors/n_total_biogrid*100:.1f}%"
    )

with col4:
    st.metric(
        "Significant Overlap", 
        f"{n_significant_overlap}/{n_total_biogrid}",
        f"{n_significant_overlap/n_total_biogrid*100:.1f}% (p < 0.05)"
    )

st.markdown("""
**Key Findings:**
- While direct protein interactions are rare (4.2% in BioGRID, 7.6% in STRING), **84.4% of biomarker-target pairs share common interactors**
- **16.9% show statistically significant network overlap** (p < 0.05), indicating coherent functional modules
- Shared interactors include key oncogenic regulators: **MYC, CDK9, PARP1**
- **Network-mediated relationships dominate over direct interactions**, supporting a modular disruption model
""")

with st.expander("📄 View All PPI-Annotated Pairs"):
    tab1, tab2 = st.tabs(["STRING Database", "BioGRID Analysis"])
    
    with tab1:
        st.dataframe(ppi_df, use_container_width=True)
        csv_string = ppi_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download STRING PPI Table (.csv)", csv_string, "string_ppi_hits.csv", mime="text/csv")
    
    with tab2:
        # Show most interesting BioGRID pairs
        interesting_pairs = biogrid_df[
            (biogrid_df["fet_ppi_overlap"] < 0.05) | 
            (biogrid_df["n_shared_ppi"] >= 10) |
            (biogrid_df["interact"] == True)
        ].sort_values("fet_ppi_overlap")
        
        st.dataframe(interesting_pairs[['Biomarker_HGNC', 'TargetGene_HGNC', 'interact', 'n_shared_ppi', 
                                      'shared_ppi_jaccard_idx', 'fet_ppi_overlap', 'shared_ppi_hgnc']], 
                    use_container_width=True)
        csv_biogrid = biogrid_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download BioGRID Analysis (.csv)", csv_biogrid, "biogrid_ppi_analysis.csv", mime="text/csv")

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

# --- View 5: PPI Network Analysis ---
elif view_option == "PPI Network Analysis":
    st.subheader("🕸️ Protein Interaction Network Analysis")
    
    # Summary statistics
    median_shared = biogrid_df[biogrid_df["n_shared_ppi"] > 0]["n_shared_ppi"].median()
    mean_jaccard = biogrid_df[biogrid_df["shared_ppi_jaccard_idx"] > 0]["shared_ppi_jaccard_idx"].mean()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Median Shared Interactors", f"{median_shared:.0f}")
        st.metric("Mean Jaccard Index", f"{mean_jaccard:.3f}")
        
        st.markdown("""
        **Network Statistics:**
        - Median of 4 shared interactors among connected pairs
        - Jaccard similarity averaging 0.029 indicates moderate but meaningful overlap
        - Network topology serves as predictive framework for cancer vulnerabilities
        """)
    
    with col2:
        # Distribution of shared interactors
        fig, ax = plt.subplots(figsize=(8, 5))
        shared_counts = biogrid_df[biogrid_df["n_shared_ppi"] > 0]["n_shared_ppi"]
        ax.hist(shared_counts, bins=25, color='#1f77b4', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Number of Shared Interactors')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of Shared PPI Counts')
        ax.axvline(x=median_shared, color='red', linestyle='--', label=f'Median = {median_shared:.0f}')
        ax.legend()
        st.pyplot(fig)
    
    # Top shared interactors analysis
    st.subheader("🎯 Most Frequent Shared Interactors")
    st.markdown("Canonical oncogenic regulators that recur across multiple synthetic lethal relationships:")
    
    # Process shared_ppi_hgnc column to count frequencies
    all_interactors = []
    for ppi_list in biogrid_df["shared_ppi_hgnc"].dropna():
        if isinstance(ppi_list, str) and ppi_list != "":
            interactors = [x.strip() for x in ppi_list.split(",") if x.strip()]
            all_interactors.extend(interactors)
    
    if all_interactors:
        interactor_counts = pd.Series(all_interactors).value_counts().head(20)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 8))
            interactor_counts.plot(kind='barh', ax=ax, color='#2ca02c')
            ax.set_xlabel('Frequency Across SL Pairs')
            ax.set_ylabel('Shared Interactor')
            ax.set_title('Top 20 Most Frequent Shared Protein Interactors')
            # Highlight key oncogenes
            for i, (gene, count) in enumerate(interactor_counts.head(20).items()):
                if gene in ['MYC', 'CDK9', 'PARP1', 'TP53', 'EGFR', 'AKT1']:
                    ax.barh(i, count, color='#d62728', alpha=0.8)
            st.pyplot(fig)
        
        with col2:
            st.markdown("**Key Oncogenic Regulators:**")
            key_genes = ['MYC', 'CDK9', 'PARP1', 'TP53', 'EGFR', 'AKT1', 'BRCA1', 'ATM']
            for gene in key_genes:
                if gene in interactor_counts.index:
                    count = interactor_counts[gene]
                    st.markdown(f"• **{gene}**: {count} pairs")
    
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