import streamlit as st

# --- Page config ---
st.set_page_config(page_title="About & Patient Involvement", layout="wide")
st.title("About this Dashboard & Patient Involvement")
st.caption("Last updated: August 19th 2025")

# --- Intro: keep it short ---
st.markdown(
    """
This dashboard explores **synthetic lethality (SL)** in **High‑Grade Serous Ovarian Cancer (HGSOC)** by
linking tumour **copy‑number biomarkers** to **gene vulnerabilities**, then stress‑testing findings across
networks, public databases, drugs, and survival outcomes.
"""
)

# --- Why Synthetic Lethality ---
st.subheader("Why Synthetic Lethality ?")
st.markdown(
    """
**Idea in One Line:** some tumours with a specific **biomarker** (e.g., a gene amplification) become
**dependent** on a partner gene. **Inhibiting that partner can selectively harm biomarker‑positive cancer
cells** while sparing others—**precision with less collateral damage**.

**What This Means Here:** we look for genes that become more essential **when a biomarker is amplified**,
then check whether those targets sit in plausible pathways, have prior evidence, align with drug
responses, and show clinical relevance in patients.
"""
)

# --- What this dashboard shows ---
st.subheader("What This Dashboard Shows")
st.markdown(
    """
The pages in this app map to a **pipeline**:

1) **Biomarker discovery in patients (TCGA)** — find genes frequently amplified/deleted and test if copy number
relates to protein expression (GISTIC −2…+2).  
2) **Cross‑validation in HGSOC cell lines (DepMap)** — confirm those alterations exist in experimental models.  
3) **SL screen (CRISPR vs CNA)** — model **gene dependency ~ biomarker CNA**; shortlist hits by effect size and FDR.  
4) **Networks & pathways (STRING / g:Profiler)** — check if biomarker–target pairs interact or enrich shared pathways.  
5) **Drug sensitivity (GDSC)** — ask if **higher biomarker copy number ↔ higher drug sensitivity** as an orthogonal signal.  
6) **Clinical survival (TCGA)** — explore whether target expression (± biomarker context) links to overall survival.
"""
)

with st.expander("See the Data Flow at a Glance"):
    st.markdown(
        """
- **TCGA HGSOC** → candidate biomarkers and CNA–protein links  
- **DepMap HGSOC cell lines** → confirm biomarker presence; run SL regression screen  
- **STRING / g:Profiler** → mechanistic plausibility (PPI/pathways)  
- **GDSC** → biomarker amplification signals drug sensitivity  
- **TCGA survival** → clinical context
"""
    )

# --- Data sources & caveats ---
st.subheader("Data Sources & Caveats")
left, right = st.columns([1,1])

with left:
    st.markdown(
        """
**Primary sources**
- **TCGA HGSOC (cBioPortal Pan‑Cancer Atlas)** — CNA (GISTIC), mRNA, proteomics.  
- **DepMap (CCLE)** — HGSOC cell line CNA and CRISPR dependency.  
- **STRING v12** — protein–protein interactions; confidence thresholds (e.g., 400).  
- **SynLethDB / ISLE** — public SL interaction references.  
- **GDSC** — RNA‑seq expression and drug response (AUC).  

**Notes on processing**
- **Biomarkers:** selected from TCGA by frequency and CNA–protein association.  
- **SL screen:** OLS modelling of dependency vs CNA; shortlist by **effect size < 0** and **FDR**.  
- **Networks:** map HGNC symbols to STRING IDs, test PPIs and run pathway enrichment.  
"""
    )

with right:
    st.markdown(
        """
**Caveats (read first)**
- **Association ≠ causation:** regression + correlation signals need perturbed validation.  
- **Model bias:** cell lines are imperfect tumour proxies; copy‑number scales differ (GISTIC vs absolute CN).  
- **Multiple testing:** FDR thresholds help but do not eliminate false positives.  
- **PPI scores:** STRING cut‑offs affect hit counts; pathways can be broad or redundant.  
- **Drug links:** CNA–AUC associations are orthogonal hints, **not** proof of druggability or efficacy.  
- **Survival signals:** can reflect confounding; interpret as exploratory.
"""
    )

st.divider()

# --- Patient involvement ---
st.subheader("Patient Involvement")
st.markdown(
    """
**How Patient Input Shaped This Work**
- **Clarity first:** prioritised **readable gene names**, simple visuals, and short explanations.  
- **Clinical relevance:** emphasised **biomarker‑guided** targets and survival context to focus on
what could matter to treatment research.  

**What this Dashboard Does Not Do**
- It does **not** use identifiable patient data.  
- It does **not** recommend treatments or replace clinical advice.

**Ways Patients and Advocates can Contribute**
- Suggest **which outcomes matter** (e.g., quality‑of‑life endpoints to track in future analyses).  
- Flag **unclear language** so we can improve the plain‑English summaries.  
- Share priorities for **biomarker‑stratified trial concepts** we should examine next.

If you have comments or priorities to share, please reach out via the project contact listed on the home page.
"""
)

