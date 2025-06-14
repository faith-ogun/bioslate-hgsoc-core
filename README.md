# BioSLATE: Biomarker Selection and Synthetic Lethality Analysis for Therapeutic Exploration in HGSOC

## 🧠 Description
This repository contains all code, documentation, and deliverables from a 10-week research project, led by Dr. Colm Ryan at University College Dublin (UCD), in collaboration with **Breakthrough Cancer Research**. The objective of this project was to identify and prioritise clinically actionable synthetic lethal gene pairs in HGSOC using publicly available multi-omics data and CRISPR screens.

## 🚀 Objectives
- Identify recurrent genomic alterations (biomarkers) in HGSOC
- Discover synthetic lethal gene partners using CRISPR dependency data
- Evaluate therapeutic relevance of synthetic lethal pairs
- Incorporate patient/public involvement (PPI) and deliver lay-friendly summaries

---

## 📁 Repository Structure

```
bioslate-hgsoc-core/
├── data/                   # Cleaned and processed input data (non-sensitive)
├── notebooks/              # Jupyter notebooks for each analysis phase
├── scripts/                # Python and R scripts for reproducible workflows
├── results/                # Output files: figures, tables, biomarker lists
├── reports/                # Final report, executive summary, lay summary
├── figures/                # Static visualisations used in reporting
├── presentations/          # Final slide deck (PDF or PPTX)
├── environment.yml         # Reproducible Conda environment
└── README.md               # You're here!
```

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/faith-ogun/bioslate-hgsoc-core.git
cd bioslate-hgsoc-core
```

### 2. Create environment

```bash
conda env create -f environment.yml
conda activate bioslate
```

### 3. Run notebooks or scripts

Notebooks are modular and numbered by phase.

---

## 📊 Data Sources

- [DepMap (Cancer Cell Line Encyclopedia)](https://depmap.org/portal/)
- [TCGA - The Cancer Genome Atlas](https://portal.gdc.cancer.gov/)
- [Open Targets](https://www.opentargets.org/)
- CRISPR screen dependency datasets (Achilles, DEMETER2)

*Note: Raw data not included due to size and licensing. Scripts retrieve via APIs or require manual download.*

---

## 🧪 Methodology Overview

### Phase 1: Discovery & Biomarker Identification
- CNV analysis on HGSOC cell lines (DepMap)
- TCGA alteration frequency calculation
- Candidate biomarker selection

### Phase 2: Synthetic Lethality Mapping
- Stratify cell lines by biomarker status
- Use CRISPR screen scores to detect differential essentiality
- Statistical testing and FDR correction

### Phase 3: Target Prioritisation
- Integrate druggability scores from Open Targets
- Cross-reference with drug screening results
- PPI-informed prioritisation

---

## 🧾 Deliverables

- 📘 Full technical report (PDF)
- 🧬 Ranked synthetic lethal gene pairs
- 🧠 Executive summary + Lay summary (PPI)
- 🎞 Final slide presentation (case study format)
- 📂 All supporting data, code, and figures

---

## 💬 Public and Patient Involvement (PPI)

A lay-friendly summary and patient feedback loop were integrated into the research process to ensure outputs are aligned with clinical relevance and patient priorities.

---

## 👥 Contributors

- **Faith Ogundimu** – Undergraduate (now Postgraduate) Researcher funded by Breakthrough Cancer Research
- **Supervisor** - Associate Professor Colm Ryan
- **Postdoctoral Researcher** (Mentor) - Dr. Metin Yazar
- **Breakthrough Cancer Research** – Funding Body (Grant Code: SUMSCH037)   
- PPI Panel (anonymous) – Feedback on priorities and communication

---

## 📄 License

This repository is licensed for non-commercial academic/research use. See `LICENSE` for details.

---

## 📫 Contact

🔗 [LinkedIn](https://www.linkedin.com/in/faith-ogundimu-3895421b9/)  

---

## 🧭 Citation / Acknowledgement

If you use this project or analysis approach in your work, please cite:

(_Coming soon_)
