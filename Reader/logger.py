import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
def setup_logger(name: str = "reader") -> logging.Logger:
    """Set up and return a configured logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # File handler for all logs
    file_handler = RotatingFileHandler(
        log_dir / "reader.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Error file handler
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger

# Create default logger instance
logger = setup_logger()

# Create separate loggers for different components
auth_logger = logging.getLogger("reader.auth")
db_logger = logging.getLogger("reader.db")
api_logger = logging.getLogger("reader.api")
error_logger = logging.getLogger("reader.error") 