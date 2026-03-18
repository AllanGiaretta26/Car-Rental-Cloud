from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Parametros minimos para ler a fila e guardar o historico em memoria.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "notification-service"
    app_env: str = "development"
    redis_url: str = "redis://redis:6379/0"
    notification_queue_name: str = "notifications:pending"
    max_notifications_in_memory: int = Field(default=30, ge=10, le=100)


@lru_cache
def get_settings() -> Settings:
    # Reaproveita a mesma configuracao durante a vida do processo.
    return Settings()
