from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "FinEdge Pro"
    ENV: str = "dev"
    DEBUG: bool = True
    JWT_SECRET: str = "devsecret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "sqlite:///./finedge.db"
    CORS_ALLOW_ORIGINS: str = "http://localhost:5173"

    LLM_PROVIDER: str | None = None
    LLM_API_KEY: str | None = None
    LLM_MODEL: str | None = None

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
