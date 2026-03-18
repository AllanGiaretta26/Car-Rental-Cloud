from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Vehicle, VehicleStatus
from app.schemas import VehicleCreate


class VehicleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Vehicle]:
        return list(self.db.scalars(select(Vehicle).order_by(Vehicle.created_at.desc())).all())

    def get_by_id(self, vehicle_id: int) -> Vehicle | None:
        return self.db.get(Vehicle, vehicle_id)

    def get_by_license_plate(self, license_plate: str) -> Vehicle | None:
        statement = select(Vehicle).where(Vehicle.license_plate == license_plate)
        return self.db.scalar(statement)

    def create(self, payload: VehicleCreate) -> Vehicle:
        vehicle = Vehicle(**payload.model_dump())
        self.db.add(vehicle)
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle

    def update_status(self, vehicle: Vehicle, status: VehicleStatus) -> Vehicle:
        vehicle.status = status
        self.db.add(vehicle)
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle
