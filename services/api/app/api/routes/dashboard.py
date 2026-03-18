from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import DashboardSummary
from app.services.queue_service import get_queue_service
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    service = ReservationService(db, get_queue_service())
    return service.build_dashboard_summary()
