import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import customers, dashboard, health, internal, notifications, reservations, vehicles
from app.core.config import get_settings
from app.db import SessionLocal, init_db
from app.services.bootstrap_service import seed_demo_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    init_db()
    if settings.seed_demo_data:
        with SessionLocal() as db:
            seed_demo_data(db)
    yield


settings = get_settings()
app = FastAPI(title="Car Rental Cloud API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(customers.router)
app.include_router(vehicles.router)
app.include_router(reservations.router)
app.include_router(dashboard.router)
app.include_router(notifications.router)
app.include_router(internal.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Car Rental Cloud API online."}
