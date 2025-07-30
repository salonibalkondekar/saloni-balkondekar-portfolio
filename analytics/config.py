"""
Configuration for analytics service
"""

import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Analytics service settings"""

    # Database
    database_url: str = Field(
        default="postgresql://analytics:analytics_password@postgres:5432/analytics_db",
        env="DATABASE_URL",
    )

    # Admin
    admin_password: str = Field(default="change_me_in_production", env="ADMIN_PASSWORD")

    # Security
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production", env="SECRET_KEY"
    )
    session_expire_hours: int = 24 * 7  # 1 week

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_minutes: int = 60
    rate_limit_block_minutes: int = 60

    # CORS
    cors_origins: list[str] = Field(default=["*"])

    # Service info
    service_name: str = "Analytics Service"
    service_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
