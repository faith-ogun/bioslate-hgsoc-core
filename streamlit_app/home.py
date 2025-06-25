import streamlit as st

st.set_page_config(page_title="BioSLATE Home", layout="wide")

# Display logo
st.image("streamlit_app/assets/bioslate_logo.png", width=500)  # Adjust width as needed

st.subheader("Data-driven Precision Oncology")
st.markdown(
    """
    **BioSLATE** is an interactive platform for translational cancer research. It enables the exploration of synthetic lethality, biomarker discovery, and drug response prediction in high-grade serous ovarian cancer (HGSOC) using multi-omics data and AI models.
    """
)

st.markdown("### 🚀 Available Modules")

col1, col2, col3 = st.columns(3)

with col1:
    st.image("streamlit_app/assets/gene_biomarker.png", width=160)
    st.markdown("#### Gene-Protein Explorer")
    st.write(
        "Interactively explore multi-omics data to identify protein-coding genes "
        "associated with copy number alterations and protein expression changes in HGSOC. "
        "Uncover potential biomarkers and therapeutic targets by analyzing "
        "statistical significance and effect sizes across patient samples."
    )


with col2:
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="streamlit_app/assets/synthetic_lethality.png" width="265"/>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("#### Explore Synthetic Lethality")
    st.write("Identify potential drug targets that exhibit synthetic lethality with cancer-specific mutations.")

with col3:
    st.image("streamlit_app/assets/responder-non-responder.png", width=250)
    st.markdown("#### Drug Response Prediction")
    st.write("Visualize machine models predictictions on how TCGA PanCancer patients will respond to different cancer therapies.")

st.markdown("---")
st.markdown("🏠 Use the sidebar to navigate between modules.")
