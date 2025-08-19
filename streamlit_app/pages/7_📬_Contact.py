import streamlit as st
from streamlit.components.v1 import html

# -------------------------- Page config & styling --------------------------
st.set_page_config(
    page_title="Contact – BioSLATE",
    page_icon="📬",
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
    
    /* Header styling - Contact Theme */
    .main-header {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        padding: 2rem 1rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 15px 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white !important;
        margin-bottom: 0.5rem;
        font-weight: 700;
        font-size: 2.5rem;
    }
    
    .main-header .caption {
        color: #d1fae5 !important;
        font-size: 1.1rem;
        margin-bottom: 0.25rem;
    }
    
    /* Sidebar styling - Consistent across all pages */
    .stSidebar {
        background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
    }
    
    /* Contact cards */
    .contact-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border-left: 4px solid #10b981;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }
    
    .contact-card h3 {
        color: #065f46;
        margin-bottom: 1.5rem;
        font-weight: 700;
        font-size: 1.3rem;
    }
    
    .contact-card p {
        color: #374151;
        line-height: 1.6;
        margin-bottom: 0.5rem;
    }
    
    .contact-card strong {
        color: #065f46;
        font-weight: 600;
    }
    
    .contact-card a {
        color: #059669;
        text-decoration: none;
        font-weight: 500;
    }
    
    .contact-card a:hover {
        color: #047857;
        text-decoration: underline;
    }
    
    /* Map container */
    .map-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #10b981;
    }
    
    .map-container h3 {
        color: #065f46;
        margin-bottom: 1rem;
        font-weight: 700;
        font-size: 1.3rem;
    }
    
    /* Intro text styling */
    .intro-text {
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #10b981;
        margin-bottom: 2rem;
        color: #065f46;
        font-size: 1.1rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Header section
st.markdown("""
<div class="main-header">
    <h1>📬 Contact the BioSLATE Team</h1>
    <div class="caption">Connect with our research team for questions, collaborations, and feedback</div>
</div>
""", unsafe_allow_html=True)

# Intro text
st.markdown("""
<div class="intro-text">
    If you have any questions, suggestions, or feedback about BioSLATE, feel free to reach out to us using the details below. 
    We welcome collaborations and are always happy to discuss our research in precision oncology and synthetic lethality.
</div>
""", unsafe_allow_html=True)

# Two columns
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("""
    <div class="contact-card">
        <h3>👨‍💼 Research Team</h3>
        
        <p><strong>Faith Ogundimu</strong><br>
        GOIPG IRC RCSI PhD Candidate<br>
        ✉️ <a href="mailto:faithogun12@gmail.com">faithogun12@gmail.com</a><br>
        ✉️ <a href="mailto:faith.ogundimu@rcsi.ie">faith.ogundimu@rcsi.ie</a><br>
        🔗 <a href="https://www.linkedin.com/in/faith-ogundimu" target="_blank">LinkedIn Profile</a><br>
        🖥️ <a href="https://cancerdata.ucd.ie/" target="_blank">UCD Cancer Data Lab</a></p>
        
        <p><em>Passionate about advancing precision oncology through bioinformatics and AI.</em></p>
        
        <hr style="margin: 2rem 0; border: none; border-top: 1px solid #e5e7eb;">
        
        <p><strong>Dr. Colm Ryan</strong><br>
        Associate Professor, UCD<br>
        Project Supervisor</p>
        
        <p><strong>Dr. Metin Yazar</strong><br>
        Postdoctoral Researcher<br>
        Mentor & Scientific Contributor</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="map-container">
        <h3>📍 UCD Conway Institute</h3>
    """, unsafe_allow_html=True)
    
    html(
        """
        <iframe 
            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2383.8451648508526!2d-6.227360423397385!3d53.31021917742615!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x486709338b645959%3A0xfa11bb9c23e854c1!2sUCD%20Conway%20Institute%2C%20University%20College%20Dublin!5e0!3m2!1sen!2sie!4v1751030718414!5m2!1sen!2sie" 
            width="100%" 
            height="400" 
            style="border:0; border-radius: 8px;" 
            allowfullscreen="" 
            loading="lazy" 
            referrerpolicy="no-referrer-when-downgrade">
        </iframe>
        """,
        height=430,
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

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
        Advancing precision oncology through computational genomics and artificial intelligence
    </div>
</div>
""", unsafe_allow_html=True)