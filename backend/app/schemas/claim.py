import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ClaimCreate(BaseModel):
    policy_id: uuid.UUID
    type: str
    incident_date: date | None = None
    incident_description: str | None = None
    claimed_amount: float


class ClaimResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    policy_id: uuid.UUID
    type: str
    claim_date: date
    incident_date: date | None
    incident_description: str | None
    claimed_amount: float
    approved_amount: float | None
    status: str
    final_decision: str | None
    processing_history: list
    fraud_score: float | None
    fraud_label: str | None
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClaimDecisionRequest(BaseModel):
    decision: str  # "approved" or "rejected"
    approved_amount: float | None = None
    notes: str | None = None
