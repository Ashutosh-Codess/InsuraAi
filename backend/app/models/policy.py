import uuid
from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, JSON, Numeric, String, Text, Uuid
from sqlalchemy.orm import relationship

from app.core.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(Uuid(as_uuid=True), ForeignKey("customers.id"), nullable=False)

    # fields per "Insurance Policy Data" in the spec
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # health / motor / life / travel etc
    provider = Column(String(255))
    coverage_details = Column(Text)
    coverage_amount = Column(Numeric(14, 2), nullable=False)
    premium_amount = Column(Numeric(14, 2), nullable=False)
    deductible = Column(Numeric(14, 2), default=0)
    duration_months = Column(Integer, nullable=False)
    eligibility = Column(JSON, default=dict)
    exclusions = Column(JSON, default=dict)
    terms_and_conditions = Column(Text)
    renewal_conditions = Column(Text)

    start_date = Column(Date, default=date.today)
    status = Column(String(20), default="active")

    customer = relationship("Customer", back_populates="policies")
    claims = relationship("Claim", back_populates="policy")
