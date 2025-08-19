# 7_Clinical_Validation_TCGA_OV.py
import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

# -------------------------- Page config --------------------------
st.set_page_config(page_title="Clinical Validation (TCGA‑OV)", layout="wide")
st.title("Clinical Validation — TCGA‑OV")
st.caption("Overall survival (OS) and exploratory PFS; Cox models, volcano, forest, and Kaplan–Meier.")
st.caption("Last updated: August 19th 2025")

# -------------------------- Utilities --------------------------
@st.cache_data(show_spinner=False)
def load_cox_results():
    # biomarker_cox_results_os_with_HGNC.csv / biomarker_cox_results_pfs_with_HGNC.csv
    os_path = "streamlit_app/data/biomarker_cox_results_os_with_HGNC.csv"
    pfs_path = "streamlit_app/data/biomarker_cox_results_pfs_with_HGNC.csv"
    os_df = pd.read_csv(os_path) if os.path.exists(os_path) else pd.DataFrame()
    pfs_df = pd.read_csv(pfs_path) if os.path.exists(pfs_path) else pd.DataFrame()
    # Normalise expected columns
    for df in (os_df, pfs_df):
        if not df.empty:
            # Backward compatibility for column names
            rename_map = {
                "Adjusted p": "Adjusted_p",
                "Adjusted p-value": "Adjusted_p",
                "Adjusted HR": "Adjusted_HR",
                "Adjusted CI lower": "Adjusted_CI_lower",
                "Adjusted CI upper": "Adjusted_CI_upper",
                "Amp freq": "Amp_frequency",
                "Biomarker_HGNC_Symbol": "Biomarker_HGNC",
            }
            df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)
            # Ensure required cols exist
            required = ["Biomarker", "Biomarker_HGNC", "Adjusted_HR", "Adjusted_p",
                        "Adjusted_CI_lower", "Adjusted_CI_upper", "N_patients", "Amp_frequency"]
            for c in required:
                if c not in df.columns:
                    df[c] = np.nan
            # Add FDR column if missing
            if "Adjusted_FDR" not in df.columns:
                df["Adjusted_FDR"] = np.nan
            # Coerce types
            for c in ["Adjusted_HR", "Adjusted_p", "Adjusted_CI_lower", "Adjusted_CI_upper",
                      "N_patients", "Amp_frequency", "Adjusted_FDR"]:
                df[c] = pd.to_numeric(df[c], errors="coerce")
            # Provide HGNC fallback
            if df["Biomarker_HGNC"].isna().all():
                df["Biomarker_HGNC"] = df["Biomarker"].astype(str)
    return os_df, pfs_df

@st.cache_data(show_spinner=False)
def load_km_inputs():
    # From your notebook’s matched datasets
    clinical_path = "streamlit_app/data/clinical_matched.csv"
    amp_path = "streamlit_app/data/biomarker_amplifications_matched.csv"
    # HGNC mapping (for symbol↔Entrez)
    hgnc_map_path = "streamlit_app/data/gene_with_protein_product.txt"

    clinical_df = pd.read_csv(clinical_path) if os.path.exists(clinical_path) else pd.DataFrame()
    amp_df = pd.read_csv(amp_path, index_col=0) if os.path.exists(amp_path) else pd.DataFrame()
    if not amp_df.empty:
        amp_df.index = amp_df.index.astype(str)
        amp_df.columns = [c.replace("-", "_") for c in amp_df.columns]

    if os.path.exists(hgnc_map_path):
        hgnc_df = pd.read_csv(hgnc_map_path, sep="\t")
        symbol_to_entrez = dict(zip(hgnc_df["symbol"], hgnc_df["entrez_id"].astype(str)))
        entrez_to_symbol = dict(zip(hgnc_df["entrez_id"].astype(str), hgnc_df["symbol"]))
    else:
        symbol_to_entrez, entrez_to_symbol = {}, {}

    return clinical_df, amp_df, symbol_to_entrez, entrez_to_symbol

def safe_log2(x):
    try:
        return math.log2(x) if x > 0 else np.nan
    except Exception:
        return np.nan

def volcano(ax, df, p_col="Adjusted_p", hr_col="Adjusted_HR", fdr_col="Adjusted_FDR",
            p_thresh=0.05, fdr_thresh=0.05, title="Volcano (OS)"):
    plot_df = df.copy()
    plot_df["log2HR"] = plot_df[hr_col].apply(safe_log2)
    plot_df["neglog10p"] = -np.log10(plot_df[p_col].replace(0, np.nan))

    # Points
    ax.scatter(plot_df["log2HR"], plot_df["neglog10p"], s=28, alpha=0.75)

    # Reference lines
    ax.axhline(-math.log10(p_thresh), linestyle="--", linewidth=1, alpha=0.4)
    ax.axvline(math.log2(1.25), linestyle="--", linewidth=1, alpha=0.3)
    ax.axvline(math.log2(0.8), linestyle="--", linewidth=1, alpha=0.3)

    # Highlight top by nominal p
    top = plot_df.nsmallest(8, p_col)
    for _, r in top.iterrows():
        label = r.get("Biomarker_HGNC") or str(r.get("Biomarker"))
        if pd.notna(r["log2HR"]) and pd.notna(r["neglog10p"]):
            ax.text(r["log2HR"], r["neglog10p"], label, fontsize=9)

    ax.set_xlabel("log₂(HR)")
    ax.set_ylabel("−log₁₀(p)")
    ax.set_title(title)
    ax.grid(alpha=0.3)

    # Summary box
    n = len(plot_df)
    n_nom = int((plot_df[p_col] < p_thresh).sum())
    n_fdr = int((plot_df[fdr_col] < fdr_thresh).sum()) if fdr_col in plot_df.columns else 0
    txt = f"n={n}\nNominal p<{p_thresh}: {n_nom}\nFDR<{fdr_thresh}: {n_fdr}"
    ax.text(0.02, 0.98, txt, transform=ax.transAxes, va="top",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.7))

def forest(ax, df, top_n=15, title="Top biomarkers — Cox (OS)"):
    d = df.nsmallest(top_n, "Adjusted_p").copy()
    d = d.sort_values("Adjusted_p")
    y = np.arange(len(d))

    # CI bars
    for i, (_, r) in enumerate(d.iterrows()):
        lo, hi, hr = r["Adjusted_CI_lower"], r["Adjusted_CI_upper"], r["Adjusted_HR"]
        if pd.notna(lo) and pd.notna(hi) and pd.notna(hr):
            ax.plot([lo, hi], [i, i], linewidth=3, alpha=0.9)
            ax.scatter([hr], [i], edgecolors="black", zorder=3)

    # Labels
    labels = []
    for _, r in d.iterrows():
        name = r.get("Biomarker_HGNC") or str(r.get("Biomarker"))
        freq = r.get("Amp_frequency")
        freq_txt = f"{freq*100:.1f}%" if pd.notna(freq) else "NA"
        labels.append(f"{name} ({freq_txt})")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Hazard ratio (95% CI)")
    ax.set_xscale("log")
    ax.axvline(1.0, linestyle="--", alpha=0.5)
    ax.set_title(title)
    ax.grid(alpha=0.3, axis="x")

def km_plot(ax, clinical_df, amp_df, symbol_to_entrez, gene_symbol):
    if gene_symbol not in symbol_to_entrez:
        ax.set_title(f"{gene_symbol}: not in HGNC mapping")
        return
    entrez = str(symbol_to_entrez[gene_symbol])
    if entrez not in amp_df.index:
        ax.set_title(f"{gene_symbol} ({entrez}) not in amplification matrix")
        return

    amp_status = amp_df.loc[entrez].reset_index()
    amp_status.columns = ["PATIENT_ID_CLEAN", "AMP_STATUS"]
    df = clinical_df.merge(amp_status, on="PATIENT_ID_CLEAN", how="inner")
    df = df.dropna(subset=["OS_MONTHS", "OS_STATUS_BINARY", "AMP_STATUS"])

    if df["AMP_STATUS"].nunique() < 2:
        ax.set_title(f"{gene_symbol}: insufficient group separation")
        return

    grpA = df[df["AMP_STATUS"] == 1]
    grpB = df[df["AMP_STATUS"] == 0]

    kmA = KaplanMeierFitter()
    kmB = KaplanMeierFitter()
    kmA.fit(grpA["OS_MONTHS"], grpA["OS_STATUS_BINARY"], label=f"{gene_symbol} amplified (n={len(grpA)})")
    kmB.fit(grpB["OS_MONTHS"], grpB["OS_STATUS_BINARY"], label=f"not amplified (n={len(grpB)})")

    kmA.plot(ax=ax, ci_show=False, linewidth=2)
    kmB.plot(ax=ax, ci_show=False, linewidth=2)

    res = logrank_test(grpA["OS_MONTHS"], grpB["OS_MONTHS"],
                       event_observed_A=grpA["OS_STATUS_BINARY"],
                       event_observed_B=grpB["OS_STATUS_BINARY"])
    p = res.p_value
    ax.set_title(f"{gene_symbol} amplification — OS (log‑rank p={p:.3g})")
    ax.set_xlabel("Months")
    ax.set_ylabel("Survival probability")
    ax.grid(alpha=0.3)

# -------------------------- Load data --------------------------
os_df, pfs_df = load_cox_results()
clinical_df, amp_df, symbol_to_entrez, entrez_to_symbol = load_km_inputs()

# -------------------------- Sidebar controls --------------------------
with st.sidebar:
    st.header("Settings")
    endpoint = st.radio("Endpoint", ["OS", "PFS"], help="Select which Cox results to explore first.")
    p_thresh = st.number_input("Nominal p threshold", value=0.05, step=0.01, min_value=0.0)
    fdr_thresh = st.number_input("FDR threshold", value=0.05, step=0.01, min_value=0.0)
    top_n = st.slider("Forest plot: top N (by adjusted p)", 5, 30, 15, 1)
    default_genes = ["CCNE1", "ACTN4", "URI1"]
    genes = st.multiselect("Kaplan–Meier genes (HGNC symbols)", default_genes, default=default_genes)

# Select df
df = os_df if endpoint == "OS" else pfs_df
other_df = pfs_df if endpoint == "OS" else os_df

if df.empty:
    st.error("Cox results not found. Ensure the expected CSV outputs are present in ../results/clinical_translation/")
    st.stop()

# -------------------------- Visuals row 1: Volcano + Forest --------------------------
col1, col2 = st.columns([1.1, 1.0])

with col1:
    st.subheader(f"Volcano — {endpoint}")
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    volcano(ax, df, p_col="Adjusted_p", hr_col="Adjusted_HR",
            fdr_col="Adjusted_FDR", p_thresh=p_thresh, fdr_thresh=fdr_thresh,
            title=f"Exploratory volcano ({endpoint})")
    st.pyplot(fig, clear_figure=True)

with col2:
    st.subheader(f"Forest — {endpoint}")
    fig2, ax2 = plt.subplots(figsize=(7.5, 6.5))
    forest(ax2, df, top_n=top_n, title=f"Top {top_n} biomarkers — Cox ({endpoint})")
    st.pyplot(fig2, clear_figure=True)

# -------------------------- Table: Significant Cox terms --------------------------
st.subheader("Significant Cox terms")
has_fdr_hits = ("Adjusted_FDR" in df.columns) and (df["Adjusted_FDR"] < fdr_thresh).any()
if has_fdr_hits:
    table_df = df[df["Adjusted_FDR"] < fdr_thresh].copy()
    sig_note = f"FDR < {fdr_thresh}"
else:
    # Fall back to nominal if no FDR hits (transparent to users)
    table_df = df[df["Adjusted_p"] < p_thresh].copy()
    sig_note = f"Nominal p < {p_thresh} (exploratory; no FDR‑significant hits)"

# Optional interaction terms if present (biomarker × covariate)
possible_interactions = [c for c in df.columns if "Interaction" in c or "x" in c]
show_cols = ["Biomarker_HGNC", "Biomarker", "N_patients", "Amp_frequency",
             "Adjusted_HR", "Adjusted_CI_lower", "Adjusted_CI_upper", "Adjusted_p", "Adjusted_FDR"]
show_cols += [c for c in possible_interactions if c in df.columns]

if table_df.empty:
    st.info("No significant terms under current thresholds. Try relaxing filters or view nominal results.")
else:
    st.caption(sig_note)
    st.dataframe(
        table_df[ [c for c in show_cols if c in table_df.columns] ]
        .sort_values(["Adjusted_FDR", "Adjusted_p"], na_position="last")
        .reset_index(drop=True),
        use_container_width=True
    )

# -------------------------- Visuals row 2: Kaplan–Meier --------------------------
st.subheader("Kaplan–Meier survival (OS) for selected biomarkers")
if clinical_df.empty or amp_df.empty:
    st.info("KM inputs not found. Provide clinical_matched.csv and biomarker_amplifications_matched.csv to enable KM plots.")
else:
    ncols = 3
    rows = math.ceil(max(1, len(genes)) / ncols)
    for r in range(rows):
        cols = st.columns(ncols)
        for j in range(ncols):
            idx = r * ncols + j
            if idx >= len(genes):
                break
            g = genes[idx]
            with cols[j]:
                fig_km, ax_km = plt.subplots(figsize=(5, 4))
                km_plot(ax_km, clinical_df, amp_df, symbol_to_entrez, g)
                st.pyplot(fig_km, clear_figure=True)

# -------------------------- Context & caveats --------------------------
with st.expander("Methods & caveats"):
    st.markdown(
        """
- **Models:** Per‑biomarker Cox PH (endpoint = OS or PFS), age‑adjusted; FDR (Benjamini–Hochberg).
- **KM:** Grouped by **GISTIC deep amplification (2)** vs not; log‑rank test.
- **Interpretation:** Association ≠ causation; no treatment recommendations. Use findings as hypothesis‑generating.
- **Multiple testing:** Expect few/no FDR‑significant hits in exploratory screens; review nominal signals for plausibility.
- **Data:** TCGA‑OV Pan‑Cancer Atlas clinical + GISTIC CNA; matched per your preprocessing.
"""
    )

# -------------------------- Download --------------------------
dl_col1, dl_col2 = st.columns(2)
with dl_col1:
    st.download_button(
        "Download Cox results (OS)",
        data=os_df.to_csv(index=False).encode("utf-8") if not os_df.empty else "".encode("utf-8"),
        file_name="biomarker_cox_results_os_with_HGNC.csv",
        mime="text/csv",
        disabled=os_df.empty,
    )
with dl_col2:
    st.download_button(
        "Download Cox results (PFS)",
        data=pfs_df.to_csv(index=False).encode("utf-8") if not pfs_df.empty else "".encode("utf-8"),
        file_name="biomarker_cox_results_pfs_with_HGNC.csv",
        mime="text/csv",
        disabled=pfs_df.empty,
    )

# Footer
st.markdown("---")
st.markdown("🔬 Built for **BioSLATE**, in collaboration with **Breakthrough Cancer Research**")