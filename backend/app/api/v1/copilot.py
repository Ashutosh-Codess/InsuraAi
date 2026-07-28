"""
Two endpoints: a plain search over the knowledge base, and a streaming
chat endpoint grounded in that search.

Performance notes:
  - The RAG retriever uses sentence-transformers (pre-warmed at startup)
    so the first query is fast.
  - The Ollama LLM stream starts immediately; the browser sees the first
    tokens arrive even while the model is still generating.
  - max_tokens=400 caps generation length so the model doesn't run forever.
  - If Ollama is unreachable the endpoint returns a graceful error, not a
    500 crash.
"""
import os
import re

import httpx
import yaml
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from openai import OpenAI, APIConnectionError
from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.claim import Claim
from app.models.customer import Customer
from app.models.policy import Policy
from app.models.user import User
from guardrails.input_guard import apply_input_guardrail
from guardrails.output_guard import check_faithfulness
from rag.retriever import retrieve
from vector_db.collections import ALL_COLLECTIONS

router = APIRouter()

# Local Ollama server — defaults to 127.0.0.1 for local dev.
# In Docker the env var is set to http://ollama:11434/v1
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Capped so long prompts don't stall the browser for minutes.
MAX_TOKENS = int(os.getenv("COPILOT_MAX_TOKENS", "400"))

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=OLLAMA_BASE_URL,
            api_key="ollama",
            http_client=httpx.Client(timeout=180),
        )
    return _client


def _load_system_prompt() -> str:
    path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "..",
        "prompts",
        "policy_copilot.yaml",
    )

    with open(path, encoding="utf-8") as f:
        prompt = yaml.safe_load(f)

    return (
        f"{prompt['backstory']}\n\n"
        f"Goal: {prompt['goal']}\n\n"
        f"Instructions:\n{prompt['instructions']}"
    )


SYSTEM_PROMPT = _load_system_prompt()


class SearchRequest(BaseModel):
    collection: str
    query: str


class SearchResponse(BaseModel):
    results: list[dict]
    faithfulness_note: str | None = None


class AskRequest(BaseModel):
    collection: str
    question: str


class ContextualChatRequest(BaseModel):
    message: str


def _policy_number(policy_id) -> str:
    return f"POL-{str(policy_id).replace('-', '')[:8].upper()}"


def _claim_number(claim_id) -> str:
    return f"CLM-{str(claim_id).replace('-', '')[:8].upper()}"


def _matches_question(value: str, question: str) -> bool:
    """Match an ID/name fragment supplied by a user without exposing other data."""
    normal_value = re.sub(r"[^a-z0-9]", "", str(value).lower())
    normal_question = re.sub(r"[^a-z0-9]", "", question.lower())
    return len(normal_value) >= 5 and normal_value in normal_question


def _agent_claim_line(claim: Claim, db: Session) -> str:
    customer = db.get(Customer, claim.customer_id)
    policy = db.get(Policy, claim.policy_id)
    fraud = (
        f"; fraud assessment: {claim.fraud_label} ({float(claim.fraud_score):.0%})"
        if claim.fraud_score is not None else "; fraud assessment: not run"
    )
    return (
        f"• {_claim_number(claim.id)} — {customer.name if customer else 'Unknown customer'}; "
        f"policy {_policy_number(claim.policy_id)} ({policy.name if policy else claim.type}); "
        f"{claim.type} claim for ₹{float(claim.claimed_amount):,.2f}; status: {claim.status}{fraud}."
    )


@router.post("/copilot/contextual-chat")
def contextual_chat(
    payload: ContextualChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return question-specific, role-scoped live insurance context."""
    question = payload.message.strip() or "account overview"
    query = question.lower()

    if current_user.role in {"agent", "admin"}:
        claims = db.query(Claim).order_by(Claim.submitted_at.desc()).all()
        customers = db.query(Customer).all()
        identified = next((claim for claim in claims if _matches_question(_claim_number(claim.id), question) or _matches_question(claim.id, question)), None)
        if identified:
            return {"reply": f"Claim details for {_claim_number(identified.id)}:\n{_agent_claim_line(identified, db)}\n\nYou can run AI analysis from the Fraud Monitor before recording a decision."}

        high_risk = [claim for claim in claims if claim.fraud_score is not None and float(claim.fraud_score) >= 0.4]
        pending = [claim for claim in claims if claim.status in {"submitted", "under_review"}]
        if any(term in query for term in ("risk", "fraud", "suspicious", "flagged", "high risk")):
            selected = high_risk
            heading = "Claims currently flagged for fraud review"
            if not selected:
                return {"reply": "No claims are currently flagged for fraud review. You can run AI analysis from the Fraud Monitor to assess unreviewed claims."}
        elif any(term in query for term in ("pending", "queue", "review", "submitted")):
            selected = pending
            heading = "Claims awaiting agent review"
            if not selected:
                return {"reply": "There are no claims waiting for agent review right now."}
        else:
            selected = []
            heading = ""

        if not selected:
            matched_customer = next((customer for customer in customers if customer.name and customer.name.lower() in query), None)
            if matched_customer:
                selected = [claim for claim in claims if claim.customer_id == matched_customer.id]
                heading = f"Claims for {matched_customer.name}"

        if selected:
            lines = [f"{heading} ({len(selected)}):", *[_agent_claim_line(claim, db) for claim in selected]]
            return {"reply": "\n".join(lines)}

        total_value = sum(float(claim.claimed_amount or 0) for claim in pending)
        lines = [
            f"Agent portfolio summary for: {question}",
            f"There are {len(customers)} customers, {len(claims)} total claims, and {len(pending)} awaiting review (₹{total_value:,.2f}).",
            f"{len(high_risk)} claim(s) have a fraud score of 40% or higher.",
            "Ask for the review queue, high-risk claims, a customer name, or a claim number for a focused answer.",
        ]
        return {"reply": "\n".join(lines)}

    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        return {"reply": "Your customer profile is not complete yet. Please complete your profile before reviewing policies or filing a claim."}

    policies = db.query(Policy).filter(Policy.customer_id == customer.id).all()
    claims = db.query(Claim).filter(Claim.customer_id == customer.id).order_by(Claim.submitted_at.desc()).all()
    identified_claim = next((claim for claim in claims if _matches_question(_claim_number(claim.id), question) or _matches_question(claim.id, question)), None)
    if identified_claim:
        approved = f" Approved amount: ₹{float(identified_claim.approved_amount):,.2f}." if identified_claim.approved_amount is not None else ""
        return {"reply": f"{_claim_number(identified_claim.id)} is a {identified_claim.type} claim for ₹{float(identified_claim.claimed_amount):,.2f}. Its current status is {identified_claim.status}.{approved}"}

    identified_policy = next((policy for policy in policies if _matches_question(_policy_number(policy.id), question) or _matches_question(policy.id, question)), None)
    if identified_policy or any(term in query for term in ("coverage", "deductible", "premium", "policy")):
        selected = [identified_policy] if identified_policy else policies
        if not selected:
            return {"reply": "You do not currently have a policy on file."}
        lines = ["Your policy information:"]
        for policy in selected:
            lines.append(f"• {_policy_number(policy.id)} — {policy.name} ({policy.status}); coverage ₹{float(policy.coverage_amount):,.2f}, deductible ₹{float(policy.deductible or 0):,.2f}, premium ₹{float(policy.premium_amount):,.2f}. {policy.coverage_details or ''}".strip())
        return {"reply": "\n".join(lines)}

    if any(term in query for term in ("claim", "status", "filed")):
        if not claims:
            return {"reply": "You have not filed any claims yet."}
        return {"reply": "Your claims:\n" + "\n".join(f"• {_claim_number(claim.id)} — {claim.type} claim for ₹{float(claim.claimed_amount):,.2f}; status: {claim.status}." for claim in claims)}

    return {"reply": f"Hello {customer.name}. You have {len(policies)} policy or policies and {len(claims)} claim(s) on your account. Ask me about policy coverage, a claim status, or a specific policy or claim number."}


@router.post("/copilot/search", response_model=SearchResponse)
def search_knowledge_base(
    payload: SearchRequest,
    current_user: User = Depends(get_current_user),
):
    if payload.collection not in ALL_COLLECTIONS:
        return SearchResponse(
            results=[],
            faithfulness_note=f"Unknown collection. Valid: {ALL_COLLECTIONS}",
        )

    results = retrieve(payload.collection, payload.query)
    return SearchResponse(results=results)


@router.post("/copilot/ask")
def ask_copilot(
    payload: AskRequest,
    current_user: User = Depends(get_current_user),
):
    safe_question = apply_input_guardrail(payload.question)

    if payload.collection in ALL_COLLECTIONS:
        retrieved = retrieve(payload.collection, safe_question)
    else:
        retrieved = []

    context_text = "\n\n".join(r["text"] for r in retrieved)

    # Fast-path: if we have no Ollama or the collection had no docs,
    # return the raw retrieved text immediately so the user gets something.
    if not context_text:
        def no_context_stream():
            yield (
                "I couldn't find specific policy information for your question in the "
                "knowledge base. Please contact your insurance agent directly for "
                "accurate policy details regarding: " + safe_question
            )
        return StreamingResponse(no_context_stream(), media_type="text/plain")

    def stream():
        full_answer = ""

        try:
            response = get_client().chat.completions.create(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context_text}\n\nQuestion: {safe_question}",
                    },
                ],
                stream=True,
                max_tokens=MAX_TOKENS,
            )

            for chunk in response:
                delta = chunk.choices[0].delta.content or ""
                full_answer += delta
                yield delta

        except APIConnectionError:
            # Ollama is not running — fall back to showing the raw retrieved context
            fallback = (
                "[Copilot AI is currently offline. Here is the relevant policy information "
                "retrieved from the knowledge base:]\n\n" + context_text
            )
            full_answer = fallback
            yield fallback
            return
        except Exception as exc:
            yield f"\n\n[Error generating answer: {exc}]"
            return

        faithfulness = check_faithfulness(
            full_answer,
            [r["text"] for r in retrieved],
        )

        if not faithfulness["faithful"]:
            print(f"[copilot] low faithfulness answer flagged: {faithfulness}")

    return StreamingResponse(stream(), media_type="text/plain")
