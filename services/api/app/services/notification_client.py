import logging

import httpx

from app.core.config import get_settings
from app.schemas import NotificationPreview

logger = logging.getLogger(__name__)


def fetch_recent_notifications() -> list[NotificationPreview]:
    settings = get_settings()
    try:
        response = httpx.get(f"{settings.notification_service_url}/notifications", timeout=5.0)
        response.raise_for_status()
        return [NotificationPreview.model_validate(item) for item in response.json()]
    except Exception as exc:
        logger.warning("Nao foi possivel consultar o servico de notificacoes: %s", exc)
        return []
