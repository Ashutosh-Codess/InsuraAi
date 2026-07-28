import uuid

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Uuid
from sqlalchemy.orm import relationship

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)

    # fields per "Customer Profile Data" in the spec
    name = Column(String(255), nullable=False)
    age = Column(Integer)
    gender = Column(String(20))
    location = Column(String(255))
    occupation = Column(String(255))
    income = Column(Numeric(14, 2))
    employment = Column(String(100))
    marital_status = Column(String(30))
    dependents = Column(Integer, default=0)

    # risk_service.py writes to these two - customer never sets them directly
    risk_score = Column(Numeric(5, 2), nullable=True)
    risk_category = Column(String(20), nullable=True)  # Low / Medium / High

    policies = relationship("Policy", back_populates="customer")
    claims = relationship("Claim", back_populates="customer")
