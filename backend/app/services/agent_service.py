"""
This is the only file in backend/ that talks directly to agents/. Keeping
that boundary in one place means the rest of the backend doesn't need to
know anything about CrewAI or PydanticAI - it just calls these functions.

Requires agents/, guardrails/, rag/, and vector_db/ to be on the Python
path - see docker-compose.yml, the backend container mounts them and sets
PYTHONPATH so `import agents...` works from here.
"""
from agents.orchestrator import (
    dispatch_claim_workflow,
    dispatch_kyc_verification,
    dispatch_policy_recommendation,
)
from guardrails.output_guard import requires_human_review


def process_claim_with_agents(claim_context: str, claimed_amount: float, fraud_score: float | None) -> dict:
    adjudication_result = dispatch_claim_workflow("claim_adjudication", claim_context)
    fraud_result = dispatch_claim_workflow("fraud_investigation", claim_context)

    review = requires_human_review(claimed_amount, fraud_score)

    return {
        "adjudication": adjudication_result,
        "fraud_analysis": fraud_result,
        "requires_human_review": review["required"],
        "review_reason": review["reason"],
    }


def get_policy_recommendation(customer_profile: str) -> dict:
    recommendation = dispatch_policy_recommendation(customer_profile)
    return recommendation.model_dump()


def verify_customer_kyc(ocr_result: str, customer_record: str) -> dict:
    verification = dispatch_kyc_verification(ocr_result, customer_record)
    return verification.model_dump()
