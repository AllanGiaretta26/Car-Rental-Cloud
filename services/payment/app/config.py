from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Parametros do worker de pagamento e do callback interno.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "payment-service"
    app_env: str = "development"
    redis_url: str = "redis://redis:6379/0"
    payment_queue_name: str = "payments:pending"
    api_internal_url: str = "http://api:8000/internal/payments/process-result"
    internal_service_token: str = "change-me"
    simulated_payment_delay_seconds: int = Field(default=4, ge=1, le=30)
    callback_timeout_seconds: int = Field(default=10, ge=1, le=60)
    max_callback_retries: int = Field(default=3, ge=0, le=10)


@lru_cache
def get_settings() -> Settings:
    # Reaproveita a mesma configuracao durante a vida do processo.
    return Settings()
