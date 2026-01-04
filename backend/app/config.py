from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
import os
import logging

# Configure logger
config_logger = logging.getLogger("config")

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str

    def __init__(self, **data):
        super().__init__(**data)
        # Fly.io uses postgres:// but SQLAlchemy needs postgresql://
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgres://"):
            object.__setattr__(self, 'DATABASE_URL', self.DATABASE_URL.replace("postgres://", "postgresql://", 1))

    # Security settings
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # API Integration
    GEMINI_API_KEY: Optional[str] = ""

    # File Storage
    UPLOAD_DIR: str = os.path.abspath("./uploads")
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB

    # Application settings
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "*"

    # Cache settings (optional)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 86400  # 24 hours

    class Config:
        env_file = ".env"

try:
    # Try to read environment variables
    config_dict: Dict[str, Any] = {}

    # Check for render.com specific environment variables
    if os.environ.get("RENDER") == "true":
        config_logger.info("Running in Render.com environment")
        # Ensure uploads directory exists in the Render disk mount
        if os.environ.get("RENDER_VOLUME_MOUNT_PATH"):
            mount_path = os.environ.get("RENDER_VOLUME_MOUNT_PATH", "")
            config_dict["UPLOAD_DIR"] = os.path.join(mount_path, "uploads")
            os.makedirs(config_dict["UPLOAD_DIR"], exist_ok=True)
            config_logger.info(f"Using Render volume mount for uploads: {config_dict['UPLOAD_DIR']}")

    # Fallback DATABASE_URL for development if not set
    if not os.environ.get("DATABASE_URL") and os.environ.get("ENVIRONMENT") != "production":
        config_logger.warning("No DATABASE_URL provided. Using SQLite for development")
        config_dict["DATABASE_URL"] = "sqlite:///./hazop.db"

    settings = Settings(**config_dict)
    config_logger.info(f"Config loaded successfully. Environment: {settings.ENVIRONMENT}")

except Exception as e:
    config_logger.error(f"Error loading configuration: {e}")
    # Create minimal settings to allow application to start
    if os.environ.get("ENVIRONMENT") != "production":
        config_logger.warning("Using default configuration for development")
        settings = Settings(
            DATABASE_URL="sqlite:///./hazop.db",
            JWT_SECRET="development_secret_key_not_for_production",
            ENVIRONMENT="development"
        )
    else:
        config_logger.critical("Failed to load configuration in production mode")
        raise
