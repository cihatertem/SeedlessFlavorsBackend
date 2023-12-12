# app/core/config.py
from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    # model_config = SettingsConfigDict(env_file=".env.fastapi", extra="allow")
    pass


class GlobalConfig(BaseConfig):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    SECRET_KEY: str  # openssl rand -base64 32
    PIN: str


settings = GlobalConfig()
