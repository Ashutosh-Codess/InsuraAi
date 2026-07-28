"""
Requires the full backend dependency stack (FastAPI, SQLAlchemy, a running
Postgres) - couldn't be executed in the environment this was built in, but
is straightforward to run once you `pip install -r requirements.txt` and
have the db service up:

    pytest tests/integration/test_health.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unauthenticated_request_to_protected_route_is_rejected():
    response = client.get("/api/v1/customers/me")
    assert response.status_code == 401
