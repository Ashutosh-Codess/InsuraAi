import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from guardrails.output_guard import check_faithfulness, requires_human_review


def test_faithful_answer_passes():
    answer = "the policy covers fire and theft damage"
    context = ["this policy covers fire and theft damage up to the sum insured"]
    result = check_faithfulness(answer, context)
    assert result["faithful"] is True


def test_unfaithful_answer_fails():
    answer = "the policy covers alien abduction and time travel insurance"
    context = ["this policy covers fire and theft damage"]
    result = check_faithfulness(answer, context)
    assert result["faithful"] is False


def test_no_context_is_not_faithful():
    result = check_faithfulness("some answer", [])
    assert result["faithful"] is False


def test_high_payout_requires_review():
    result = requires_human_review(500000, None)
    assert result["required"] is True


def test_high_fraud_score_requires_review():
    result = requires_human_review(1000, 0.85)
    assert result["required"] is True


def test_normal_claim_does_not_require_review():
    result = requires_human_review(5000, 0.1)
    assert result["required"] is False
