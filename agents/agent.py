import os
import requests
from typing import Type, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, PrivateAttr
from Bio import Entrez
from crewai import Agent, Task, Crew, Process, LLM
from langchain_openai import ChatOpenAI
from crewai.tools import BaseTool
from ddgs import DDGS

# ---------------------------
# WARNING CONTROL
# ---------------------------
import warnings
import logging
from urllib3.connectionpool import log as urllib3_logger

warnings.filterwarnings('ignore')

# Suppress unclosed socket warnings from urllib3
logging.getLogger("urllib3").setLevel(logging.ERROR)
urllib3_logger.setLevel(logging.CRITICAL)

# ---------------------------
# ENVIRONMENT SETUP
# ---------------------------

# Load the .env file from the same folder as this script
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Load required environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENTREZ_EMAIL = os.getenv("ENTREZ_EMAIL")

# Set required environments for downstream usage
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
Entrez.email = ENTREZ_EMAIL

# ---------------------------
# LLM SETUP (GPT-3.5 Turbo)
# ---------------------------

llm = LLM(model="gpt-4o")

# ---------------------------
# HGNC to Ensembl
# ---------------------------

def load_hgnc_map(filepath: str) -> dict:
    import pandas as pd
    df = pd.read_csv(filepath, sep="\t", dtype=str)
    return dict(zip(df["symbol"], df["ensembl_gene_id"]))

# ---------------------------
# TOOL: PubMed Search
# ---------------------------

class PubMedSearchInput(BaseModel):
    biomarker: str = Field(description="The biomarker gene symbol")
    target: str = Field(description="The target gene symbol")

class PubMedSearchTool(BaseTool):
    name: str = "PubMed Search Tool"
    description: str = "Searches PubMed for SL-related studies for a gene pair"
    args_schema: Type[BaseModel] = PubMedSearchInput

    def _run(self, biomarker: str, target: str) -> str:
        queries = [
            f"{biomarker} AND {target} AND synthetic lethality",
            f"{biomarker} AND cancer",
            f"{target} AND cancer",
            f"{biomarker} AND {target}",
            f"{biomarker} OR {target} AND ovarian cancer",
            f"{target} AND ovarian cancer",
            f"{biomarker} AND ovarian cancer"
        ]

        try:
            all_entries = []
            seen_pmids = set()

            for query in queries:
                handle = Entrez.esearch(db="pubmed", term=query, retmax=5)
                record = Entrez.read(handle)
                pmid_list = record["IdList"]

                if not pmid_list:
                    continue

                handle = Entrez.efetch(db="pubmed", id=",".join(pmid_list), retmode="xml")
                results = Entrez.read(handle)

                for article in results["PubmedArticle"]:
                    pmid = str(article["MedlineCitation"]["PMID"])
                    if pmid in seen_pmids:
                        continue
                    seen_pmids.add(pmid)

                    article_data = article["MedlineCitation"]["Article"]
                    title = article_data.get("ArticleTitle", "No title")
                    abstract = " ".join(article_data["Abstract"]["AbstractText"]) if "Abstract" in article_data else "No abstract"
                    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}"

                    all_entries.append(
                        f"Query: {query}\n- PMID: {pmid} – {url}\n  **Title**: {title.strip()}\n  **Abstract**: {abstract.strip()}"
                    )

            if not all_entries:
                return "No relevant PubMed results found."

            return "\n\n".join(all_entries)

        except Exception as e:
            return f"Error accessing PubMed: {str(e)}"


# ---------------------------
# TOOL: Open Targets Search
# ---------------------------

class OpenTargetsInput(BaseModel):
    target: str = Field(description="The target gene symbol")

class OpenTargetsTool(BaseTool):
    name: str = "Open Targets Tool"
    description: str = "Fetches drug info from Open Targets for the target gene"
    args_schema: Type[BaseModel] = OpenTargetsInput

    _hgnc_map: dict = PrivateAttr()

    def __init__(self, hgnc_map: dict):
        super().__init__()
        self._hgnc_map = hgnc_map  # ← use _hgnc_map, not hgnc_map

    def symbol_to_ensembl(self, symbol: str) -> Optional[str]:
        return self._hgnc_map.get(symbol)

    def _run(self, target: str) -> str:
        ensembl_id = self.symbol_to_ensembl(target)
        if not ensembl_id:
            return f"No Ensembl ID found for gene: {target}"

        query = """
        query KnownDrugsQuery($ensgId: String!, $cursor: String, $size: Int) {
          target(ensemblId: $ensgId) {
            knownDrugs(cursor: $cursor, size: $size) {
              rows {
                phase
                status
                urls {
                  url
                }
                disease {
                  name
                }
                drug {
                  name
                }
                mechanismOfAction
              }
            }
          }
        }
        """

        variables = {
            "ensgId": ensembl_id,
            "cursor": None,
            "size": 20
        }

        url = "https://api.platform.opentargets.org/api/v4/graphql"
        res = requests.post(url, json={"query": query, "variables": variables})
        res.raise_for_status()
        drugs = res.json()["data"]["target"]["knownDrugs"]["rows"]

        if not drugs:
            return f"No drugs found for {target} ({ensembl_id})"

        output = [f"Drugs targeting {target} ({ensembl_id}):"]
        for d in drugs:
            drug_name = d["drug"]["name"]
            moa = d["mechanismOfAction"] or "N/A"
            disease = d["disease"]["name"]
            status = d["status"]
            phase = d["phase"]
            link = next((u["url"] for u in d["urls"] if u.get("url")), "N/A")
            output.append(
                f"- {drug_name}:\n"
                f"  • Phase: {phase}\n"
                f"  • Status: {status}\n"
                f"  • MoA: {moa}\n"
                f"  • Disease: {disease}\n"
                f"  • Link: {link}"
            )

        return "\n".join(output)

# ---------------------------
# TOOL: ClinicalTrials.gov Search
# ---------------------------

class ClinicalTrialsInput(BaseModel):
    gene: str = Field(description="Gene symbol to search for in clinical trial records")

class ClinicalTrialsTool(BaseTool):
    name: str = "Clinical Trials Tool"
    description: str = "Searches ClinicalTrials.gov for trials involving the gene"
    args_schema: Type[BaseModel] = ClinicalTrialsInput

    def _run(self, gene: str) -> str:
        res = requests.get(
            "https://clinicaltrials.gov/api/v2/studies",
            params={"query.term": gene, "pageSize": 10}
        )
        res.raise_for_status()
        studies = res.json().get("studies", [])

        if not studies:
            return f"No clinical trials found for gene: {gene}."

        output = [f"Clinical trials mentioning {gene}:\n"]
        for study in studies:
            try:
                ps = study["protocolSection"]
                ident = ps["identificationModule"]
                status = ps.get("statusModule", {})
                conditions = ps.get("conditionsModule", {}).get("conditions", [])
                design = ps.get("designModule", {})
                nct_id = ident["nctId"]
                title = ident.get("briefTitle", "No title")
                condition_str = ", ".join(conditions) or "No condition listed"
                phase = ", ".join(design.get("phases", [])) or "N/A"
                trial_status = status.get("overallStatus", "Unknown")
                trial_url = f"https://clinicaltrials.gov/study/{nct_id}"

                output.append(
                    f"- [{title}]({trial_url})\n"
                    f"  - **NCT ID**: {nct_id}\n"
                    f"  - **Phase**: {phase}\n"
                    f"  - **Status**: {trial_status}\n"
                    f"  - **Condition(s)**: {condition_str}"
                )
            except Exception as e:
                output.append(f"- Failed to parse study: {e}")

        return "\n\n".join(output)

# ---------------------------
# Markdown REPORT WRITER
# ---------------------------

def write_markdown_report(biomarker, target, content, folder="agents/reports"):
    filename = f"{folder}/{biomarker}_{target}_report.md"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    final_text = content.output if hasattr(content, "output") else str(content)

    with open(filename, "w") as f:
        f.write(f"# Synthetic Lethality Report: {biomarker} - {target}\n\n")
        f.write(final_text)

    print(f"✅ Markdown report saved to {filename}")

# ---------------------------
# LOGS 
# ---------------------------
    
def log_agent_output(biomarker, target, agent_name, content):
    filename = f"agents/logs/{biomarker}_{target}_{agent_name}.md"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(content.output if hasattr(content, "output") else str(content))

# ---------------------------
# CREW SETUP
# ---------------------------

def run_research(biomarker, target):
    pubmed_tool = PubMedSearchTool()

    hgnc_map = load_hgnc_map("agents/assets/gene_with_protein_product.txt")
    opentargets_tool = OpenTargetsTool(hgnc_map)

    clinical_trials_tool = ClinicalTrialsTool()

    pubmed = Agent(
    role="Cancer Literature Analyst",
    goal="Retrieve PubMed abstracts supporting synthetic lethality and cancer relevance",
    backstory="Expert in mining literature to assess the scientific and translational value of candidate gene pairs.",
    tools=[pubmed_tool],
    allow_delegation=False
    )

    opentargets = Agent(
    role="Drug Target Analyst",
    goal="Retrieve drug/inhibitor data for each gene from Open Targets",
    backstory="Expert in therapeutic targeting, mechanisms of action, and drug status evaluation.",
    tools=[opentargets_tool],
    allow_delegation=False
    )

    trials = Agent(
    role="Clinical Trials Specialist",
    goal="Retrieve information about ongoing or past clinical trials for each gene",
    backstory="Specialist in mining ClinicalTrials.gov for drug development and biomarker translation data.",
    tools=[clinical_trials_tool],
    allow_delegation=False
    )

    analyst = Agent(
        role="Biomedical Research Analyst",
        goal="Analyse and synthesise relevance of findings",
        backstory="Skilled at turning raw search data into structured biomedical insights with emphasis on cancer relevance.",
        verbose=True,
        llm=llm
    )

    qa = Agent(
        role="Scientific QA Reviewer",
        goal="Ensure the report is focused, evidence-based, and cancer-relevant. If not, recommend further search.",
        backstory=(
            "You are a former editor at a top cancer research journal. You assess whether the findings are specific, actionable, and correctly sourced. "
            "If the output reads like generic filler, lacks citations, or overstates the evidence, you MUST reject the report and return feedback only."
        ),
        verbose=True,
        llm=llm
    )

    confidence_agent = Agent(
        role="Confidence Scoring Evaluator",
        goal="Score the strength of evidence for the SL interaction",
        backstory=(
            "You are a rigorous SL evidence evaluator. "
            "You score the strength of evidence based on peer-reviewed literature, drug info, cancer relevance, and quality of sources. "
            "You output a score from 0 to 100 and a justification for your score."
        ),
        verbose=True,
        llm=llm
    )

    writer = Agent(
        role="Scientific Technical Writer",
        goal="Write a clear, well-structured markdown report for clinicians and researchers.",
        backstory="Expert in translating dense biomedical content into readable, cited reports.",
        verbose=True,
        llm=llm
    )

    # Tasks
    pubmed_task = Task(
        description=f"""
        Search PubMed for literature mentioning the genes **{biomarker}** and **{target}**.

        Prioritise:
        - Any **synthetic lethality** interactions between the two genes.
        - Studies mentioning **either gene** in a cancer context, especially **ovarian** or **breast** cancer.
        - Abstracts with relevance to **gene regulation**, **DNA repair**, or **tumour progression**.

        Include:
        - Up to 5 abstracts per query.
        - PubMed IDs, titles, and clean abstracts.
        - Direct URLs to each abstract.

        This task is strictly PubMed-focused. Do not include drug or clinical trial data.
        """,
        expected_output="List of relevant PubMed abstracts with PMIDs, summaries, and relevance notes.",
        agent=pubmed
    )

    drug_task = Task(
        description=f"""
        Use the Open Targets API to search for **drugs or inhibitors** associated with **{biomarker}** and **{target}**.

        Include:
        - Drug name, type, and approval status (e.g., Approved, Clinical Trial, Preclinical).
        - Disease context or cancer type targeted.
        - Mechanism of action (MoA) if available.
        - If no drug is found for a gene, state that clearly.

        Output must be structured by gene symbol.

        This task is strictly drug-focused. Do not include PubMed or trial data.
        """,
        expected_output="Structured drug data from Open Targets for each gene.",
        agent=opentargets
    )

    clinical_task = Task(
        description=f"""
        Search ClinicalTrials.gov for **active or past clinical trials** involving **{biomarker}** and **{target}**.

        Include for each trial:
        - Trial title
        - NCT ID
        - Trial phase (e.g. Phase I, II, III)
        - Status (e.g. Recruiting, Completed)
        - Condition/disease being studied
        - Direct link to trial

        Focus on **cancer-related** trials, especially those in **ovarian** or **breast** cancer.

        This task is strictly ClinicalTrials.gov-focused. Do not include drug or PubMed data.
        """,
        expected_output="Structured list of relevant clinical trials involving either gene.",
        agent=trials
    )

    analysis_task = Task(
        description="Analyse search results and assess their relevance to synthetic lethality and cancer context.",
        expected_output="A structured analysis of whether this gene pair is synthetically lethal, and if drugs exist.",
        context=[pubmed_task, drug_task, clinical_task],
        agent=analyst
    )

    qa_task = Task(
        description="Review the analysis for clarity, depth, and relevance. If not strong, suggest more search or context refinement. If rejected, output must start with 'REJECTED: <reason>'.",
        expected_output="Approve or deny readiness for final writing. Suggest improvements if needed.",
        context=[analysis_task],
        agent=qa
    )

    confidence_task = Task(
        description=f"""
        Score the synthetic lethality (SL) gene pair **{biomarker} – {target}** using this weighted rubric:
        1. **SL Evidence (PubMed) – 40 points**
           - Full points if at least one abstract **explicitly** mentions synthetic lethality between the pair.
           - Partial (10–30) for synergy, DNA repair links, or indirect evidence.
        2. **Drug Evidence (Open Targets) – 25 points**
           - 20–25 points for drugs with known MoA and cancer relevance.
           - 10–15 points for partial data (e.g. no disease context or unknown status).
           - <10 if only weak or inactive agents.
        3. **Clinical Trials – 15 points**
           - 10–15 for direct trial mentions in ovarian or breast cancer.
           - <10 if general cancer trials or gene only appears as exploratory.
        4. **Cancer-Relevant Literature – 20 points**
           - 15–20 for mentions in ovarian or breast cancer.
           - 5–10 for mentions in other cancers without SL.
           - 0 if no cancer relevance at all.
        Use this exact output format:
        ```
        Confidence Score: <score>/100
        SL Evidence (PubMed): <x>/40 – <justification>
        Drug Evidence (Open Targets): <x>/25 – <justification>
        Clinical Trials: <x>/15 – <justification>
        Cancer Literature (PubMed): <x>/20 – <justification>
        Reason: <Wrap-up sentence about strength/weakness of evidence>
        ```
        If there’s no evidence at all:
        ```
        Confidence Score: 10/100
        SL Evidence (PubMed): 0/40 – No evidence found
        Drug Evidence (Open Targets): 5/25 – No drug info
        Clinical Trials: 5/15 – No trials found
        Cancer Literature (PubMed): 0/20 – Gene not cancer-linked
        Reason: No meaningful data found to support SL, druggability or cancer relevance.
        ```
        """,
        expected_output="Structured score with component breakdown and rationale.",
        context=[qa_task, pubmed_task, drug_task, clinical_task],
        agent=confidence_agent
    )   

    writing_task = Task(
        description=f"""
    Using only the search_task output, write a structured markdown report for the gene pair: **{biomarker} – {target}**.

    Mandatory report sections:

    1. **Background on Genes** – Basic roles and relevance to cancer (only if supported by literature).
    2. **SL Evidence (with PMIDs)** – Include ONLY synthetic lethality mentions explicitly stated in abstracts. Cite with PMID and link.
    3. **Drug Targets (with Open Targets data)** – Summarise any known inhibitors, status, mechanism of action, and disease area.
    4. **Clinical Trials** – List any relevant trials involving either gene from ClinicalTrials.gov. Include:
       - NCT ID
       - Trial Title (linked)
       - Phase
       - Status
       - Condition
       Skip this section if no trials found.

    5. **Translational Potential (across cancers)** – If SL evidence or drugs exist in other cancers, describe them briefly.

    6. **Conclusion** – Wrap-up summary.

    7. **References** – Markdown list of cited PubMed PMIDs in this format:
       - PMID: 28112439 – https://pubmed.ncbi.nlm.nih.gov/28112439  
         Title: ABCF2, an Nrf2 target gene, contributes to cisplatin resistance in ovarian cancer cells.

    Strict Rules:
    - Use **only** abstracts and PMIDs found in search_task.
    - Do NOT fabricate PMIDs, titles, or URLs.
    - Do NOT guess drug info not found in Open Targets.
    - Do NOT invent clinical trial info not found in ClinicalTrials.gov tool output.
    - Do NOT infer synthetic lethality unless explicitly stated in the abstract.
    - If no evidence is found, clearly say so. Do NOT write filler or boilerplate.

    If the QA task result begins with `REJECTED:`, do not write a report. Output only the rejection message.

    Ensure all content is written in **clean, clinical markdown** suitable for cancer research reporting.
    """,
        expected_output="A clean, markdown-formatted report with structured citations from real PubMed and trial results.",
        context=[qa_task, pubmed_task, drug_task, clinical_task],
        agent=writer
    )


    # Run crew
    crew = Crew(
        agents=[pubmed, opentargets, trials, analyst, qa, confidence_agent, writer],
        tasks=[pubmed_task, drug_task, clinical_task, analysis_task, qa_task, confidence_task, writing_task],
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()

    # Logs
    log_agent_output(biomarker, target, "pubmed", pubmed_task.output)
    log_agent_output(biomarker, target, "opentargets", drug_task.output)
    log_agent_output(biomarker, target, "clinicaltrials", clinical_task.output)
    log_agent_output(biomarker, target, "analysis", analysis_task.output)
    log_agent_output(biomarker, target, "qa", qa_task.output)
    log_agent_output(biomarker, target, "confidence", confidence_task.output)
    log_agent_output(biomarker, target, "writer", result)

    # Extract score
    conf_text = confidence_task.output.output if hasattr(confidence_task.output, "output") else str(confidence_task.output)
    try:
        score_line = next(line for line in conf_text.splitlines() if "Confidence Score" in line)
        score = int(score_line.split(":")[1].strip().split("/")[0])
    except:
        score = 0

    # QA rejection?
    qa_text = str(qa_task.output)
    rejected = qa_text.startswith("REJECTED:")

    # Save to appropriate location
    if rejected or score < 50:
        header = f"⚠️ LOW CONFIDENCE REPORT ({score}/100)\n\n"
        fallback_text = header + (result.output if hasattr(result, "output") else str(result))
        write_markdown_report(biomarker, target, fallback_text, folder="agents/low_confidence_reports")
        print(f"⚠️ Report saved to low confidence folder due to low score or QA rejection.")
    else:
        write_markdown_report(biomarker, target, result)

# ---------------------------
# RUN INTERACTIVELY
# ---------------------------

if __name__ == "__main__":
    print("🔬 SL Report Generator")
    biomarker = input("Enter biomarker gene symbol (e.g. MYC): ").strip().upper()
    target = input("Enter target gene symbol (e.g. CHEK1): ").strip().upper()
    run_research(biomarker, target)
