from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Le variaveis de ambiente e ignora chaves extras.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "car-rental-api"
    app_env: str = "development"
    database_url: str = "sqlite:////data/rental.db"
    redis_url: str = "redis://redis:6379/0"
    payment_queue_name: str = "payments:pending"
    notification_queue_name: str = "notifications:pending"
    internal_service_token: str = "change-me"
    notification_service_url: str = "http://notification-service:8002"
    cors_origins: str = "http://localhost:3000,http://frontend"
    seed_demo_data: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        # Converte a string do .env em lista para o middleware CORS.
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    # Evita recriar a configuracao a cada import.
    return Settings()
