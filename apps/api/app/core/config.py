from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agentic AI API"
    environment: str = "local"
    api_prefix: str = "/v1"
    cors_origins: list[str] = ["http://localhost:3000"]
    database_url: str = "sqlite:///./agentic_ai.db"
    auto_create_tables: bool = True
    session_signing_secret: Optional[str] = None
    session_signature_ttl_seconds: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AGENTIC_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
