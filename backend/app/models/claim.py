import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Column, Date, DateTime, ForeignKey, JSON, Numeric, String, Text, Uuid
from sqlalchemy.orm import relationship

from app.core.database import Base


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(Uuid(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    policy_id = Column(Uuid(as_uuid=True), ForeignKey("policies.id"), nullable=False)

    # fields per "Insurance Claim Records" in the spec
    type = Column(String(50), nullable=False)  # matches policy.type - motor, health, etc
    claim_date = Column(Date, default=date.today)
    incident_date = Column(Date, nullable=True)
    incident_description = Column(Text)
    claimed_amount = Column(Numeric(14, 2), nullable=False)
    approved_amount = Column(Numeric(14, 2), nullable=True)
    status = Column(String(30), default="submitted")  # submitted / under_review / approved / rejected
    final_decision = Column(Text, nullable=True)

    # processing_history is an append-only log of status changes -
    # the doc calls this out explicitly under Insurance Claim Records
    processing_history = Column(JSON, default=list)

    # "Fraud Detection Data" doesn't have its own model file in the doc's
    # directory tree, so those fields live here instead of a separate table
    fraud_score = Column(Numeric(5, 2), nullable=True)
    fraud_label = Column(String(20), nullable=True)  # Fraudulent / Genuine / Unreviewed
    investigation_notes = Column(Text, nullable=True)

    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    customer = relationship("Customer", back_populates="claims")
    policy = relationship("Policy", back_populates="claims")
