"""
Runs on what comes OUT of an agent/LLM. Checks the answer is actually
grounded in what was retrieved, and decides whether a claim needs a human
to look at it before anything gets finalized.
"""
import re

HIGH_PAYOUT_THRESHOLD = 100000  # claims above this always go to a human
FRAUD_SCORE_THRESHOLD = 0.7


STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be", "been",
    "this", "that", "these", "those", "to", "of", "in", "on", "for", "with", "as",
    "it", "its", "at", "by", "from", "up", "down", "not", "no", "yes", "your", "you",
}


def _tokenize(text: str) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9]+", text.lower()))
    return tokens - STOPWORDS


def check_faithfulness(answer: str, retrieved_chunks: list[str], min_overlap: float = 0.5) -> dict:
    """Rough faithfulness check - how much of the answer's vocabulary
    actually shows up in what was retrieved. Not a substitute for a real
    faithfulness model, but catches an answer that's clearly not grounded
    in anything retrieved."""
    if not retrieved_chunks:
        return {"faithful": False, "reason": "no context was retrieved"}

    answer_tokens = _tokenize(answer)
    context_tokens = set()
    for chunk in retrieved_chunks:
        context_tokens.update(_tokenize(chunk))

    if not answer_tokens:
        return {"faithful": False, "reason": "empty answer"}

    overlap = len(answer_tokens & context_tokens) / len(answer_tokens)
    return {"faithful": overlap >= min_overlap, "overlap_ratio": round(overlap, 2)}


def requires_human_review(claimed_amount: float, fraud_score: float | None) -> dict:
    if claimed_amount >= HIGH_PAYOUT_THRESHOLD:
        return {"required": True, "reason": f"claim amount {claimed_amount} exceeds high-payout threshold"}
    if fraud_score is not None and fraud_score >= FRAUD_SCORE_THRESHOLD:
        return {"required": True, "reason": f"fraud score {fraud_score} exceeds threshold"}
    return {"required": False, "reason": None}
