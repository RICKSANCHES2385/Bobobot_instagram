"""Application settings."""

from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Telegram
    telegram_bot_token: str = Field(..., description="Telegram Bot API token")

    # Database
    database_url: str = Field(..., description="PostgreSQL connection URL")

    # Redis (optional)
    redis_url: str | None = Field(default=None, description="Redis connection URL (optional)")

    @field_validator("redis_url", mode="before")
    @classmethod
    def validate_redis_url(cls, v: Any) -> str | None:
        """Validate Redis URL - allow None or empty string."""
        if v is None or v == "":
            return None
        return v

    # HikerAPI
    hikerapi_key: str = Field(..., description="HikerAPI access key")
    hikerapi_base_url: str = Field(
        default="https://api.hikerapi.com",
        description="HikerAPI base URL"
    )

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(
        default=10,
        description="Max requests per minute per user"
    )
    rate_limit_requests_per_day: int = Field(
        default=100,
        description="Max requests per day per user"
    )

    # Cache
    cache_ttl_seconds: int = Field(
        default=300,
        description="Cache TTL in seconds (5 minutes)"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/bot.log", description="Log file path")

    # Application
    environment: str = Field(default="production", description="Environment (dev/production)")

    # Support Contacts
    support_email: str = Field(
        default="support@example.com",
        description="Support email address"
    )
    support_telegram: str = Field(
        default="@support_bot",
        description="Support Telegram username"
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
