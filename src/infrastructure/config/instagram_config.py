"""Instagram Integration Configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class InstagramConfig(BaseSettings):
    """Instagram integration settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    hikerapi_key: str = Field(..., description="HikerAPI access key")
    hikerapi_base_url: str = Field(default="https://api.hikerapi.com", description="HikerAPI base URL")
    cache_ttl_seconds: int = Field(default=300, description="Cache TTL in seconds")
    rate_limit_requests_per_minute: int = Field(default=10, description="Max requests per minute")


instagram_config = InstagramConfig()
