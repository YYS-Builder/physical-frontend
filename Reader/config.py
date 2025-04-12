from pydantic import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./reader.db")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    API_KEY: str = os.getenv("API_KEY", "your-api-key-here")
    
    # API settings
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Documentation settings
    ENABLE_DOCS: bool = os.getenv("ENABLE_DOCS", "True").lower() == "true"
    DOCS_URL: str = os.getenv("DOCS_URL", "/docs")
    REDOC_URL: str = os.getenv("REDOC_URL", "/redoc")
    OPENAPI_URL: str = os.getenv("OPENAPI_URL", "/openapi.json")
    API_TITLE: str = os.getenv("API_TITLE", "Reader API")
    API_DESCRIPTION: str = os.getenv("API_DESCRIPTION", "API for document management and reading analytics")
    
    # Rate limiting settings
    RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
    RATE_LIMIT_TIME_WINDOW: int = int(os.getenv("RATE_LIMIT_TIME_WINDOW", "60"))
    
    # Monitoring settings
    MONITORING_ENABLED: bool = bool(os.getenv("MONITORING_ENABLED", "True"))
    PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", "9090"))
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "reader.log")
    
    # File storage settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    
    # Security settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "300"))  # 5 minutes
    ALLOWED_METHODS: list = ["GET", "POST", "PUT", "DELETE"]
    ALLOWED_CONTENT_TYPES: list = ["application/json"]
    MAX_REQUEST_SIZE: int = int(os.getenv("MAX_REQUEST_SIZE", "1048576"))  # 1MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 