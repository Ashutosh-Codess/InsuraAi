"""
Risk scoring logic used when a customer profile is created or updated.

This is a plain rule-based scorer, not a trained model - the doc lists
Pandas/NumPy for "feature extraction" but doesn't specify a trained risk
model anywhere, so this stays deterministic and explainable rather than
guessing at an ML approach that isn't actually described.
"""
from typing import TYPE_CHECKING

# Only imported for the type hint below, never at runtime - this function
# only touches plain attributes (age, income, dependents, employment), so
# it doesn't actually need SQLAlchemy loaded to run or to be unit tested.
if TYPE_CHECKING:
    from app.models.customer import Customer


def calculate_risk_score(customer: "Customer") -> tuple[float, str]:
    score = 0.0

    if customer.age is not None:
        if customer.age >= 60:
            score += 25
        elif customer.age >= 40:
            score += 10

    if customer.income is not None and customer.income < 300000:
        score += 15

    if customer.dependents:
        score += min(customer.dependents * 5, 20)

    if customer.employment and customer.employment.lower() in ("unemployed", "self-employed"):
        score += 10

    score = min(score, 100.0)

    if score >= 60:
        category = "High"
    elif score >= 30:
        category = "Medium"
    else:
        category = "Low"

    return score, category
