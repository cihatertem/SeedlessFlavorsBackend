# app/core/config.py
from pydantic_settings import SettingsConfigDict, BaseSettings


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.fastapi", extra="allow")


class GlobalConfig(BaseConfig):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int


settings = GlobalConfig()
