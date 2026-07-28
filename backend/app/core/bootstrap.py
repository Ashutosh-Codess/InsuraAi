from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.claim import Claim
from app.models.customer import Customer
from app.models.policy import Policy
from app.models.user import User
from app.services.risk_service import calculate_risk_score


def _get_user(db, email: str):
    return db.query(User).filter(User.email == email).first()


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        customer_user = _get_user(db, "customer@insuramind.local")
        if customer_user is None:
            customer_user = User(email="customer@insuramind.local", hashed_password=hash_password("password123"), role="customer")
            db.add(customer_user)
            db.flush()

        if _get_user(db, "agent@insuramind.local") is None:
            db.add(User(email="agent@insuramind.local", hashed_password=hash_password("password123"), role="agent"))

        if _get_user(db, "admin@insuramind.local") is None:
            db.add(User(email="admin@insuramind.local", hashed_password=hash_password("password123"), role="admin"))

        customer = db.query(Customer).filter(Customer.user_id == customer_user.id).first()
        if customer is None:
            customer = Customer(
                user_id=customer_user.id,
                name="Demo Customer",
                age=34,
                gender="female",
                location="Mumbai",
                occupation="Analyst",
                income=750000,
                employment="salaried",
                marital_status="single",
                dependents=0,
            )
            customer.risk_score, customer.risk_category = calculate_risk_score(customer)
            db.add(customer)
            db.flush()

        policy = db.query(Policy).filter(Policy.customer_id == customer.id).first()
        if policy is None:
            policy = Policy(
                customer_id=customer.id,
                name="Demo Health Plan",
                type="health",
                provider="InsuraMind Demo Insurance",
                coverage_details="Covers inpatient and outpatient care for the demo customer.",
                coverage_amount=500000,
                premium_amount=12500,
                deductible=5000,
                duration_months=12,
                eligibility={"age_max": 60},
                exclusions={"cosmetic": True},
                terms_and_conditions="Demo policy terms.",
                renewal_conditions="Auto-renew unless cancelled.",
            )
            db.add(policy)
            db.flush()

        claim = db.query(Claim).filter(Claim.policy_id == policy.id).first()
        if claim is None:
            claim = Claim(
                customer_id=customer.id,
                policy_id=policy.id,
                type=policy.type,
                incident_description="Demo claim created so the customer and agent views have sample data.",
                claimed_amount=32000,
                status="submitted",
                processing_history=[{"event": "demo claim created", "timestamp": "2026-07-26T00:00:00+00:00"}],
                fraud_score=0.12,
                fraud_label="Unreviewed",
            )
            db.add(claim)

        db.commit()
    finally:
        db.close()