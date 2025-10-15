from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: Optional[str] = "redis://localhost:6379"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    GEMINI_API_KEY: Optional[str] = ""
    UPLOAD_DIR: str = os.path.abspath("./uploads")
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB

    class Config:
        env_file = ".env"

settings = Settings()
