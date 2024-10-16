from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Optional


class Settings(BaseSettings):
    """Класс конфигурации приложения"""
    environment: str = 'development'
    is_debug: bool = True
    host: str = '127.0.0.1'
    port: int = 8080
    log_level: str = 'info'
    docs_name: str = 'auth'
    
    #настройка базы данных
    postgres_host: str
    postgres_username: str
    postgres_password: str
    postgres_port: int
    postgre_db_name: str
    postgres_url: Optional[PostgresDsn] = None

    model_config = SettingsConfigDict(
        env_file = '.env'
        env_file_encoding='utf-8'
    )

    @property
    def service_name(
        self,
    ) -> str:
        return self.docs_name
    
    @field_validator('postgres_url', mode='before')
    def assemble_postgres_connection(cls, v: Optional[str], values: dict[str[Any]]) -> str:
        if v is not None:
            return v
        
        return PostgresDsn.build(
            scheme='postgresql',
            user=values['postgres_username'],
            password=values['postgres_password'],
            host=values['postgres_host'],
            port=str(values['postgres_port']),
            path=f'/{values['postgres_db_name']}',
        )
    
settings = Settings()