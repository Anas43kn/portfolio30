from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Portfolio V2"
    database_url: str = "sqlite:///./app/database.db"
    secret_key: str = "change-me-in-production"
    admin_email: str = "admin@admin.com"
    admin_password: str = "wxcvbn,;:!1234567890"
    max_upload_mb: int = 5
    trusted_proxy_ips: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
