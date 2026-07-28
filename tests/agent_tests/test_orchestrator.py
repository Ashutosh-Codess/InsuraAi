"""
Tests the orchestrator's dispatch logic and guardrail wiring, not actual
agent output quality (that's not something you can assert on
deterministically against a real LLM anyway). Mocks out the actual
CrewAI/PydanticAI calls so these can run without Ollama or a GPU.

Needs crewai + pydantic-ai installed to even import agents.orchestrator -
couldn't be executed in the build environment for that reason. Once
dependencies are installed:

    pytest tests/agent_tests/test_orchestrator.py
"""
import sys
import os
from unittest.mock import patch

repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, repo_root)
sys.path.insert(0, os.path.join(repo_root, "backend"))

import pytest

from guardrails.agent_guard import AgentLoopError


def test_unknown_workflow_raises():
    from agents.orchestrator import dispatch_claim_workflow

    with pytest.raises(ValueError):
        dispatch_claim_workflow("not_a_real_workflow", "some context")


@patch("agents.orchestrator.run_claim_adjudication")
def test_claim_adjudication_gets_pii_masked_context(mock_run):
    from agents.orchestrator import dispatch_claim_workflow

    mock_run.return_value = "mocked crew result"
    result = dispatch_claim_workflow("claim_adjudication", "customer aadhaar is 1234 5678 9012")

    assert result == "mocked crew result"
    called_with = mock_run.call_args[0][0]
    assert "1234 5678 9012" not in called_with  # guardrail actually ran before the crew was called


@patch("agents.orchestrator.run_claim_adjudication")
def test_iteration_limit_is_enforced(mock_run):
    from agents.orchestrator import dispatch_claim_workflow

    mock_run.return_value = "mocked"
    with pytest.raises(AgentLoopError):
        dispatch_claim_workflow("claim_adjudication", "context", iteration=10)
