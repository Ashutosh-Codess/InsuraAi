import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.services.risk_service import calculate_risk_score


class FakeCustomer:
    """Plain stand-in so this test doesn't need a database or SQLAlchemy
    session - calculate_risk_score only reads attributes off the object."""

    def __init__(self, age=None, income=None, dependents=0, employment=None):
        self.age = age
        self.income = income
        self.dependents = dependents
        self.employment = employment


def test_low_risk_customer():
    customer = FakeCustomer(age=30, income=1000000, dependents=0, employment="salaried")
    _score, category = calculate_risk_score(customer)
    assert category == "Low"


def test_high_risk_customer():
    customer = FakeCustomer(age=65, income=150000, dependents=4, employment="unemployed")
    score, category = calculate_risk_score(customer)
    assert category == "High"
    assert score == 70.0


def test_score_never_exceeds_100():
    customer = FakeCustomer(age=90, income=0, dependents=10, employment="unemployed")
    score, _ = calculate_risk_score(customer)
    assert score <= 100.0
