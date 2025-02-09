from typing import Any, Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Класс конфигурации приложения"""
    environment: str = 'development'
    is_debug: bool = True
    host: str = '127.0.0.1'
    port: int = 8080
    log_level: str = 'info'
    docs_name: str = 'auth'
    
    # Настройки базы данных
    postgres_host: str
    postgres_username: str
    postgres_password: str
    postgres_port: int
    postgres_db_name: str
    postgres_url: str

    # Настройка почтового клиента
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_from: str 

    # Настройка Redis
    redis_host: str
    redis_port: int
    redis_db: int

    # JWT настройки
    jwt_secret_key: str
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    secure_cookies: bool = False  # change for True in production

    fake_link: str = "http://localhost:8080/api/v1/auth/simulate_password_reset_link"
    reset_url: str = "http://localhost:8080/api/v1/users/reset_password"

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

    @property
    def service_name(self) -> str:
        return self.docs_name

    @field_validator('postgres_url', mode='before')
    def assemble_postgres_connection(cls, v: Optional[str], values: dict[str, Any]) -> str:
        if v is not None:
            return v
        # Construct the PostgreSQL connection string
        return f"postgresql://{values['postgres_username']}:{values['postgres_password']}@{values['postgres_host']}:{values['postgres_port']}/{values['postgres_db_name']}"

settings = Settings()
