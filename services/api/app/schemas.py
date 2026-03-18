from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import PaymentStatus, ReservationStatus, VehicleStatus


class APIMessage(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str


class CustomerBase(BaseModel):
    full_name: str = Field(min_length=3, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehicleBase(BaseModel):
    brand: str = Field(min_length=2, max_length=80)
    model: str = Field(min_length=1, max_length=80)
    year: int = Field(ge=2000, le=2100)
    license_plate: str = Field(min_length=5, max_length=20)
    daily_rate: float = Field(gt=0)


class VehicleCreate(VehicleBase):
    pass


class VehicleStatusUpdate(BaseModel):
    status: VehicleStatus


class VehicleRead(VehicleBase):
    id: int
    status: VehicleStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentRead(BaseModel):
    id: int
    reservation_id: int
    amount: float
    status: PaymentStatus
    provider_reference: str | None = None
    message: str | None = None
    processed_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReservationCreate(BaseModel):
    customer_id: int
    vehicle_id: int
    start_date: date
    end_date: date
    simulate_payment_failure: bool = False


class ReservationRead(BaseModel):
    id: int
    customer: CustomerRead
    vehicle: VehicleRead
    payment: PaymentRead | None = None
    start_date: date
    end_date: date
    total_amount: float
    status: ReservationStatus
    simulate_payment_failure: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentResultPayload(BaseModel):
    reservation_id: int
    payment_status: PaymentStatus
    provider_reference: str
    message: str
    processed_at: datetime


class NotificationPreview(BaseModel):
    reservation_id: int
    customer_email: str
    customer_name: str
    message: str
    sent_at: datetime


class DashboardSummary(BaseModel):
    customers_count: int
    vehicles_count: int
    available_vehicles: int
    active_reservations: int
    pending_payments: int
    recent_notifications: int
