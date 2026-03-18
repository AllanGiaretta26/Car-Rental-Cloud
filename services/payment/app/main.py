import logging
from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.worker import PaymentWorker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

settings = get_settings()
worker = PaymentWorker(settings)


@asynccontextmanager
async def lifespan(_: FastAPI) -> Generator[None, None, None]:
    worker.start()
    yield
    worker.stop()


app = FastAPI(title="Payment Processing Service", version="1.0.0", lifespan=lifespan)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Payment processing service online."}


@app.get("/health")
def health() -> dict[str, int | str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "processed_count": worker.processed_count,
        "failed_callbacks": worker.failed_callbacks,
    }
