import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.customer import Customer
from app.models.policy import Policy
from app.models.user import User
from app.schemas.policy import PolicyCreate, PolicyResponse

router = APIRouter()


@router.get("/policies/mine", response_model=list[PolicyResponse])
def list_my_policies(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        return []
    return db.query(Policy).filter(Policy.customer_id == customer.id, Policy.status == "active").all()


@router.get("/policies", response_model=list[PolicyResponse])
def list_policies(type: str | None = None, db: Session = Depends(get_db)):
    # public catalog lookup - policy type filter is optional
    query = db.query(Policy).filter(Policy.status == "active")
    if type:
        query = query.filter(Policy.type == type)
    return query.all()


@router.get("/policies/{policy_id}", response_model=PolicyResponse)
def get_policy(policy_id: uuid.UUID, db: Session = Depends(get_db)):
    policy = db.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    return policy


@router.post("/policies", response_model=PolicyResponse)
def create_policy(payload: PolicyCreate, _: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    customer = db.get(Customer, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    policy = Policy(**payload.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.get("/customers/{customer_id}/policies", response_model=list[PolicyResponse])
def list_customer_policies(customer_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(Policy).filter(Policy.customer_id == customer_id).all()
