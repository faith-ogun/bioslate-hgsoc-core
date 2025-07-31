# cluster_selector_agent.py

import os
import json
import re
import pandas as pd
import requests
from dotenv import load_dotenv
from typing import Type, Optional
from Bio import Entrez
from pydantic import BaseModel, Field, PrivateAttr
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool

# --------------------------
# Schemas
# --------------------------

class GeneInput(BaseModel):
    gene: str = Field(..., description="Gene symbol to search in PubMed")

class TargetInput(BaseModel):
    target: str = Field(..., description="Target gene symbol to query")

# --------------------------
# PubMed Tool
# --------------------------

class PubMedTool(BaseTool):
    name: str = "PubMedTool"
    description: str = "Check cancer and synthetic lethality relevance from PubMed"
    args_schema: Type[BaseModel] = GeneInput

    def _run(self, gene: str) -> str:
        Entrez.email = os.getenv("ENTREZ_EMAIL")

        def has_hits(term):
            try:
                handle = Entrez.esearch(db="pubmed", term=term, retmax=1)
                return bool(Entrez.read(handle)["IdList"])
            except:
                return False

        results = {
            "cancer": has_hits(f"{gene} AND cancer"),
            "ovarian": has_hits(f"{gene} AND ovarian cancer"),
            "sl": has_hits(f"{gene} AND synthetic lethality"),
            "onc": has_hits(f"{gene} AND oncogene")
        }
        return json.dumps(results)

# --------------------------
# Open Targets Tool
# --------------------------

class OpenTargetsTool(BaseTool):
    name: str = "OpenTargetsTool"
    description: str = "Checks if a gene is druggable using Open Targets GraphQL"
    args_schema: Type[BaseModel] = TargetInput
    _hgnc_map: dict = PrivateAttr()

    def __init__(self, hgnc_map):
        super().__init__()
        self._hgnc_map = hgnc_map

    def symbol_to_ensembl(self, symbol: str) -> Optional[str]:
        return self._hgnc_map.get(symbol)

    def _run(self, target: str) -> str:
        ensembl_id = self.symbol_to_ensembl(target)
        if not ensembl_id:
            return "No Ensembl ID found"

        query = """
        query KnownDrugsQuery($ensgId: String!, $cursor: String, $size: Int) {
          target(ensemblId: $ensgId) {
            knownDrugs(cursor: $cursor, size: $size) {
              rows {
                drug {
                  name
                }
              }
            }
          }
        }
        """
        url = "https://api.platform.opentargets.org/api/v4/graphql"
        variables = {"ensgId": ensembl_id, "cursor": None, "size": 1}

        try:
            res = requests.post(url, json={"query": query, "variables": variables})
            res.raise_for_status()
            drugs = res.json()["data"]["target"]["knownDrugs"]["rows"]
            return "Druggable" if drugs else "Not Druggable"
        except:
            return "Error"

# --------------------------
# Ovarian Oncogene Overrides
# --------------------------

OVARIAN_ONCOGENES = {
    "CCNE1", "MYC", "KRAS", "MECOM", "PIK3CA", "BCL2", "CDK2", "CDK12",
    "BRD4", "BIRC5", "RSF1", "YAP1", "AKT2"
}

# --------------------------
# Helpers
# --------------------------

def load_hgnc_map(hgnc_file):
    df = pd.read_csv(hgnc_file, sep="\t", dtype=str)
    return dict(zip(df["symbol"], df["ensembl_gene_id"]))

def create_agent(llm):
    return Agent(
        role="Cancer Systems Biologist",
        goal="Select the best representative gene from a CNA cluster based on evidence",
        backstory="Skilled at prioritising genes using cancer relevance, SL data, and druggability.",
        llm=llm,
        verbose=True
    )

def extract_declared_gene(output: str, gene_list: list[str]) -> Optional[str]:
    pattern = r"(?:select|chosen|recommend|representative).*?\b(" + "|".join(gene_list) + r")\b"
    match = re.search(pattern, output, flags=re.IGNORECASE)
    return match.group(1) if match else None

def run_selector_on_cluster(i, genes, pubmed_tool, ot_tool, selector_agent):
    gene_data = []
    prompt = "## Candidate Genes:\n"

    # ✅ Step 0: Manual override if known ovarian oncogene is present
    for preferred in OVARIAN_ONCOGENES:
        if preferred in genes:
            os.makedirs("agents/cluster_selector/logs", exist_ok=True)
            with open(f"agents/cluster_selector/logs/cluster_{i+1}.md", "w") as f:
                f.write(f"## Override Applied\n{preferred} was selected as it is a known ovarian oncogene.\n")
                f.write(f"\n## Original Cluster\n{', '.join(genes)}\n")
            print(f"[Cluster {i+1}] OVERRIDE: Selecting {preferred} due to known oncogene status.")
            return preferred

    # If no override hit, continue with agent evaluation
    for gene in genes:
        pubmed_raw = pubmed_tool._run(gene=gene)
        ot = ot_tool._run(target=gene)

        try:
            pubmed = json.loads(pubmed_raw)
        except:
            pubmed = {"cancer": 0, "ovarian": 0, "sl": 0, "onc": 0}

        score = (
            20 * int(pubmed["cancer"]) +
            20 * int(pubmed["ovarian"]) +
            20 * int(pubmed["sl"]) +
            20 * int(pubmed["onc"]) +
            20 * (1 if ot == "Druggable" else 0)
        )
        gene_data.append({"gene": gene, "score": score})
        prompt += f"- {gene}: score={score}, cancer={pubmed['cancer']}, ovarian={pubmed['ovarian']}, SL={pubmed['sl']}, ONC={pubmed['onc']}, druggable={ot}\n"

    prompt += "\nChoose the best representative gene from this list and explain your reasoning clearly and unambiguously. End your answer by naming the selected gene explicitly."

    task = Task(
        description=prompt,
        expected_output="One representative gene with reasoning. Return the chosen gene explicitly in the last sentence.",
        agent=selector_agent
    )
    crew = Crew(agents=[selector_agent], tasks=[task], verbose=True)
    result = crew.kickoff()
    result_str = str(result)

    declared_gene = extract_declared_gene(result_str, genes)

    if declared_gene:
        selected_gene = declared_gene
    else:
        selected_gene = max(gene_data, key=lambda x: x["score"])["gene"]

    # Log output
    os.makedirs("agents/cluster_selector/logs", exist_ok=True)
    with open(f"agents/cluster_selector/logs/cluster_{i+1}.md", "w") as f:
        f.write("## Gene Scores\n")
        f.write(json.dumps(gene_data, indent=2))
        f.write("\n\n## Agent Output\n")
        f.write(result_str)

    return selected_gene

# --------------------------
# Main Pipeline
# --------------------------

def select_representatives(input_csv, output_csv, hgnc_file):
    load_dotenv()
    hgnc_map = load_hgnc_map(hgnc_file)
    pubmed_tool = PubMedTool()
    ot_tool = OpenTargetsTool(hgnc_map)
    llm = LLM(model="gpt-4o")
    selector_agent = create_agent(llm)

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

        try:
            rep = run_selector_on_cluster(i, genes, pubmed_tool, ot_tool, selector_agent)
        except Exception as e:
            print(f"Cluster {i+1} failed: {e}")
            rep = genes[0]

        representatives.append(rep)

    df["ClusterRepresentative"] = representatives
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Output saved to {output_csv}")

# --------------------------
# Entrypoint
# --------------------------

if __name__ == "__main__":
    input_csv = "agents/assets/cluster_hits.csv"
    output_csv = "agents/cluster_selector/representative_biomarkers.csv"
    hgnc_file = "agents/assets/gene_with_protein_product.txt"
    select_representatives(input_csv, output_csv, hgnc_file)
