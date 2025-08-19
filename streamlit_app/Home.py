import streamlit as st
from streamlit.components.v1 import html

# -------------------------- Page config & styling --------------------------
st.set_page_config(
    page_title="BioSLATE Home",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main background and text */
    .stApp {
        background-color: #fafbfc;
    }
    
    /* Hero section styling */
    .hero-section {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
        padding: 3rem 2rem;
        margin: -1rem -1rem 3rem -1rem;
        border-radius: 0 0 20px 20px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.1);
    }
    
    .hero-title {
        color: white !important;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .hero-subtitle {
        color: #e0e7ff !important;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .hero-description {
        color: #cbd5e1 !important;
        font-size: 1.2rem;
        max-width: 800px;
        margin: 0 auto 2rem auto;
        line-height: 1.6;
    }
    
    .tagline {
        color: #f8fafc !important;
        font-size: 1.3rem;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 1.5rem;
    }
    
    /* Logo container */
    .logo-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #3b82f6;
        margin-bottom: 2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.1);
    }
    
    .feature-title {
        color: #1e40af;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .feature-description {
        color: #374151;
        line-height: 1.7;
        font-size: 1rem;
    }
    
    /* Section headers */
    .section-header {
        color: #1e40af;
        font-size: 2.2rem;
        font-weight: 700;
        text-align: center;
        margin: 3rem 0 2rem 0;
        border-bottom: 3px solid #e2e8f0;
        padding-bottom: 1rem;
    }
    
    /* Infographic container */
    .infographic-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin: 2rem 0;
    }
    
    /* Footer styling */
    .footer-section {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 2rem;
        margin: 3rem -1rem -1rem -1rem;
        border-radius: 20px 20px 0 0;
        text-align: center;
    }
    
    .copyright-text {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 2rem;
        font-style: italic;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
    }
    
    /* Custom button styling */
    .cta-button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        text-decoration: none;
        display: inline-block;
        margin: 1rem 0.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .cta-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 16px -4px rgba(16, 185, 129, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar logo
with st.sidebar:
    st.image("streamlit_app/assets/bioslate_logo.png", use_container_width=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="tagline">DISCOVER • DECODE • DELIVER</div>
    <h1 class="hero-title">🔬 HGSOC Explorer Platform</h1>
    <div class="hero-subtitle">Data-Driven Precision Oncology</div>
    <div class="hero-description">
        BioSLATE is a free and open-source web application built for researchers and clinicians exploring translational cancer biology. 
        It facilitates the rapid interrogation of gene–protein relationships, biomarker discovery, and synthetic lethality interactions 
        using large-scale, multi-omics datasets and AI-powered models.
    </div>
    <div style="margin-top: 2rem;">
        <span style="color: #cbd5e1; font-size: 1rem; font-style: italic;">Last updated: August 19th, 2025</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Display logo after hero section
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("streamlit_app/assets/bioslate_logo.png", use_container_width=True)

# Platform Overview Infographic
st.markdown('<h2 class="section-header">📊 Platform Overview</h2>', unsafe_allow_html=True)

st.markdown("""
<div class="infographic-container">
""", unsafe_allow_html=True)

st.image("streamlit_app/assets/bioslate_infographic.png", use_container_width=True, caption="BioSLATE Platform Architecture and Workflow")

st.markdown("""
</div>
""", unsafe_allow_html=True)

# Functional Modules
st.markdown('<h2 class="section-header">🔧 Functional Modules</h2>', unsafe_allow_html=True)

# Create feature cards
features = [
    {
        "icon": "🧬",
        "title": "Gene–Protein Explorer",
        "description": "Investigate how copy number alterations (CNA) influence protein abundance across cancer samples. This module supports statistical analysis (linear regression and significance testing) to identify genes whose amplifications or deletions lead to proteomic dysregulation — helping prioritise biomarkers and druggable alterations."
    },
    {
        "icon": "⚡",
        "title": "Synthetic Lethality Discovery",
        "description": "Explore high-confidence synthetic lethal interactions derived from CNA–CRISPR regression screens in ovarian cancer. Visualise SL pairs with amplification-stratified dependency, access statistical summaries, and interactively browse potent hits filtered by effect size, selectivity, and essentiality thresholds."
    },
    {
        "icon": "🕸️",
        "title": "Network & Pathway Analysis",
        "description": "Prioritise SL targets based on their functional connectivity and biological relevance. This module integrates STRING PPI data and g:Profiler pathway enrichment to highlight gene pairs with mechanistic support — including dot plots, barplots, and interactive chord diagrams of curated pathways."
    },
    {
        "icon": "📈",
        "title": "Clinical Validation (TCGA-OV)",
        "description": "Assess whether amplified biomarkers are associated with patient outcomes in the TCGA ovarian cancer cohort. Visuals include Kaplan–Meier survival curves (overall survival) and forest plots summarising hazard ratios with translational context for prioritised biomarkers."
    },
    {
        "icon": "💊",
        "title": "Drug Sensitivity & Tractability",
        "description": "Summarise the translational potential of synthetic lethal targets by integrating Open Targets tractability data. Visual outputs highlight targets supported by approved drugs, small molecule inhibitors, antibody modalities, or clinical precedence."
    },
    {
        "icon": "🤝",
        "title": "About & Patient Involvement",
        "description": "Accessible explanations of synthetic lethality in ovarian cancer and dashboard purpose. Outlines data sources and important caveats — framed for patients, the public, and researchers with emphasis on clarity without technical jargon."
    }
]

# Display features in a grid
col1, col2 = st.columns(2)

for i, feature in enumerate(features):
    with col1 if i % 2 == 0 else col2:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-title">
                {feature['icon']} {feature['title']}
            </div>
            <div class="feature-description">
                {feature['description']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Call to Action
st.markdown("""
<div style="text-align: center; margin: 3rem 0;">
    <h3 style="color: #1e40af; margin-bottom: 1rem;">Ready to explore cancer genomics?</h3>
    <p style="color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;">
        Navigate through our modules using the sidebar to start your analysis journey.
    </p>
</div>
""", unsafe_allow_html=True)

# Footer Section
st.markdown("""
<div class="footer-section">
    <h3 style="color: #1e40af; margin-bottom: 2rem;">🤝 Useful Links</h3>
    <p style="color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;">
        Developed in collaboration with leading cancer research institutions
    </p>
""", unsafe_allow_html=True)

# Footer icons
html("""
<style>
.icon-row {
    display: flex;
    gap: 40px;
    justify-content: center;
    margin: 2rem 0;
    flex-wrap: wrap;
}
.icon-link {
    text-decoration: none;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem;
    border-radius: 15px;
    background: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    min-width: 120px;
}
.icon-link:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}
.icon-img {
    width: 50px;
    height: 50px;
    object-fit: contain;
    margin-bottom: 0.5rem;
}
.icon-label {
    font-size: 0.8rem;
    color: #374151;
    font-weight: 600;
    text-align: center;
}
</style>

<div class="icon-row">
    <a href="https://www.linkedin.com/in/faith-ogundimu" target="_blank" class="icon-link">
        <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" class="icon-img">
    </a>
    <a href="https://github.com/faith-ogun" target="_blank" class="icon-link">
        <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" class="icon-img">
    </a>
    <a href="https://cancerdata.ucd.ie/" target="_blank" class="icon-link">
        <img src="https://cancerdata.ucd.ie/media/icon_dark_hu0ad8bdf2403366b9efcf01fd91c5dcb6_31076_400x0_resize_lanczos_3.png" class="icon-img">
    </a>
    <a href="https://breakthroughcancerresearch.ie/" target="_blank" class="icon-link">
        <img src="https://breakthroughcancerresearch.ie/wp-content/uploads/2024/10/bcr-main-logo.png" class="icon-img">
    </a>
</div>
""", height=220)

# -------------------------- Footer --------------------------
st.markdown("---")

st.markdown("""
<div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); margin: 2rem -1rem -1rem -1rem; border-radius: 15px 15px 0 0;">
    <div style="font-size: 1.2rem; font-weight: 600; color: #1e40af; margin-bottom: 0.5rem;">
        🔬 BioSLATE Clinical Translation Platform
    </div>
    <div style="color: #64748b; font-size: 1rem;">
        Developed in collaboration with <strong style="color: #1e40af;">Breakthrough Cancer Research</strong>
    </div>
    <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem;">
        Advancing precision oncology through computational genomics
    </div>
</div>
""", unsafe_allow_html=True)