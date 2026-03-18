import logging
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Customer, Payment, PaymentStatus, Reservation, ReservationStatus, Vehicle, VehicleStatus
from app.repositories.reservation_repository import ReservationRepository
from app.schemas import DashboardSummary, PaymentResultPayload, ReservationCreate
from app.services.notification_client import fetch_recent_notifications
from app.services.queue_service import EventQueueService

logger = logging.getLogger(__name__)


class ReservationService:
    def __init__(self, db: Session, queue_service: EventQueueService) -> None:
        self.db = db
        self.queue_service = queue_service
        self.reservation_repository = ReservationRepository(db)

    def create_reservation(self, payload: ReservationCreate) -> Reservation:
        # A API faz a validacao principal antes de enviar qualquer evento para a fila.
        customer = self.db.get(Customer, payload.customer_id)
        vehicle = self.db.get(Vehicle, payload.vehicle_id)

        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente nao encontrado.")
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veiculo nao encontrado.")
        if vehicle.status != VehicleStatus.AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="O veiculo selecionado nao esta disponivel para reserva.",
            )
        if payload.end_date <= payload.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A data final deve ser maior que a data inicial.",
            )

        rental_days = (payload.end_date - payload.start_date).days
        total_amount = rental_days * vehicle.daily_rate

        reservation = Reservation(
            customer_id=customer.id,
            vehicle_id=vehicle.id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            total_amount=total_amount,
            status=ReservationStatus.PENDING_PAYMENT,
            simulate_payment_failure=payload.simulate_payment_failure,
        )
        payment = Payment(amount=total_amount, status=PaymentStatus.PENDING)

        reservation.payment = payment
        vehicle.status = VehicleStatus.RESERVED

        # Primeiro persiste a reserva; depois publica o evento assincrono.
        self.db.add(reservation)
        self.db.add(payment)
        self.db.add(vehicle)
        self.db.commit()
        self.db.refresh(reservation)
        reservation = self.reservation_repository.get_by_id(reservation.id)
        if not reservation:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao criar reserva.")

        event_payload = {
            "reservation_id": reservation.id,
            "amount": reservation.total_amount,
            "customer_name": reservation.customer.full_name,
            "customer_email": reservation.customer.email,
            "vehicle_label": f"{reservation.vehicle.brand} {reservation.vehicle.model}",
            "simulate_payment_failure": reservation.simulate_payment_failure,
        }

        try:
            self.queue_service.enqueue_payment(event_payload)
        except Exception as exc:
            # Se a fila falhar, a reserva nao fica presa como pendente.
            logger.exception("Falha ao publicar evento de pagamento: %s", exc)
            payment_record = reservation.payment
            if payment_record:
                payment_record.status = PaymentStatus.FAILED
                payment_record.message = "Falha ao enviar o pagamento para a fila."
                payment_record.processed_at = datetime.utcnow()
                self.db.add(payment_record)

            reservation.status = ReservationStatus.PAYMENT_FAILED
            reservation.vehicle.status = VehicleStatus.AVAILABLE
            self.db.add(reservation)
            self.db.add(reservation.vehicle)
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Nao foi possivel enviar a reserva para processamento de pagamento.",
            ) from exc

        logger.info("Reserva %s criada e enviada para processamento de pagamento.", reservation.id)
        return reservation

    def process_payment_result(self, payload: PaymentResultPayload) -> Reservation:
        # Este metodo e chamado apenas pelo webhook interno do servico de pagamento.
        reservation = self.reservation_repository.get_by_id(payload.reservation_id)
        if not reservation or not reservation.payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva ou pagamento nao encontrado.")

        if reservation.payment.status == payload.payment_status:
            return reservation

        reservation.payment.status = payload.payment_status
        reservation.payment.provider_reference = payload.provider_reference
        reservation.payment.message = payload.message
        reservation.payment.processed_at = payload.processed_at

        if payload.payment_status == PaymentStatus.PAID:
            reservation.status = ReservationStatus.CONFIRMED
        else:
            reservation.status = ReservationStatus.PAYMENT_FAILED
            reservation.vehicle.status = VehicleStatus.AVAILABLE
            self.db.add(reservation.vehicle)

        self.db.add(reservation.payment)
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        reservation = self.reservation_repository.get_by_id(reservation.id)
        if not reservation:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao atualizar reserva.")

        # Depois da confirmacao do pagamento, a notificacao segue por outra fila.
        notification_payload = {
            "reservation_id": reservation.id,
            "customer_email": reservation.customer.email,
            "customer_name": reservation.customer.full_name,
            "message": (
                f"Pagamento aprovado para a reserva #{reservation.id}. Veiculo liberado para retirada."
                if payload.payment_status == PaymentStatus.PAID
                else f"Pagamento recusado para a reserva #{reservation.id}. O veiculo voltou a ficar disponivel."
            ),
            "sent_at": payload.processed_at.isoformat(),
        }
        self.queue_service.enqueue_notification(notification_payload)

        logger.info("Resultado do pagamento aplicado a reserva %s.", reservation.id)
        return reservation

    def build_dashboard_summary(self) -> DashboardSummary:
        # Resumo usado pelo painel web.
        customers_count = self.db.scalar(select(func.count(Customer.id))) or 0
        vehicles_count = self.db.scalar(select(func.count(Vehicle.id))) or 0
        available_vehicles = self.db.scalar(
            select(func.count(Vehicle.id)).where(Vehicle.status == VehicleStatus.AVAILABLE)
        ) or 0
        active_reservations = self.db.scalar(
            select(func.count(Reservation.id)).where(Reservation.status == ReservationStatus.CONFIRMED)
        ) or 0
        pending_payments = self.db.scalar(
            select(func.count(Payment.id)).where(Payment.status == PaymentStatus.PENDING)
        ) or 0
        recent_notifications = len(fetch_recent_notifications())

        return DashboardSummary(
            customers_count=customers_count,
            vehicles_count=vehicles_count,
            available_vehicles=available_vehicles,
            active_reservations=active_reservations,
            pending_payments=pending_payments,
            recent_notifications=recent_notifications,
        )
