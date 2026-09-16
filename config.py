from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Telegram Bot
    BOT_TOKEN: str
    
    # Database
    DATABASE_URL: str

    #Time
    TIMEZONE: str
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_URL: str = "http://127.0.0.1:8000"
    API_TITLE: str = "Request Service API"
    API_REQUEST_TIMEOUT: float = 5.0
    MAX_ACTIVE_REQUESTS: int = 2

    # Scheduler
    CLEANUP_INTERVAL_SECONDS: int = 3600
    COMPLETED_REQUEST_RETENTION_DAYS: int = 30
    
    # Environment
    DEBUG: bool = False

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()