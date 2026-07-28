"""
Generates synthetic customers, policies, and claims for local development
and testing, using Faker. Run manually - this never runs automatically on
app startup:

    python database/seeds/generate_seed_data.py --customers 50

Needs the backend's app package on the path since it reuses the real
SQLAlchemy models and risk_service, rather than duplicating that logic.
"""
import argparse
import os
import random
import sys
from datetime import date, timedelta

from faker import Faker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.core.database import SessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.claim import Claim  # noqa: E402
from app.models.customer import Customer  # noqa: E402
from app.models.policy import Policy  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.risk_service import calculate_risk_score  # noqa: E402

fake = Faker()

POLICY_TYPES = ["health", "motor", "life", "travel", "home"]
EMPLOYMENT_TYPES = ["salaried", "self-employed", "unemployed", "retired"]
CLAIM_STATUSES = ["submitted", "under_review", "approved", "rejected"]


def create_customer(db) -> Customer:
    email = fake.unique.email()
    user = User(email=email, hashed_password=hash_password("password123"), role="customer")
    db.add(user)
    db.flush()  # need user.id before creating the customer row

    customer = Customer(
        user_id=user.id,
        name=fake.name(),
        age=random.randint(18, 75),
        gender=random.choice(["male", "female", "other"]),
        location=fake.city(),
        occupation=fake.job(),
        income=round(random.uniform(200000, 2000000), 2),
        employment=random.choice(EMPLOYMENT_TYPES),
        marital_status=random.choice(["single", "married", "divorced"]),
        dependents=random.randint(0, 4),
    )
    customer.risk_score, customer.risk_category = calculate_risk_score(customer)
    db.add(customer)
    db.flush()
    return customer


def create_policy(db, customer: Customer) -> Policy:
    coverage = round(random.uniform(100000, 2000000), 2)
    policy = Policy(
        customer_id=customer.id,
        name=f"{fake.company()} {random.choice(POLICY_TYPES).title()} Plan",
        type=random.choice(POLICY_TYPES),
        provider=fake.company(),
        coverage_details=fake.sentence(),
        coverage_amount=coverage,
        premium_amount=round(coverage * random.uniform(0.01, 0.05), 2),
        deductible=round(coverage * 0.02, 2),
        duration_months=random.choice([6, 12, 24]),
        start_date=date.today() - timedelta(days=random.randint(0, 400)),
    )
    db.add(policy)
    db.flush()
    return policy


def create_claim(db, customer: Customer, policy: Policy) -> Claim:
    claimed = round(random.uniform(5000, policy.coverage_amount * 0.5), 2)
    status = random.choice(CLAIM_STATUSES)
    claim = Claim(
        customer_id=customer.id,
        policy_id=policy.id,
        type=policy.type,
        incident_date=date.today() - timedelta(days=random.randint(0, 60)),
        incident_description=fake.paragraph(),
        claimed_amount=claimed,
        approved_amount=round(claimed * 0.8, 2) if status == "approved" else None,
        status=status,
        processing_history=[{"event": "claim submitted", "timestamp": fake.iso8601()}],
        fraud_score=round(random.uniform(0, 1), 2) if random.random() < 0.2 else None,
    )
    db.add(claim)
    return claim


def run(num_customers: int):
    db = SessionLocal()
    try:
        for _ in range(num_customers):
            customer = create_customer(db)

            for _ in range(random.randint(1, 2)):
                policy = create_policy(db, customer)

                if random.random() < 0.6:
                    create_claim(db, customer, policy)

        db.commit()
        print(f"[seed] created {num_customers} synthetic customers with policies and claims")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--customers", type=int, default=50)
    args = parser.parse_args()
    run(args.customers)
