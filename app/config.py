"""Application configuration using environment variables."""
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Runtime configuration for the API."""

    app_name: str = Field(default="AI Financial Risk Engine")
    database_url: str = Field(default="postgresql+psycopg2://postgres:postgres@localhost:5432/risk_engine")
    jwt_secret_key: str = Field(default="change-me")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
