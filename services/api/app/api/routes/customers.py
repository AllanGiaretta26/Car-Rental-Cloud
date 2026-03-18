from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.customer_repository import CustomerRepository
from app.schemas import CustomerCreate, CustomerRead

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=list[CustomerRead])
def list_customers(db: Session = Depends(get_db)) -> list[CustomerRead]:
    return CustomerRepository(db).list_all()


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)) -> CustomerRead:
    repository = CustomerRepository(db)
    if repository.get_by_email(payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ja existe um cliente com este e-mail.")
    return repository.create(payload)
