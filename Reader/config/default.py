import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Application
APP_NAME = "Reader"
APP_VERSION = "0.1.0"
DEBUG = False
TESTING = False

# API
API_PREFIX = "/api/v1"
API_TITLE = "Reader API"
API_DESCRIPTION = "API for the Reader application"
API_VERSION = "0.1.0"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reader.db")
DATABASE_POOL_SIZE = 5
DATABASE_MAX_OVERFLOW = 10

# File Storage
UPLOAD_DIR = BASE_DIR / "uploads"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Cache
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = 3600  # 1 hour

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = BASE_DIR / "logs" / "reader.log"

# AI Model
AI_MODEL_URL = os.getenv("AI_MODEL_URL", "http://localhost:8001")
AI_MODEL_TIMEOUT = 30

# Create necessary directories
for directory in [UPLOAD_DIR, BASE_DIR / "logs"]:
    directory.mkdir(parents=True, exist_ok=True) 