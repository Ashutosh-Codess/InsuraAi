"""
Same caveat as test_health.py - needs the full stack + a real Postgres
database to actually run. Uses a throwaway email per test run so it's
safe to run against a real dev database repeatedly.
"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from fastapi.testclient import TestClient
from main import app

def _unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


def test_register_then_login():
    email = _unique_email()

    with TestClient(app) as client:
        register_response = client.post("/api/v1/auth/register", json={"email": email, "password": "testpass123"})
        assert register_response.status_code == 200
        assert register_response.json()["role"] == "customer"

        login_response = client.post("/api/v1/auth/login", data={"username": email, "password": "testpass123"})
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()


def test_login_with_wrong_password_fails():
    email = _unique_email()
    with TestClient(app) as client:
        client.post("/api/v1/auth/register", json={"email": email, "password": "testpass123"})

        response = client.post("/api/v1/auth/login", data={"username": email, "password": "wrongpassword"})
        assert response.status_code == 401


def test_json_login_with_demo_customer_and_agent():
    """The two browser portals authenticate through the JSON-compatible endpoint."""
    with TestClient(app) as client:
        for email, expected_role in (
            ("customer@insuramind.local", "customer"),
            ("agent@insuramind.local", "agent"),
        ):
            response = client.post(
                "/api/v1/auth/login/json",
                json={"email": email, "password": "password123"},
            )
            assert response.status_code == 200
            token = response.json()["access_token"]
            me_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert me_response.status_code == 200
            assert me_response.json()["role"] == expected_role


def test_duplicate_registration_fails():
    email = _unique_email()
    with TestClient(app) as client:
        client.post("/api/v1/auth/register", json={"email": email, "password": "testpass123"})

        second_attempt = client.post("/api/v1/auth/register", json={"email": email, "password": "testpass123"})
        assert second_attempt.status_code == 400
