from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer, Vehicle


def seed_demo_data(db: Session) -> None:
    has_customers = db.scalar(select(Customer.id).limit(1))
    has_vehicles = db.scalar(select(Vehicle.id).limit(1))

    if not has_customers:
        db.add_all(
            [
                Customer(full_name="Ana Martins", email="ana.martins@example.com", phone="(11) 99999-0101"),
                Customer(full_name="Carlos Souza", email="carlos.souza@example.com", phone="(21) 98888-0202"),
            ]
        )

    if not has_vehicles:
        db.add_all(
            [
                Vehicle(brand="Toyota", model="Corolla", year=2023, license_plate="BRA2E19", daily_rate=220.0),
                Vehicle(brand="Jeep", model="Renegade", year=2024, license_plate="RIO4F21", daily_rate=295.0),
                Vehicle(brand="Chevrolet", model="Onix", year=2022, license_plate="SPC1D77", daily_rate=165.0),
            ]
        )

    db.commit()
