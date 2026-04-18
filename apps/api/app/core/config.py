from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agentic AI API"
    environment: str = "local"
    api_prefix: str = "/v1"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AGENTIC_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
