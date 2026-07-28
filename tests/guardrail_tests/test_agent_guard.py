import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from guardrails.agent_guard import AgentLoopError, MAX_ITERATIONS, check_iteration


def test_stays_under_limit():
    count = 0
    for _ in range(MAX_ITERATIONS - 1):
        count = check_iteration(count)
    assert count == MAX_ITERATIONS - 1


def test_raises_once_limit_hit():
    count = 0
    with pytest.raises(AgentLoopError):
        for _ in range(MAX_ITERATIONS + 1):
            count = check_iteration(count)
