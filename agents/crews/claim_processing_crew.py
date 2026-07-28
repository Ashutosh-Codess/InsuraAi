"""
Claim Adjudication Team, per the doc:
    Agent 1 (OCR/Extraction) -> Agent 2 (Coverage Validator) -> Agent 3 (Payout Assessor)

This crew doesn't decide anything final - it produces a recommendation
that still has to go through a human agent (see api/v1/claims.py
decide_claim endpoint). The Payout Assessor's number is a suggestion, not
an approval.

Note on the LLM: the doc says "open-weight LLMs (Llama 3, Qwen 2.5, or
DeepSeek)" without picking one or saying how it's served. I went with
Ollama serving llama3 by default since that's the simplest way to run an
open-weight model locally - change OLLAMA_MODEL / OLLAMA_BASE_URL if
you're running something else.
"""
import os

import yaml
from crewai import Agent, Crew, LLM, Process, Task

from agents.tools.database_tool import database_lookup
from agents.tools.rag_tool import knowledge_base_search

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

llm = LLM(model=f"ollama/{OLLAMA_MODEL}", base_url=OLLAMA_BASE_URL, api_base=OLLAMA_BASE_URL)


def _load_prompt(filename: str) -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", filename)
    with open(path) as f:
        return yaml.safe_load(f)


coverage_prompt = _load_prompt("claim_assessor.yaml")

ocr_agent = Agent(
    role="Document Extractor",
    goal="Extract key fields (amounts, dates, names) from claim documents so the rest of the crew has structured data to work with.",
    backstory="You pull out the facts from invoices, reports, and forms without interpreting them.",
    llm=llm,
    allow_delegation=False,
)

coverage_agent = Agent(
    role=coverage_prompt["role"],
    goal=coverage_prompt["goal"],
    backstory=coverage_prompt["backstory"],
    tools=[knowledge_base_search, database_lookup],
    llm=llm,
    allow_delegation=False,
)

payout_agent = Agent(
    role="Payout Assessor",
    goal="Calculate a suggested settlement amount based on the claim, policy coverage limits, and deductible.",
    backstory="You do the arithmetic on claims that have already been confirmed as covered - you don't re-litigate coverage.",
    tools=[database_lookup],
    llm=llm,
    allow_delegation=False,
)


def run_claim_adjudication(claim_context: str) -> str:
    """claim_context should already have PII masked via
    guardrails/input_guard.py before it gets here."""
    extract_task = Task(
        description=f"Extract the key facts from this claim: {claim_context}",
        expected_output="A short structured summary of dates, amounts, and incident details.",
        agent=ocr_agent,
    )

    coverage_task = Task(
        description="Using the extracted claim facts, check whether this incident is covered under the policy. Search policy_terms for the relevant clause.",
        expected_output="A statement of whether the claim is covered, citing the specific clause or exclusion.",
        agent=coverage_agent,
        context=[extract_task],
    )

    payout_task = Task(
        description="If the claim is covered, calculate a suggested payout amount based on coverage limits and deductible.",
        expected_output="A suggested payout amount with the calculation shown, or a note that the claim isn't covered.",
        agent=payout_agent,
        context=[coverage_task],
    )

    crew = Crew(
        agents=[ocr_agent, coverage_agent, payout_agent],
        tasks=[extract_task, coverage_task, payout_task],
        process=Process.sequential,
    )

    return str(crew.kickoff())
