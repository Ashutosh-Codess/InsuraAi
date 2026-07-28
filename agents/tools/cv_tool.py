"""
Lets the Damage Analyst agent run damage assessment on an uploaded
vehicle photo. Wraps cv_service.assess_damage and applies the confidence
guardrail before handing the result to the agent.
"""
from crewai.tools import tool

from app.services.cv_service import assess_damage
from guardrails.execution_guard import check_cv_confidence


@tool("vehicle_damage_inspection")
def vehicle_damage_inspection(image_path: str) -> str:
    """Runs computer vision damage assessment on a vehicle photo and
    returns the damage score, or a note that it needs manual review if
    the confidence is too low to trust."""
    result = assess_damage(image_path)
    confidence_check = check_cv_confidence(result)

    if not confidence_check["accepted"]:
        return f"Damage assessment inconclusive: {confidence_check['reason']}. Route to manual review."

    return f"Damage score: {result['damage_score']} (method: {result['method']})"
