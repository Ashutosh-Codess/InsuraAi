import uuid

from pydantic import BaseModel, ConfigDict


class CustomerCreate(BaseModel):
    name: str
    age: int | None = None
    gender: str | None = None
    location: str | None = None
    occupation: str | None = None
    income: float | None = None
    employment: str | None = None
    marital_status: str | None = None
    dependents: int = 0


class CustomerUpdate(CustomerCreate):
    pass


class CustomerResponse(BaseModel):
    id: uuid.UUID
    name: str
    age: int | None
    gender: str | None
    location: str | None
    occupation: str | None
    income: float | None
    employment: str | None
    marital_status: str | None
    dependents: int
    risk_score: float | None
    risk_category: str | None

    model_config = ConfigDict(from_attributes=True)
