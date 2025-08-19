import streamlit as st

# --- Page config ---
st.set_page_config(page_title="About & Patient Involvement", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #7BB3F0 0%, #4A90E2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .section-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 5px solid #2E86AB;
        margin-bottom: 1.5rem;
    }
    
    .highlight-box {
        background: linear-gradient(135deg, #4A90E2 0%, #2E86AB 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
    }
    
    .pipeline-step {
        background: #F0F4F8;
        border: 2px solid #D6E4F0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #2E86AB;
    }
    
    .patient-focus {
        background: linear-gradient(135deg, #4A90E2 0%, #7BB3F0 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #fdcb6e;
    }
    
    .data-source {
        background: #E8F4FD;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #4A90E2;
    }
    
    .section-spacer {
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Main Header ---
st.markdown("""
<div class="main-header">
    <h1>🧬 Understanding Synthetic Lethality in Ovarian Cancer</h1>
    <p style="font-size: 1.2em; margin-top: 1rem; opacity: 0.9;">
        Breakthrough Cancer Research Dashboard
    </p>
    <p style="font-size: 0.9em; opacity: 0.8;">Last updated: August 19th, 2025</p>
</div>
""", unsafe_allow_html=True)

# --- Quick Overview ---
st.markdown("""
<div class="highlight-box">
    <h3>🎯 Our Mission</h3>
    <p style="font-size: 1.1em;">
        We're exploring <strong>synthetic lethality</strong> in High-Grade Serous Ovarian Cancer (HGSOC) 
        to find new treatment targets that could selectively attack cancer cells while protecting healthy tissue.
    </p>
</div>
""", unsafe_allow_html=True)

# --- What is Synthetic Lethality? ---
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    <div style="background: #F0F4F8; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; border-left: 4px solid #2E86AB;">
        <strong>💡 The Simple Idea</strong><br>
        Some cancer cells with a specific biomarker (like a gene amplification) become dependent on a partner gene to survive.
    </div>

    <div style="background: #E8F4FD; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4A90E2;">
        <strong>✨ The Opportunity</strong><br>
        If we can block that partner gene, we can selectively harm the cancer cells while leaving healthy cells unaffected.
    </div>

    <div style="background: #E8F4FD; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4A90E2;">
        <strong>🎯 Our Approach</strong><br>
        We search for genes that become essential when a biomarker is amplified, then validate these findings across multiple datasets and clinical outcomes.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: #E8F4FD; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4A90E2;">
        <strong>🎯 Precision Medicine</strong><br>
        Target cancer cells specifically
    </div>

    <div style="background: #E8F4FD; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4A90E2;">
        <strong>💊 Better Treatment</strong><br>
        Potentially fewer side effects
    </div>

    <div style="background: #E8F4FD; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4A90E2;">
        <strong>📈 Hope</strong><br>
        New therapeutic opportunities
    </div>
    """, unsafe_allow_html=True)

# --- Our Research Pipeline ---
st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="section-card">
    <h3>🔄 Our Research Pipeline</h3>
    <p>We follow a systematic 6-step process to identify and validate potential treatment targets:</p>
</div>
""", unsafe_allow_html=True)

# Pipeline steps in a more visual format
pipeline_steps = [
    ("1️⃣", "Patient Data Analysis (TCGA)", "Find genes frequently amplified/deleted in patient tumours and test if copy number relates to protein expression"),
    ("2️⃣", "Cell Line Validation (DepMap)", "Confirm these genetic changes exist in laboratory models of ovarian cancer"),
    ("3️⃣", "Synthetic Lethality Screen", "Test which genes become essential when biomarkers are present using CRISPR technology"),
    ("4️⃣", "Network & Pathway Analysis", "Check if biomarker-target pairs interact through known biological pathways"),
    ("5️⃣", "Drug Sensitivity Testing", "Explore whether genetic changes predict response to existing drugs"),
    ("6️⃣", "Clinical Outcomes", "Examine links between gene copy number and patient survival data")
]

cols = st.columns(2)
for i, (emoji, title, desc) in enumerate(pipeline_steps):
    with cols[i % 2]:
        st.markdown(f"""
        <div class="pipeline-step">
            <h4>{emoji} {title}</h4>
            <p style="margin-bottom: 0;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# --- Data Sources ---
st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="section-card">
    <h3>📚 Our Data Sources</h3>
    <p>We combine multiple high-quality datasets to ensure robust findings:</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="data-source">
        <strong>🏥 TCGA (The Cancer Genome Atlas)</strong><br>
        Patient tumour data including genetic changes and protein levels
    </div>
    
    <div class="data-source">
        <strong>🧪 DepMap</strong><br>
        Laboratory cell line data for experimental validation
    </div>
    
    <div class="data-source">
        <strong>🔗 STRING Database</strong><br>
        Protein interaction networks and biological pathways
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="data-source">
        <strong>📖 SynLethDB / ISLE</strong><br>
        Published synthetic lethality interactions from literature
    </div>
    
    <div class="data-source">
        <strong>💊 GDSC</strong><br>
        Drug response data across cancer cell lines
    </div>
    """, unsafe_allow_html=True)

# --- Important Considerations ---
with st.expander("⚠️ Important Considerations & Limitations", expanded=False):
    st.markdown("""
    <div class="warning-box">
        <h4>🔍 What Our Results Mean</h4>
        <ul>
            <li><strong>Early Research:</strong> These are research findings that need further validation</li>
            <li><strong>Not Medical Advice:</strong> This dashboard does not provide treatment recommendations</li>
            <li><strong>Model Limitations:</strong> Laboratory models don't perfectly represent patient tumours</li>
            <li><strong>Statistical Considerations:</strong> We use statistical methods to reduce false positives, but some may remain</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --- Patient Involvement Section ---
st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="patient-focus">
    <h2>👥 Patient Involvement & Partnership</h2>
    <p style="font-size: 1.2em; margin-bottom: 2rem;">
        Patient voices guide our research priorities and help us communicate findings clearly
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background: #E8F4FD; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4A90E2;">
        <strong>📝 Clear Communication</strong><br>
        Simple language and readable gene names
    </div>

    <div style="background: #E8F4FD; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4A90E2;">
        <strong>🎯 Clinical Focus</strong><br>
        Emphasis on biomarker-guided targets and survival outcomes
    </div>

    <div style="background: #E8F4FD; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4A90E2;">
        <strong>📊 Visual Design</strong><br>
        Charts and summaries that are easy to understand
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: #E8F4FD; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4A90E2;">
        <strong>💬 Share Feedback</strong><br>
        Help us identify unclear language or confusing sections
    </div>

    <div style="background: #E8F4FD; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4A90E2;">
        <strong>🎯 Suggest Priorities</strong><br>
        Tell us which outcomes matter most for future research
    </div>

    <div style="background: #E8F4FD; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4A90E2;">
        <strong>🔬 Trial Insights</strong><br>
        Share thoughts on biomarker-stratified trial concepts
    </div>
    """, unsafe_allow_html=True)

# -------------------------- Footer --------------------------
st.markdown("---")

st.markdown("""
<div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); margin: 2rem -1rem -1rem -1rem; border-radius: 15px 15px 0 0;">
    <div style="font-size: 1.2rem; font-weight: 600; color: #1e40af; margin-bottom: 0.5rem;">
        🔬 BioSLATE Clinical Validation Platform
    </div>
    <div style="color: #64748b; font-size: 1rem;">
        Developed in collaboration with <strong style="color: #1e40af;">Breakthrough Cancer Research</strong>
    </div>
    <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem;">
        Advancing precision oncology through computational genomics
    </div>
</div>
""", unsafe_allow_html=True)