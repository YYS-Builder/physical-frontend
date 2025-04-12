from fastapi import status
from typing import Optional, Dict, Any
from .logger import logger
from .monitor import monitor

class ReaderException(Exception):
    """Base exception class for Reader application."""
    
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        self.context = context or {}
        logger.error(f"ReaderException: {detail}")
        monitor.track_error("ReaderException", str(detail))

class AuthenticationError(ReaderException):
    """Exception raised for authentication errors."""
    
    def __init__(
        self,
        detail: str = "Authentication failed",
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            context=context
        )

class AuthorizationError(ReaderException):
    """Exception raised for authorization errors."""
    
    def __init__(
        self,
        detail: str = "Not authorized",
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code,
            context=context
        )

class ResourceNotFoundError(ReaderException):
    """Exception raised when a resource is not found."""
    
    def __init__(
        self,
        detail: str = "Resource not found",
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=error_code,
            context=context
        )

class ValidationError(ReaderException):
    """Exception raised for validation errors."""
    
    def __init__(
        self,
        detail: str = "Validation error",
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=error_code,
            context=context
        )

class StorageError(ReaderException):
    """Exception raised for storage-related errors."""
    
    def __init__(
        self,
        detail: str = "Storage error",
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=error_code,
            context=context
        )

class DatabaseError(ReaderException):
    """Exception raised for database-related errors."""
    
    def __init__(
        self,
        detail: str = "Database error",
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=error_code,
            context=context
        )

class RateLimitError(ReaderException):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=error_code,
            context=context
        )

class ServiceUnavailableError(ReaderException):
    """Exception raised when a service is unavailable."""
    
    def __init__(
        self,
        detail: str = "Service unavailable",
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=error_code,
            context=context
        ) 