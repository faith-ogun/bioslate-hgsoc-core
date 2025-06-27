import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Contact – BioSLATE", layout="wide")
st.title("📬 Contact the BioSLATE Team")

st.markdown("""
If you have any questions, suggestions, or feedback, feel free to reach out to us using the details below.
""")

# Two columns
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("""
    ### 📍 UCD Cancer Data Lab

    **Faith Ogundimu**  
    PhD Researcher & Bioinformatics Intern  
    ✉️ [faithogun12@gmail.com](mailto:faithogun12@gmail.com)  
    ✉️ [faith.ogundimu@rcsi.ie](mailto:faith.ogundimu@rcsi.ie)  
    🔗 [LinkedIn](https://www.linkedin.com/in/faith-ogundimu)  
    🖥️ [UCD Cancer Data Lab](https://cancerdata.ucd.ie/)  

    Passionate about advancing precision oncology through bioinformatics and AI.  
    Working on multi-omics data integration, biomarker discovery, and drug response prediction in ovarian cancer.

    ---

    **Dr. Colm Ryan**  
    Associate Professor, UCD  
    Principal Investigator & PhD Supervisor  

    **Dr. Metin Yazar**  
    Postdoctoral Researcher  
    Mentor & Scientific Contributor  
    """)


with col2:
    st.markdown("### 📍 Conway Institute – UCD, Dublin")
    st.components.v1.html(
        """
        <iframe 
            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2383.2429243141576!2d-6.223420184460338!3d53.307245979978675!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x48670e9f3ac504ef%3A0xd96856d3a13ae886!2sUCD%20Conway%20Institute!5e0!3m2!1sen!2sie!4v1718274133066!5m2!1sen!2sie" 
            width="100%" 
            height="400" 
            style="border:0; border-radius: 8px;" 
            allowfullscreen="" 
            loading="lazy" 
            referrerpolicy="no-referrer-when-downgrade">
        </iframe>
        """,
        height=420,
    )
