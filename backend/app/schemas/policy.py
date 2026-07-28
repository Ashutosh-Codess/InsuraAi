import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class PolicyCreate(BaseModel):
    customer_id: uuid.UUID
    name: str
    type: str
    provider: str | None = None
    coverage_details: str | None = None
    coverage_amount: float
    premium_amount: float
    deductible: float = 0
    duration_months: int
    eligibility: dict = {}
    exclusions: dict = {}
    terms_and_conditions: str | None = None
    renewal_conditions: str | None = None


class PolicyResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    name: str
    type: str
    provider: str | None
    coverage_amount: float
    premium_amount: float
    deductible: float
    duration_months: int
    start_date: date
    status: str

    model_config = ConfigDict(from_attributes=True)
