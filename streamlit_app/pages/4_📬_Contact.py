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

    ---

    **Dr. Colm Ryan**  
    Associate Professor, UCD  
    Principal Investigator & PhD Supervisor  

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