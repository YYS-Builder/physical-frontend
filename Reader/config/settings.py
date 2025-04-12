from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "sqlite:///./reader.db"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Reader"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list = ["*"]  # Change this in production
    
    class Config:
        case_sensitive = True

settings = Settings() 