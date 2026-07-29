from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# A checkout should be usable without Docker or a running PostgreSQL service.
# Docker supplies its PostgreSQL URL through the environment (see
# docker-compose.yml), while local development uses this persistent demo DB.
DEFAULT_DATABASE_URL = f"sqlite:///{Path(__file__).resolve().parents[2] / 'demo.db'}"


class Settings(BaseSettings):
    # App
    APP_NAME: str = "InsuraMind AI"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = DEFAULT_DATABASE_URL

    # Auth
    JWT_SECRET_KEY: str = "change-this-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
