from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer
from app.schemas import CustomerCreate


class CustomerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Customer]:
        return list(self.db.scalars(select(Customer).order_by(Customer.created_at.desc())).all())

    def get_by_id(self, customer_id: int) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def get_by_email(self, email: str) -> Customer | None:
        statement = select(Customer).where(Customer.email == email)
        return self.db.scalar(statement)

    def create(self, payload: CustomerCreate) -> Customer:
        customer = Customer(**payload.model_dump())
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer
