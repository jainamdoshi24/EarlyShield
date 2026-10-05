"""
FastAPI configuration and environment variables
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Early AI"
    APP_VERSION: str = "3.0.0"
    DEBUG: bool = False

    # API
    API_PREFIX: str = "/api"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # Model
    MODEL_PATH: str = "backend/earlyshield_model.pkl"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
