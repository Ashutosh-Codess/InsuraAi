"""
KYC Verifier Agent (PydanticAI). Compares OCR output from an uploaded ID
document against what's on file for the customer and returns a
structured match/mismatch result per field.
"""

import os

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")

model = OpenAIModel(
    model_name=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    api_key="ollama",
)


class KYCVerificationResult(BaseModel):
    name_match: bool
    date_of_birth_match: bool
    id_number_match: bool
    overall_verified: bool
    notes: str


kyc_agent = Agent(
    model,
    result_type=KYCVerificationResult,
    system_prompt=(
        "You compare OCR-extracted identity document fields against a customer's "
        "record on file. Check name, date of birth, and ID number individually. "
        "overall_verified is only true if ALL fields match. If the OCR data was "
        "flagged as unreadable, mark everything as not matched and say so in notes."
    ),
)


def verify_kyc(ocr_result: str, customer_record: str) -> KYCVerificationResult:
    prompt = f"OCR extracted data: {ocr_result}\n\nCustomer record on file: {customer_record}"
    result = kyc_agent.run_sync(prompt)
    return result.data