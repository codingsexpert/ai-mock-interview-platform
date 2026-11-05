"""Application configuration module using Pydantic Settings."""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime settings and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Mock Interview API"
    environment: str = "development"
    debug: bool = True
    port: int = 8000
    host: str = "0.0.0.0"

    # Streamlit client origins
    cors_origins: List[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ]

    # AI & Observability
    gemini_api_key: str = ""
    langchain_tracing_v2: str = "false"
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: str = ""
    langchain_project: str = "mock-interview-agent"

    # Database & Storage
    database_url: str = ""
    sarvam_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    """Return cached instance of application settings."""
    return Settings()
