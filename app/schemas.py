import os
from datetime import datetime
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import AmqpDsn, BaseModel, Field, PostgresDsn, validator
from pydantic_settings import BaseSettings

load_dotenv()


class DBSettings(BaseSettings):
    """Pydantic модель для валидации настроек PostgreSQL и сборки URL адреса"""

    POSTGRES_HOST: str = Field(default=os.getenv("POSTGRES_HOST", default="localhost"))
    POSTGRES_PORT: int = Field(default=os.getenv("POSTGRES_PORT", default=5432))
    POSTGRES_USER: str = Field(default=os.getenv("POSTGRES_USER", default="postgres"))
    POSTGRES_PASSWORD: str = Field(
        default=os.getenv("POSTGRES_PASSWORD", default="12345")
    )
    POSTGRES_DB: str = Field(default=os.getenv("POSTGRES_DB", default="postgres"))
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_url(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values["POSTGRES_USER"],
            password=values["POSTGRES_PASSWORD"],
            host=values["POSTGRES_HOST"],
            port=values["POSTGRES_PORT"],
            path=f"{values.get('POSTGRES_DB') or ''}",
        )


class RabbitSettings(BaseSettings):
    """Pydantic модель для валидации настроек RabbitMQ и сборки URL адреса"""

    RABBIT_HOST: str = Field(default=os.getenv("RABBIT_HOST", default="localhost"))
    RABBIT_PORT: int = Field(default=os.getenv("RABBIT_PORT", default=5432))
    RABBIT_USER: str = Field(default=os.getenv("RABBIT_USER", default="postgres"))
    RABBIT_PASSWORD: str = Field(default=os.getenv("RABBIT_PASSWORD", default="12345"))
    RABBIT_VHOST: str = Field(default=os.getenv("RABBIT_VHOST", default=""))
    RABBIT_QUEUE: str = Field(default=os.getenv("RABBIT_QUEUE", default="rabbit"))
    RABBIT_EXCHANGE: str = Field(default=os.getenv("RABBIT_EXCHANGE", default="rabbit"))
    RABBIT_URL: Optional[AmqpDsn] = None

    @validator("RABBIT_URL", pre=True)
    def assemble_rabbit_url(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return AmqpDsn.build(
            scheme="amqp",
            username=values["RABBIT_USER"],
            password=values["RABBIT_PASSWORD"],
            host=values["RABBIT_HOST"],
            port=values["RABBIT_PORT"],
            path=f"{values.get('RABBIT_VHOST') or ''}",
        )


class Settings(BaseSettings):
    db: BaseSettings = DBSettings()
    rabbit: BaseSettings = RabbitSettings()


settings = Settings()


class ResultCounter(BaseModel):
    """Pydantic модель для валидации данныых, полученных из БД"""

    datetime: datetime
    title: str
    x_avg_count_in_line: float


class CheckLine(BaseModel):
    """Pydantic модель для валидации строк, отправляемых в БД"""

    datetime: datetime
    title: str
    text: str
