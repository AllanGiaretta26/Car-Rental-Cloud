from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import get_db
from app.schemas import PaymentResultPayload, ReservationRead
from app.services.queue_service import get_queue_service
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/internal/payments", tags=["internal"])


def _validate_internal_token(x_internal_token: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if x_internal_token != settings.internal_service_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token interno invalido.")


@router.post("/process-result", response_model=ReservationRead, dependencies=[Depends(_validate_internal_token)])
def process_payment_result(payload: PaymentResultPayload, db: Session = Depends(get_db)) -> ReservationRead:
    service = ReservationService(db, get_queue_service())
    return service.process_payment_result(payload)
