from fastapi import APIRouter

from app.schemas import NotificationPreview
from app.services.notification_client import fetch_recent_notifications

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/preview", response_model=list[NotificationPreview])
def get_notification_preview() -> list[NotificationPreview]:
    return fetch_recent_notifications()
