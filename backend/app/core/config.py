from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Online Bookstore API"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    testing: bool = False

    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120

    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "online_bookstore"

    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    admin_email: str = "admin@bookstore.com"
    admin_password: str = "Admin@12345"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="BOOKSTORE_",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
