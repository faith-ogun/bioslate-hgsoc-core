import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="BioSLATE Home", layout="wide")

# Top logo
st.image("streamlit_app/assets/bioslate_logo.png", width=300)

st.title("🔬 HGSOC Explorer Platform")
st.caption("Last updated: August 19th 2025")
st.subheader("Data-Driven Precision Oncology")

# Sidebar logo
with st.sidebar:
    st.image("streamlit_app/assets/bioslate_logo.png", use_container_width=True)

# Justified intro
st.markdown("""
<div style='text-align: justify;'>

**Discover. Decode. Deliver.**

**BioSLATE** is a free and open-source web application built for researchers and clinicians exploring translational cancer biology.  
It facilitates the rapid interrogation of gene–protein relationships, biomarker discovery, and synthetic lethality interactions using large-scale, multi-omics datasets and AI-powered models.  

</div>
""", unsafe_allow_html=True)

# BioSLATE Infographic
st.image("streamlit_app/assets/bioslate_infographic.png", use_container_width=True)

# Functional Overview
st.markdown("""
---

### 📌 Functional Overview

**Gene–Protein Explorer**  
Investigate how copy number alterations (CNA) influence protein abundance across cancer samples.
This module supports statistical analysis (linear regression and significance testing) to identify genes whose amplifications or deletions lead to proteomic dysregulation — helping prioritise biomarkers and druggable alterations.

**Synthetic Lethality Discovery**  
Explore high-confidence synthetic lethal interactions derived from CNA–CRISPR regression screens in ovarian cancer.
Visualise SL pairs with amplification-stratified dependency, access statistical summaries, and interactively browse potent hits filtered by effect size, selectivity, and essentiality thresholds.

**Network & Pathway Analysis**  
Prioritise SL targets based on their functional connectivity and biological relevance.
This module integrates STRING PPI data and g\:Profiler pathway enrichment to highlight gene pairs with mechanistic support — including dot plots, barplots, and interactive chord diagrams of curated pathways (e.g. apoptosis, cell cycle, PI3K signalling).

**Clinical Validation (TCGA-OV)**  
Assess whether amplified biomarkers are associated with patient outcomes in the TCGA ovarian cancer cohort.
Visuals include Kaplan–Meier survival curves (overall survival) and forest plots summarising hazard ratios. A summary table lists significant Cox regression terms, including biomarker–interaction effects where applicable, providing translational context for prioritised biomarkers.
            
**Drug Sensitivity & Tractability**  
Summarise the translational potential of synthetic lethal targets by integrating Open Targets tractability data.
Visual outputs highlight how many targets are supported by approved drugs, small molecule inhibitors, antibody modalities, or clinical precedence. Interactive tables allow users to filter by tractability class, providing a rapid overview of which SL hits are already therapeutically accessible.

**About & Patient Involvement**  
Short, accessible text explaining the motivation for synthetic lethality in ovarian cancer and the purpose of this dashboard.
This section outlines what the dashboard shows, the underlying data sources, and important caveats — framed for patients and the public as well as researchers. The emphasis is on clarity without long blocks of technical prose.
""")

# Licence and credits
st.markdown("""
<div style='text-align: center; font-size: 0.8rem; margin-top: 40px;'>
Copyright (c) 2025 Faith Ogundimu.<br>
This software is distributed under an MIT licence. Please consult the LICENSE file for more details.
</div>
""", unsafe_allow_html=True)

# Footer icons
html("""
<style>
.icon-row {
    display: flex;
    gap: 30px;
    justify-content: center;
    margin-top: 20px;
    margin-bottom: 30px;
}
.icon-link {
    text-decoration: none;
}
.icon-img {
    width: 60px;
    height: 60px;
    object-fit: contain;
    transition: transform 0.3s ease;
}
.icon-img:hover {
    transform: scale(1.3);
}
</style>

<div class="icon-row">
    <a href="https://www.linkedin.com/in/faith-ogundimu" target="_blank" class="icon-link">
        <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" class="icon-img" title="LinkedIn">
    </a>
    <a href="https://github.com/faith-ogun" target="_blank" class="icon-link">
        <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" class="icon-img" title="GitHub">
    </a>
    <a href="https://cancerdata.ucd.ie/" target="_blank" class="icon-link">
        <img src="https://cancerdata.ucd.ie/media/icon_dark_hu0ad8bdf2403366b9efcf01fd91c5dcb6_31076_400x0_resize_lanczos_3.png" class="icon-img" title="UCD Cancer Data Lab">
    </a>
    <a href="https://breakthroughcancerresearch.ie/" target="_blank" class="icon-link">
        <img src="https://breakthroughcancerresearch.ie/wp-content/uploads/2024/10/bcr-main-logo.png" class="icon-img" title="Breakthrough Cancer Research">
    </a>
</div>
""", height=180)
