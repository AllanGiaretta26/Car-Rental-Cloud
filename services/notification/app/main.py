import logging
from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.worker import NotificationStore, NotificationWorker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

settings = get_settings()
store = NotificationStore(maxlen=settings.max_notifications_in_memory)
worker = NotificationWorker(settings, store)


@asynccontextmanager
async def lifespan(_: FastAPI) -> Generator[None, None, None]:
    worker.start()
    yield
    worker.stop()


app = FastAPI(title="Notification Service", version="1.0.0", lifespan=lifespan)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Notification service online."}


@app.get("/health")
def health() -> dict[str, int | str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "processed_count": worker.processed_count,
    }


@app.get("/notifications")
def list_notifications() -> list[dict]:
    return store.list_all()
