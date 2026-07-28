"""
Single entry point that backend/app/services/agent_service.py calls into.
Decides which crew or agent handles a given workflow, and keeps a simple
iteration count so a workflow can't loop forever between handoffs.
"""
from agents.crews.claim_processing_crew import run_claim_adjudication
from agents.crews.fraud_detection_crew import run_fraud_investigation
from agents.pydantic_agents.kyc_verifier import verify_kyc
from agents.pydantic_agents.policy_recommender import recommend_policy
from guardrails.agent_guard import check_iteration
from guardrails.input_guard import apply_input_guardrail

WORKFLOWS = {
    "claim_adjudication": run_claim_adjudication,
    "fraud_investigation": run_fraud_investigation,
}


def dispatch_claim_workflow(workflow_name: str, context: str, iteration: int = 0) -> str:
    """Runs a crew-based workflow (claim_adjudication or
    fraud_investigation). context gets PII-masked before it goes anywhere
    near an LLM."""
    if workflow_name not in WORKFLOWS:
        raise ValueError(f"Unknown workflow '{workflow_name}'. Valid options: {list(WORKFLOWS)}")

    check_iteration(iteration)  # raises AgentLoopError if this workflow is looping
    safe_context = apply_input_guardrail(context)
    return WORKFLOWS[workflow_name](safe_context)


def dispatch_policy_recommendation(customer_profile: str):
    safe_profile = apply_input_guardrail(customer_profile)
    return recommend_policy(safe_profile)


def dispatch_kyc_verification(ocr_result: str, customer_record: str):
    safe_ocr = apply_input_guardrail(ocr_result)
    safe_record = apply_input_guardrail(customer_record)
    return verify_kyc(safe_ocr, safe_record)
