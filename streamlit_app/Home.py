import streamlit as st
from streamlit.components.v1 import html

# Page setup
st.set_page_config(page_title="BioSLATE Home", layout="wide")

# Main title section
st.title("🔬 BioSLATE HGSOC Explorer Platform")
st.caption("Last updated: June 27, 2025")
st.subheader("Data-Driven Precision Oncology")

# Tagline
st.markdown("**Discover. Decode. Deliver.**")

# Introduction block
st.markdown(
    """
**BioSLATE** is a free and open-source web application built for researchers and clinicians exploring translational cancer biology.  
It facilitates the rapid interrogation of gene–protein relationships, biomarker discovery, and synthetic lethality interactions using large-scale, multi-omics datasets and AI-powered models.  
Originally built to support ovarian cancer research during an internship with the UCD Cancer Data Lab, BioSLATE can be expanded to support pan-cancer contexts, drug repurposing, and patient stratification.
"""
)

# Functional Overview block
st.markdown(
    """
---

### 📌 Functional Overview

**Gene–Protein Explorer**  
This module enables users to explore the association between copy number alterations (CNA) and protein abundance across cancer samples.  
By performing statistical comparisons (T-tests, Cohen’s d effect size, and linear regression), it helps identify genes whose alterations lead to significant proteomic changes, offering a foundation for biomarker discovery or drug target prioritisation.

**Synthetic Lethality Discovery**  
This tool leverages gene dependency datasets to uncover potential synthetic lethal pairs — genes that, when co-inhibited, selectively kill cancer cells with specific mutations or deletions.  
Users can interactively explore dependency profiles, mutation filters, and identify promising targets for combination therapy strategies.

**Drug Response Prediction**  
This module hosts machine learning classifiers trained on gene expression data to predict how a patient's tumour might respond to specific treatments.  
By comparing responder vs non-responder profiles across public datasets (e.g. TCGA), it assists in evaluating likely therapeutic outcomes and personalising cancer therapy.
"""
)

# License block
st.markdown(
    """
---

### 📜 Licence

Copyright (c) 2025 Faith Ogundimu.  
This software is distributed under an MIT licence.  
Please consult the LICENSE file for more details.
"""
)

# Social icon footer
st.markdown("---")
st.markdown("### 🌐 Connect With Us")

html(
    """
    <style>
    .icon-row {
        display: flex;
        gap: 30px;
        justify-content: center;
        margin-top: 20px;
    }
    .icon-link {
        text-decoration: none;
    }
    .icon-img {
        width: 40px;
        height: 40px;
        transition: transform 0.3s ease;
    }
    .icon-img:hover {
        transform: scale(1.3);
    }
    </style>

    <div class="icon-row">
        <a href="https://www.ucd.ie/" target="_blank" class="icon-link">
            <img src="https://upload.wikimedia.org/wikipedia/en/thumb/6/68/University_College_Dublin_logo.svg/1200px-University_College_Dublin_logo.svg.png" class="icon-img" title="UCD Website">
        </a>
        <a href="https://www.linkedin.com/in/faith-ogundimu" target="_blank" class="icon-link">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" class="icon-img" title="LinkedIn">
        </a>
        <a href="https://github.com/faith-ogun" target="_blank" class="icon-link">
            <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" class="icon-img" title="GitHub">
        </a>
        <a href="https://cancerdata.ucd.ie/" target="_blank" class="icon-link">
            <img src="https://cancerdata.ucd.ie/media/icon_dark_hu0ad8bdf2403366b9efcf01fd91c5dcb6_31076_400x0_resize_lanczos_3.png" class="icon-img" title="UCD Cancer Data Lab">
        </a>
    </div>
    """,
    height=120,
)