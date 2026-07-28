import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from guardrails.execution_guard import check_cv_confidence, enforce_read_only


def test_low_confidence_damage_score_is_rejected():
    result = check_cv_confidence({"damage_score": 0.1})
    assert result["accepted"] is False


def test_high_confidence_damage_score_is_accepted():
    result = check_cv_confidence({"damage_score": 0.9})
    assert result["accepted"] is True


def test_select_query_is_allowed():
    enforce_read_only("SELECT * FROM claims WHERE id = 1")  # should not raise


def test_write_query_is_blocked():
    with pytest.raises(PermissionError):
        enforce_read_only("DELETE FROM claims WHERE id = 1")


def test_drop_table_is_blocked():
    with pytest.raises(PermissionError):
        enforce_read_only("DROP TABLE claims")
