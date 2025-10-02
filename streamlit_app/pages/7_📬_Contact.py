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
    
    /* Header styling - Royal Blue Theme */
    .main-header {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
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
        color: #dbeafe !important;
        font-size: 1.1rem;
        margin-bottom: 0.25rem;
    }
    
    .last-updated {
        color: #bfdbfe !important;
        font-size: 0.9rem;
        font-style: italic;
    }
    
    /* Sidebar styling - Consistent across all pages */
    .stSidebar {
        background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
    }
    
    .stSidebar .stSelectbox label,
    .stSidebar .stRadio label,
    .stSidebar .stNumberInput label,
    .stSidebar .stSlider label,
    .stSidebar .stMultiSelect label {
        color: #1e40af !important;
        font-weight: 600;
    }
    
    /* Download buttons - Consistent across all pages */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Header section
st.markdown("""
<div class="main-header">
    <h1>📬 Contact the BioSLATE Team</h1>
    <div class="caption">If you have any questions, suggestions, or feedback, feel free to reach out to us using the details below.</div>
</div>
""", unsafe_allow_html=True)

# Two columns
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("""
    ### 📍 UCD Cancer Data Lab

    **Faith Ogundimu**  
    Government of Ireland Postgraduate Scholar  
    ✉️ [faithogun12@gmail.com](mailto:faithogun12@gmail.com)  
    ✉️ [faithogundimu25@rcsi.ie](mailto:faithogundimu25@rcsi.ie)  
    🔗 [LinkedIn](https://www.linkedin.com/in/faith-ogundimu)  
    🖥️ [UCD Cancer Data Lab](https://cancerdata.ucd.ie/)  

    Passionate about advancing precision oncology and mechanistic discovery oncology through bioinformatics and AI.  

    ---

    **Dr. Colm Ryan**  
    Associate Professor, UCD  
    Project Supervisor  

    **Dr. Metin Yazar**  
    Postdoctoral Researcher, UCD  
    Mentor  
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
        Advancing precision oncology and mechanistic discovery oncology through computational genomics and artificial intelligence
    </div>
</div>
""", unsafe_allow_html=True)