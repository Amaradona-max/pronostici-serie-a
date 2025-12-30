"""
Application Configuration
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # External APIs
    API_FOOTBALL_KEY: str = ""
    FOOTBALL_DATA_KEY: str = ""

    # Security
    SECRET_KEY: str
    CORS_ORIGINS: str = "*"

    # Environment
    ENVIRONMENT: str = "development"

    # Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str = ""

    # Feature Flags
    ENABLE_LIVE_UPDATES: bool = False
    ENABLE_ADMIN_ENDPOINTS: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string to list"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        try:
            # Try to parse as JSON array
            origins = json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            # Fallback: split by comma
            origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

        # Always include localhost for development
        localhost_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3002"
        ]
        return list(set(origins + localhost_origins))

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"


# Singleton instance
_settings = None


def get_settings() -> Settings:
    """Get settings singleton instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
