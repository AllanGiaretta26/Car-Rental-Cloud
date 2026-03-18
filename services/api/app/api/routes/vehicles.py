from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas import VehicleCreate, VehicleRead, VehicleStatusUpdate

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleRead])
def list_vehicles(db: Session = Depends(get_db)) -> list[VehicleRead]:
    return VehicleRepository(db).list_all()


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)) -> VehicleRead:
    repository = VehicleRepository(db)
    if repository.get_by_license_plate(payload.license_plate):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ja existe um veiculo com esta placa.")
    return repository.create(payload)


@router.patch("/{vehicle_id}/status", response_model=VehicleRead)
def update_vehicle_status(
    vehicle_id: int,
    payload: VehicleStatusUpdate,
    db: Session = Depends(get_db),
) -> VehicleRead:
    repository = VehicleRepository(db)
    vehicle = repository.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veiculo nao encontrado.")
    return repository.update_status(vehicle, payload.status)
