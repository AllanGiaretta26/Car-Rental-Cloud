import json
from functools import lru_cache
from typing import Any

import redis

from app.core.config import get_settings


@lru_cache
def get_redis_client() -> redis.Redis:
    settings = get_settings()
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


class EventQueueService:
    def __init__(self, redis_client: redis.Redis | None = None) -> None:
        self.settings = get_settings()
        self.redis = redis_client or get_redis_client()

    def enqueue_payment(self, payload: dict[str, Any]) -> None:
        self.redis.rpush(self.settings.payment_queue_name, json.dumps(payload))

    def enqueue_notification(self, payload: dict[str, Any]) -> None:
        self.redis.rpush(self.settings.notification_queue_name, json.dumps(payload))


@lru_cache
def get_queue_service() -> EventQueueService:
    return EventQueueService()
