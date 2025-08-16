import os
import json
import re
import pandas as pd
import requests
from dotenv import load_dotenv
from typing import Type, Optional, Dict, Any, Union, List
from Bio import Entrez
from pydantic import BaseModel, Field, PrivateAttr
from crewai import Agent, Task, Crew, Process, LLM
from langchain_openai import ChatOpenAI
from crewai.tools import BaseTool
import warnings
import logging
from urllib3.connectionpool import log as urllib3_logger

# ---------------------------
# WARNING CONTROL
# ---------------------------
warnings.filterwarnings('ignore')
logging.getLogger("urllib3").setLevel(logging.ERROR)
urllib3_logger.setLevel(logging.CRITICAL)

# ---------------------------
# ENVIRONMENT SETUP
# ---------------------------
env_path = os.path.join(os.path.dirname(__file__), ".env")
if not os.path.exists(env_path):
    raise FileNotFoundError("Missing `.env`. Please copy `.env.example` and fill in credentials.")

load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENTREZ_EMAIL = os.getenv("ENTREZ_EMAIL")

if not OPENAI_API_KEY or not ENTREZ_EMAIL:
    raise EnvironmentError("OPENAI_API_KEY and ENTREZ_EMAIL must be set in .env.")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
Entrez.email = ENTREZ_EMAIL

# ---------------------------
# LLM SETUP
# ---------------------------
llm = LLM(model="gpt-4o")

# ---------------------------
# HGNC to Ensembl Mapping
# ---------------------------
def load_hgnc_map(filepath: str) -> dict:
    df = pd.read_csv(filepath, sep="\t", dtype=str)
    return dict(zip(df["symbol"], df["ensembl_gene_id"]))

# ---------------------------
# OVARIAN ONCOGENE OVERRIDES
# ---------------------------
OVARIAN_ONCOGENES = {
    "CCNE1", "MYC", "KRAS", "MECOM", "PIK3CA", "BCL2", "CDK2", "CDK12",
    "BRD4", "BIRC5", "RSF1", "YAP1", "AKT2"
}

# ---------------------------
# TOOLS FROM COMMON.PY
# ---------------------------

class GeneEvaluationInput(BaseModel):
    gene: str = Field(..., description="Gene symbol to evaluate")

class GeneCancerSearchTool(BaseTool):
    name: str = "Gene Cancer Search Tool"
    description: str = "Searches PubMed for cancer-related studies involving a specific gene"
    args_schema: Type[BaseModel] = GeneEvaluationInput

    def _run(self, gene: str) -> str:
        queries = [
            f"{gene} AND cancer",
            f"{gene} AND ovarian cancer",
            f"{gene} AND synthetic lethality",
            f"{gene} AND oncogene"
        ]

        try:
            all_results = []
            seen_pmids = set()
            results_summary = {
                "gene": gene,
                "cancer": False,
                "ovarian": False,
                "sl": False,
                "oncogene": False,
                "articles": []
            }

            for query in queries:
                handle = Entrez.esearch(db="pubmed", term=query, retmax=3)
                record = Entrez.read(handle)
                pmid_list = record["IdList"]

                if pmid_list:
                    # Mark relevant categories as having hits
                    if "cancer" in query and "ovarian" not in query:
                        results_summary["cancer"] = True
                    elif "ovarian cancer" in query:
                        results_summary["ovarian"] = True
                    elif "synthetic lethality" in query:
                        results_summary["sl"] = True
                    elif "oncogene" in query:
                        results_summary["oncogene"] = True

                    handle = Entrez.efetch(db="pubmed", id=",".join(pmid_list[:2]), retmode="xml")
                    results = Entrez.read(handle)

                    for article in results["PubmedArticle"]:
                        pmid = str(article["MedlineCitation"]["PMID"])
                        if pmid in seen_pmids:
                            continue
                        seen_pmids.add(pmid)

                        article_data = article["MedlineCitation"]["Article"]
                        title = article_data.get("ArticleTitle", "No title")
                        
                        results_summary["articles"].append({
                            "pmid": pmid,
                            "title": title.strip(),
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}"
                        })

            return json.dumps(results_summary, indent=2)

        except Exception as e:
            return json.dumps({"gene": gene, "cancer": False, "ovarian": False, "sl": False, "oncogene": False, "error": str(e)})

class GeneDruggabilityTool(BaseTool):
    name: str = "Gene Druggability Tool"
    description: str = "Checks druggability and tractability of a gene using Open Targets"
    args_schema: Type[BaseModel] = GeneEvaluationInput

    _hgnc_map: dict = PrivateAttr()

    def __init__(self, hgnc_map: dict):
        super().__init__()
        self._hgnc_map = hgnc_map

    def symbol_to_ensembl(self, symbol: str) -> Optional[str]:
        return self._hgnc_map.get(symbol)

    def _run(self, gene: str) -> str:
        ensembl_id = self.symbol_to_ensembl(gene)
        if not ensembl_id:
            return json.dumps({"gene": gene, "druggable": False, "druggability_level": "NONE", "error": "No Ensembl ID found"})

        query = """
        query target($ensemblId: String!) {
          target(ensemblId: $ensemblId) {
            id
            approvedSymbol
            tractability {
              label
              modality
              value
            }
            knownDrugs {
              count
              rows {
                phase
                drug {
                  name
                }
              }
            }
          }
        }
        """

        variables = {"ensemblId": ensembl_id}
        url = "https://api.platform.opentargets.org/api/v4/graphql"

        try:
            res = requests.post(url, json={"query": query, "variables": variables})
            res.raise_for_status()
            response_data = res.json()

            target_data = response_data.get("data", {}).get("target")
            if not target_data:
                return json.dumps({"gene": gene, "druggable": False, "druggability_level": "NONE", "error": "No target data"})

            tractability = target_data.get("tractability", [])
            known_drugs = target_data.get("knownDrugs", {})
            drug_count = known_drugs.get("count", 0)

            sm_scores = [t for t in tractability if t.get("modality") == "SM"]
            tract_labels = {t.get("label", ""): t.get("value", False) for t in sm_scores}

            high_conf_labels = {"Approved Drug"}
            mid_conf_labels = {"Advanced Clinical", "Phase 1 Clinical", "Clinical Precedence"}
            low_conf_labels = {"Structure with Ligand", "High-Quality Ligand", "High-Quality Pocket", "Druggable Family"}

            true_labels = {label for label, value in tract_labels.items() if value}

            if true_labels & high_conf_labels:
                druggability = "HIGH"
            elif true_labels & mid_conf_labels:
                druggability = "MODERATE"
            elif true_labels & low_conf_labels or drug_count > 0:
                druggability = "LOW"
            else:
                druggability = "NONE"

            return json.dumps({
                "gene": gene,
                "druggable": druggability != "NONE",
                "druggability_level": druggability,
                "drug_count": drug_count,
                "tractability_flags": list(true_labels)
            }, indent=2)

        except Exception as e:
            return json.dumps({"gene": gene, "druggable": False, "druggability_level": "NONE", "error": str(e)})

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def extract_and_parse_json(task_output, name="unknown"):
    """Extract JSON from task output with robust error handling"""
    raw_str = task_output.raw if hasattr(task_output, 'raw') else str(task_output)
    
    try:
        # Try direct JSON parsing first
        return json.loads(raw_str)
    except json.JSONDecodeError:
        # Try to extract JSON block from text
        json_match = re.search(r'(\{.*\})', raw_str, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
    
    # Fallback: return empty structure
    print(f"Warning: Could not parse JSON from {name}, using fallback")
    return {"error": f"Failed to parse JSON from {name}"}

def calculate_gene_score(cancer_data, drug_data):
    """Calculate deterministic score for a gene"""
    score = 0
    
    # Cancer relevance (60 points max)
    if cancer_data.get("cancer", False):
        score += 20
    if cancer_data.get("ovarian", False):
        score += 20
    if cancer_data.get("sl", False):
        score += 10
    if cancer_data.get("oncogene", False):
        score += 10
    
    # Druggability (40 points max)
    druggability_level = drug_data.get("druggability_level", "NONE")
    if druggability_level == "HIGH":
        score += 40
    elif druggability_level == "MODERATE":
        score += 25
    elif druggability_level == "LOW":
        score += 10
    
    return score

def run_selector_on_cluster(i, genes, cancer_tool, drug_tool, selector_agent):
    """Process a single cluster and select the best representative gene"""
    
    gene_data = []
    
    # Collect data for each gene
    for gene in genes:
        cancer_raw = cancer_tool._run(gene=gene)
        drug_raw = drug_tool._run(gene=gene)
        
        try:
            cancer_data = json.loads(cancer_raw)
        except:
            cancer_data = {"gene": gene, "cancer": False, "ovarian": False, "sl": False, "oncogene": False}
            
        try:
            drug_data = json.loads(drug_raw)
        except:
            drug_data = {"gene": gene, "druggable": False, "druggability_level": "NONE"}
        
        score = calculate_gene_score(cancer_data, drug_data)
        
        gene_data.append({
            "gene": gene,
            "score": score,
            "cancer_data": cancer_data,
            "drug_data": drug_data
        })
    
    # Create prompt for agent selection
    prompt = f"## Cluster Analysis for Genes: {', '.join(genes)}\n\n"
    
    for data in gene_data:
        gene = data["gene"]
        score = data["score"]
        cancer = data["cancer_data"]
        drug = data["drug_data"]
        
        prompt += f"### {gene} (Score: {score}/100)\n"
        prompt += f"- Cancer relevance: {cancer.get('cancer', False)}\n"
        prompt += f"- Ovarian cancer relevance: {cancer.get('ovarian', False)}\n"
        prompt += f"- Synthetic lethality evidence: {cancer.get('sl', False)}\n"
        prompt += f"- Oncogene evidence: {cancer.get('oncogene', False)}\n"
        prompt += f"- Druggability level: {drug.get('druggability_level', 'NONE')}\n"
        prompt += f"- Drug count: {drug.get('drug_count', 0)}\n\n"
    
    prompt += """
    Based on this evidence, select the BEST representative gene for this cluster for ovarian cancer precision medicine.
    
    Consider:
    1. Overall score and evidence strength
    2. Cancer relevance (especially ovarian cancer)
    3. Therapeutic potential (druggability)
    4. Synthetic lethality potential
    
    End your response with: "SELECTED REPRESENTATIVE: [GENE_NAME]"
    """
    
    # Create and run selection task
    task = Task(
        description=prompt,
        expected_output="Analysis and clear selection of the best representative gene with reasoning ending with 'SELECTED REPRESENTATIVE: [GENE_NAME]'",
        agent=selector_agent
    )
    
    crew = Crew(agents=[selector_agent], tasks=[task], verbose=True)
    result = crew.kickoff()
    result_str = str(result)
    
    # Extract selected gene
    selected_match = re.search(r"SELECTED REPRESENTATIVE:\s*(\w+)", result_str, re.IGNORECASE)
    
    if selected_match:
        selected_gene = selected_match.group(1)
    else:
        # Fallback to highest scoring gene
        selected_gene = max(gene_data, key=lambda x: x["score"])["gene"]
    
    # Log results
    os.makedirs("agents/cluster_selector/logs", exist_ok=True)
    with open(f"agents/cluster_selector/logs/cluster_{i+1}.md", "w") as f:
        f.write(f"# Cluster {i+1} Analysis\n\n")
        f.write(f"**Genes:** {', '.join(genes)}\n")
        f.write(f"**Selected:** {selected_gene}\n\n")
        f.write("## Gene Scores\n")
        f.write(json.dumps(gene_data, indent=2))
        f.write("\n\n## Agent Output\n")
        f.write(result_str)
    
    return selected_gene

# ---------------------------
# MAIN PIPELINE
# ---------------------------

def select_representatives(input_csv, output_csv, hgnc_file):
    """Main function to process clusters and select representatives"""
    
    # Load HGNC mapping
    hgnc_map = load_hgnc_map(hgnc_file)
    
    # Initialize tools
    cancer_tool = GeneCancerSearchTool()
    drug_tool = GeneDruggabilityTool(hgnc_map)
    
    # Create selector agent
    selector_agent = Agent(
        role="Cancer Systems Biologist",
        goal="Select the best representative gene from a CNA cluster based on evidence",
        backstory="Skilled at prioritising genes using cancer relevance, SL data, and druggability.",
        llm=llm,
        verbose=True
    )
    
    df = pd.read_csv(input_csv)
    representatives = []

    for i, row in df.iterrows():
        cluster = str(row["BiomarkerCluster_HGNC"])
        genes = [g.strip() for g in cluster.split(",") if g.strip()]

        if not genes:
            representatives.append("NA")
            continue
            
        if len(genes) == 1:
            representatives.append(genes[0])
            continue

        # Check for ovarian oncogene override
        override_gene = None
        for preferred in OVARIAN_ONCOGENES:
            if preferred in genes:
                override_gene = preferred
                break

        if override_gene:
            print(f"[Cluster {i+1}] OVERRIDE: Selecting {override_gene} (known ovarian oncogene)")
            representatives.append(override_gene)
            
            # Log override
            os.makedirs("agents/cluster_selector/logs", exist_ok=True)
            with open(f"agents/cluster_selector/logs/cluster_{i+1}.md", "w") as f:
                f.write(f"## Override Applied\n{override_gene} was selected as it is a known ovarian oncogene.\n")
                f.write(f"\n## Original Cluster\n{', '.join(genes)}\n")
            continue

        # Run full evaluation
        try:
            selected_gene = run_selector_on_cluster(i, genes, cancer_tool, drug_tool, selector_agent)
            representatives.append(selected_gene)
            print(f"[Cluster {i+1}] SELECTED: {selected_gene} from {genes}")
        except Exception as e:
            print(f"[Cluster {i+1}] ERROR: {e}, defaulting to first gene")
            representatives.append(genes[0])

    # Save results
    df["ClusterRepresentative"] = representatives
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"✅ Results saved to {output_csv}")

# ---------------------------
# ENTRYPOINT
# ---------------------------

if __name__ == "__main__":
    input_csv = "agents/assets/cluster_hits.csv"
    output_csv = "agents/cluster_selector/representative_biomarkers.csv"
    hgnc_file = "agents/assets/gene_with_protein_product.txt"
    select_representatives(input_csv, output_csv, hgnc_file)