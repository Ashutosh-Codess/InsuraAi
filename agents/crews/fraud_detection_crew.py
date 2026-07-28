"""
Fraud Investigation Team, per the doc:
    Agent 1 (Anomaly Detector) -> Agent 2 (Cross-Checker) -> Agent 3 (Risk Auditor)

Same rule as the claim crew - this produces a fraud score and reasoning,
it doesn't reject anything itself. High scores get routed to a human via
guardrails/output_guard.py's requires_human_review().
"""
import os

import yaml
from crewai import Agent, Crew, LLM, Process, Task

from agents.tools.database_tool import database_lookup

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

llm = LLM(model=f"ollama/{OLLAMA_MODEL}", base_url=OLLAMA_BASE_URL, api_base=OLLAMA_BASE_URL)


def _load_prompt(filename: str) -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", filename)
    with open(path) as f:
        return yaml.safe_load(f)


fraud_prompt = _load_prompt("fraud_analyst.yaml")

anomaly_agent = Agent(
    role="Anomaly Detector",
    goal="Check this claim's amount and timing against the customer's claim frequency for anything unusual.",
    backstory="You spot patterns in claim frequency and amounts before anyone else looks at the case.",
    tools=[database_lookup],
    llm=llm,
    allow_delegation=False,
)

cross_checker_agent = Agent(
    role="Cross-Checker",
    goal="Check this customer and claim against historical fraud records and investigation logs.",
    backstory="You dig through past cases to see if this customer or claim pattern has come up before.",
    tools=[database_lookup],
    llm=llm,
    allow_delegation=False,
)

risk_auditor_agent = Agent(
    role=fraud_prompt["role"],
    goal=fraud_prompt["goal"],
    backstory=fraud_prompt["backstory"],
    llm=llm,
    allow_delegation=False,
)


def run_fraud_investigation(claim_context: str) -> str:
    """claim_context should already have PII masked via
    guardrails/input_guard.py before it gets here."""
    anomaly_task = Task(
        description=f"Check for anomalies in claim frequency and amount for this claim: {claim_context}",
        expected_output="A list of any anomalies found, or a note that nothing unusual was found.",
        agent=anomaly_agent,
    )

    cross_check_task = Task(
        description="Cross-check this customer's history against past fraud investigation records.",
        expected_output="A note on whether this customer or claim pattern has prior fraud flags.",
        agent=cross_checker_agent,
        context=[anomaly_task],
    )

    audit_task = Task(
        description="Based on the anomaly check and cross-check, produce a fraud_score between 0 and 1 with justification.",
        expected_output="A fraud score and a plain-language explanation of what drove it.",
        agent=risk_auditor_agent,
        context=[anomaly_task, cross_check_task],
    )

    crew = Crew(
        agents=[anomaly_agent, cross_checker_agent, risk_auditor_agent],
        tasks=[anomaly_task, cross_check_task, audit_task],
        process=Process.sequential,
    )

    return str(crew.kickoff())
