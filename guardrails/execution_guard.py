"""
Sits between an agent and the tools it's allowed to call. Two jobs:
reject low-confidence CV results instead of letting an agent act on them,
and make sure any "database tool" an agent uses can only run SELECT.
"""
import re

MIN_DAMAGE_CONFIDENCE = 0.4  # below this, damage score isn't trustworthy enough to act on

WRITE_KEYWORDS = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE)\b", re.IGNORECASE)


def check_cv_confidence(result: dict) -> dict:
    score = result.get("damage_score")
    if score is None or score < MIN_DAMAGE_CONFIDENCE:
        return {"accepted": False, "reason": "damage score below confidence threshold, needs manual review"}
    return {"accepted": True, "reason": None}


def enforce_read_only(sql_query: str) -> None:
    """Raises if the query isn't a read-only SELECT. Agent DB tools should
    call this before running anything."""
    stripped = sql_query.strip().lower()
    if not stripped.startswith("select"):
        raise PermissionError("Agent database tool is restricted to SELECT queries only")
    if WRITE_KEYWORDS.search(sql_query):
        raise PermissionError("Query contains a write operation, which agents aren't allowed to run")
