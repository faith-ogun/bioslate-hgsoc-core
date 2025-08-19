import streamlit as st
from streamlit.components.v1 import html

# -------------------------- Page config & styling --------------------------
st.set_page_config(
    page_title="Contact – BioSLATE",
    page_icon="📬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📬 Contact the BioSLATE Team")

st.markdown("""
If you have any questions, suggestions, or feedback, feel free to reach out to us using the details below.
""")

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

# Two columns
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("""
    ### 📍 UCD Cancer Data Lab

    **Faith Ogundimu**  
    GOIPG IRC RCSI PhD Candidate  
    ✉️ [faithogun12@gmail.com](mailto:faithogun12@gmail.com)  
    ✉️ [faith.ogundimu@rcsi.ie](mailto:faith.ogundimu@rcsi.ie)  
    🔗 [LinkedIn](https://www.linkedin.com/in/faith-ogundimu)  
    🖥️ [UCD Cancer Data Lab](https://cancerdata.ucd.ie/)  

    Passionate about advancing precision oncology through bioinformatics and AI.  

    ---

    **Dr. Colm Ryan**  
    Associate Professor, UCD  
    Project Supervisor  

    **Dr. Metin Yazar**  
    Postdoctoral Researcher  
    Mentor & Scientific Contributor  
    """)


with col2:
    st.markdown("### 📍 UCD Conway Institute")
    html(
        """
        <iframe 
            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2383.8451648508526!2d-6.227360423397385!3d53.31021917742615!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x486709338b645959%3A0xfa11bb9c23e854c1!2sUCD%20Conway%20Institute%2C%20University%20College%20Dublin!5e0!3m2!1sen!2sie!4v1751030718414!5m2!1sen!2sie" 
            width="100%" 
            height="450" 
            style="border:0; border-radius: 8px;" 
            allowfullscreen="" 
            loading="lazy" 
            referrerpolicy="no-referrer-when-downgrade">
        </iframe>
        """,
        height=480,
    )

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