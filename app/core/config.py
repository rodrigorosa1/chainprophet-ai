from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PYTHON_VERSION: str
    APP_NAME: str
    PORT: int
    DEBUG: bool = True
    DATABASE_URL: str
    SECRET_KEY: str = "3abc99c6afb0ae67124598af47e30f4bc907c395e239f9603b62b711c02dcd69"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3600
    TESTING: bool = False
    APPLICATION_URL: str
    TIMEZONE: str = "America/Sao_Paulo"
    POOL_RECYCLE: int = 3600
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4.1-mini"
    OPENAI_TIMEOUT_SECONDS: int = 60

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
