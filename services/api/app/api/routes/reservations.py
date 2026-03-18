from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.reservation_repository import ReservationRepository
from app.schemas import ReservationCreate, ReservationRead
from app.services.queue_service import get_queue_service
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/api/reservations", tags=["reservations"])


@router.get("", response_model=list[ReservationRead])
def list_reservations(db: Session = Depends(get_db)) -> list[ReservationRead]:
    return ReservationRepository(db).list_all()


@router.post("", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db)) -> ReservationRead:
    queue_service = get_queue_service()
    service = ReservationService(db, queue_service)
    return service.create_reservation(payload)
