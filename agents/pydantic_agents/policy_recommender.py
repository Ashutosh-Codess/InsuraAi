"""
Policy Recommender Agent (PydanticAI). Takes a customer profile and
returns a structured, validated recommendation.
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


class PolicyRecommendation(BaseModel):
    recommended_policy_type: str
    recommended_coverage_amount: float
    estimated_premium: float
    reasoning: str


recommender_agent = Agent(
    model,
    result_type=PolicyRecommendation,
    system_prompt=(
        "You recommend an insurance policy type, coverage amount, and estimated "
        "premium based on a customer's profile (age, income, dependents, risk "
        "category, budget, and coverage preference). Base the premium on the "
        "risk category given to you - don't invent a different one."
    ),
)


def recommend_policy(customer_profile: str) -> PolicyRecommendation:
    result = recommender_agent.run_sync(customer_profile)
    return result.data