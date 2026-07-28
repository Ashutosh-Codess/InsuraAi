import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.customer import Customer
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.risk_service import calculate_risk_score

router = APIRouter()


@router.post("/customers/me", response_model=CustomerResponse)
def create_my_profile(payload: CustomerCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already exists")

    customer = Customer(user_id=current_user.id, **payload.model_dump())
    customer.risk_score, customer.risk_category = calculate_risk_score(customer)

    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/customers/me", response_model=CustomerResponse)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return customer


@router.put("/customers/me", response_model=CustomerResponse)
def update_my_profile(payload: CustomerUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    for field, value in payload.model_dump().items():
        setattr(customer, field, value)

    # profile changed - risk score needs recalculating
    customer.risk_score, customer.risk_category = calculate_risk_score(customer)

    db.commit()
    db.refresh(customer)
    return customer


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: uuid.UUID, _: User = Depends(require_role("agent", "admin")), db: Session = Depends(get_db)):
    # agent/admin lookup - used when reviewing a claim
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer
