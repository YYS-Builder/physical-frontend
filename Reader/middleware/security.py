from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional, Dict, Any
import hmac
import hashlib
import time
import json
from datetime import datetime, timedelta

from ..config import settings
from ..logger import logger
from ..monitor import monitor

class SecurityMiddleware:
    def __init__(self):
        self.api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
        self.signature_header = "X-Signature"
        self.timestamp_header = "X-Timestamp"
        self.max_request_age = 300  # 5 minutes in seconds

    async def __call__(self, request: Request) -> None:
        """Process incoming request for security checks."""
        try:
            # Skip security checks for health and metrics endpoints
            if request.url.path in ["/health", "/metrics"]:
                return

            # Validate API key
            api_key = await self._validate_api_key(request)
            
            # Validate request signature
            await self._validate_signature(request, api_key)
            
            # Validate request timestamp
            await self._validate_timestamp(request)
            
            # Track security check
            monitor.track_security_check(request.url.path, "success")
            
        except HTTPException as e:
            monitor.track_security_check(request.url.path, "failed", str(e))
            raise e
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            monitor.track_security_check(request.url.path, "error", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def _validate_api_key(self, request: Request) -> str:
        """Validate API key from request header."""
        api_key = await self.api_key_header(request)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is required"
            )
        
        if api_key != settings.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        return api_key

    async def _validate_signature(self, request: Request, api_key: str) -> None:
        """Validate request signature."""
        signature = request.headers.get(self.signature_header)
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Request signature is required"
            )

        # Get request body
        body = await self._get_request_body(request)
        
        # Calculate expected signature
        expected_signature = self._calculate_signature(
            method=request.method,
            path=request.url.path,
            body=body,
            timestamp=request.headers.get(self.timestamp_header),
            api_key=api_key
        )

        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid request signature"
            )

    async def _validate_timestamp(self, request: Request) -> None:
        """Validate request timestamp."""
        timestamp = request.headers.get(self.timestamp_header)
        if not timestamp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Timestamp is required"
            )

        try:
            request_time = datetime.fromtimestamp(int(timestamp))
            current_time = datetime.now()
            
            if abs((current_time - request_time).total_seconds()) > self.max_request_age:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request timestamp is too old"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid timestamp format"
            )

    async def _get_request_body(self, request: Request) -> str:
        """Get request body as string."""
        try:
            body = await request.body()
            return body.decode()
        except Exception:
            return ""

    def _calculate_signature(
        self,
        method: str,
        path: str,
        body: str,
        timestamp: str,
        api_key: str
    ) -> str:
        """Calculate request signature."""
        message = f"{method}{path}{body}{timestamp}"
        signature = hmac.new(
            api_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

# Create global instance
security_middleware = SecurityMiddleware() 