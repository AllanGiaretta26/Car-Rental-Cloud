from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, Enum as SqlEnum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class VehicleStatus(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


class ReservationStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    PAYMENT_FAILED = "payment_failed"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"


class Customer(Base):
    __tablename__ = "customers"

    # Cliente pode ter varias reservas ao longo do tempo.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    reservations: Mapped[list["Reservation"]] = relationship(back_populates="customer")


class Vehicle(Base):
    __tablename__ = "vehicles"

    # O status do veiculo ajuda a bloquear reservas concorrentes.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    brand: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    license_plate: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    daily_rate: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[VehicleStatus] = mapped_column(
        SqlEnum(VehicleStatus),
        default=VehicleStatus.AVAILABLE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    reservations: Mapped[list["Reservation"]] = relationship(back_populates="vehicle")


class Reservation(Base):
    __tablename__ = "reservations"

    # Reserva concentra o periodo, o valor total e o estado do aluguel.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[ReservationStatus] = mapped_column(
        SqlEnum(ReservationStatus),
        default=ReservationStatus.PENDING_PAYMENT,
        nullable=False,
    )
    simulate_payment_failure: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    customer: Mapped[Customer] = relationship(back_populates="reservations")
    vehicle: Mapped[Vehicle] = relationship(back_populates="reservations")
    payment: Mapped["Payment | None"] = relationship(back_populates="reservation", uselist=False)


class Payment(Base):
    __tablename__ = "payments"

    # Cada reserva possui um unico pagamento associado.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id"), nullable=False, unique=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        SqlEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
    )
    provider_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    message: Mapped[str | None] = mapped_column(String(255), nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    reservation: Mapped[Reservation] = relationship(back_populates="payment")
