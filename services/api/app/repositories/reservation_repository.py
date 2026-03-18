from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Payment, Reservation


class ReservationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Reservation]:
        statement = (
            select(Reservation)
            .options(
                joinedload(Reservation.customer),
                joinedload(Reservation.vehicle),
                joinedload(Reservation.payment),
            )
            .order_by(Reservation.created_at.desc())
        )
        return list(self.db.scalars(statement).unique().all())

    def get_by_id(self, reservation_id: int) -> Reservation | None:
        statement = (
            select(Reservation)
            .options(
                joinedload(Reservation.customer),
                joinedload(Reservation.vehicle),
                joinedload(Reservation.payment),
            )
            .where(Reservation.id == reservation_id)
        )
        return self.db.scalar(statement)

    def get_payment_by_reservation_id(self, reservation_id: int) -> Payment | None:
        statement = select(Payment).where(Payment.reservation_id == reservation_id)
        return self.db.scalar(statement)
