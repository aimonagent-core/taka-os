# File: app/config.py
# Purpose: Centralized Pydantic Settings configuration
# Dependencies: pydantic-settings

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TAKA API"
    app_version: str = "0.2.0"
    environment: str = "development"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://taka:taka_password@db:5432/taka_db"
    database_url_sync: str = "postgresql://taka:taka_password@db:5432/taka_db"

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    frontend_url: str = "http://localhost:5173"

    sentry_dsn: str | None = None
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 0.1

    redis_url: str = "redis://localhost:6379/0"
    rate_limit_default: str = "100/minute"
    rate_limit_auth: str = "10/minute"
    rate_limit_health: str = "60/minute"

    mfa_enabled: bool = True
    mfa_issuer_name: str = "TAKA Platform"

    mistral_api_key: str | None = None
    mistral_base_url: str = "https://api.mistral.ai/v1"
    mistral_primary_model: str = "mistral-medium-latest"
    mistral_fallback_model: str = "mistral-small-latest"

    s3_backup_bucket: str | None = None
    s3_backup_endpoint: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    backup_retention_days: int = 30

    # CORS — en staging/production, liste restreinte
    cors_origins: str = "http://localhost:5173,https://localhost"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_staging(self) -> bool:
        return self.environment == "staging"

    @property
    def sentry_enabled(self) -> bool:
        return bool(self.sentry_dsn)

    @property
    def s3_backup_enabled(self) -> bool:
        return bool(self.s3_backup_bucket and self.aws_access_key_id)

    @property
    def cors_origins_list(self) -> List[str]:
        if self.is_production or self.is_staging:
            return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        return ["*"]


settings = Settings()
