import streamlit as st
import os
import re
from markdown import markdown  # Make sure to install this with: pip install markdown

# Page setup
st.set_page_config(page_title="SL Confidence Reports", layout="wide")
st.title("Synthetic Lethality Confidence Reports")
st.caption("Auto-generated summaries from PubMed, Open Targets, and ClinicalTrials.gov")

# Disclaimer about low confidence
st.markdown(
    """
    <div style="background-color:#eaf4fb; padding:12px; border-radius:6px;">
        ℹ️ <b>Context:</b> All synthetic lethality (SL) reports shown here are marked as <b>low confidence</b> (score &lt; 50/100).
        <br><br>
        This reflects limitations in available biomedical evidence:
        <ul>
            <li>Few gene pairs have well-documented SL interactions in current literature or curated databases.</li>
            <li>Evidence is sparse for many genes, especially those under-studied in cancer contexts.</li>
            <li>Our scoring is deliberately conservative, penalising missing or inconclusive data across PubMed, Open Targets, and ClinicalTrials.gov.</li>
        </ul>
        These summaries remain useful for <b>hypothesis generation</b> and early-stage exploration —
        <b>which is why we are actively researching and validating these potentially novel SL pairs</b> as part of this ongoing project.
    </div>
    """,
    unsafe_allow_html=True
)

# Path to low confidence reports only
LOW_CONF_PATH = "streamlit_app/reports/low_confidence_reports/"

@st.cache_data(show_spinner=False)
def load_low_confidence_reports():
    reports = {}
    for filename in os.listdir(LOW_CONF_PATH):
        if filename.endswith(".md"):
            biomarker_target = filename.replace("_report.md", "").replace(".md", "")
            display_name = biomarker_target.replace("_", " – ")
            with open(os.path.join(LOW_CONF_PATH, filename), "r", encoding="utf-8") as f:
                content = f.read()
            score_match = re.search(r"Confidence Score: (\d+)/100", content)
            score = int(score_match.group(1)) if score_match else 0
            reports[display_name] = {
                "content": content,
                "score": score,
                "path": os.path.join(LOW_CONF_PATH, filename)
            }
    return reports

# Load reports
reports = load_low_confidence_reports()
pair_names = sorted(reports.keys())

if not pair_names:
    st.warning("No reports found in the low confidence folder.")
    st.stop()

# Sidebar selector
st.sidebar.title("Report Selection")
selected_pair = st.sidebar.selectbox("Select SL Gene Pair", pair_names)
report = reports[selected_pair]

# Display markdown content as formatted HTML
html_content = markdown(report["content"])
st.markdown(html_content, unsafe_allow_html=True)

# Download as Markdown
with open(report["path"], "rb") as f:
    st.download_button(
        label="⬇️ Download Markdown (.md)",
        data=f.read(),
        file_name=f"{selected_pair}.md",
        mime="text/markdown"
    )
