from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Dict, Tuple
import asyncio
from ..config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 5, time_window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, List[float]] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Get current timestamp
        current_time = time.time()
        
        # Clean up old requests
        self._cleanup_old_requests(current_time)
        
        # Check rate limit
        if not self._check_rate_limit(client_ip, current_time):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": self._get_retry_after(client_ip, current_time)
                },
                headers={"Retry-After": str(self._get_retry_after(client_ip, current_time))}
            )
        
        # Add request to tracking
        self._add_request(client_ip, current_time)
        
        # Process request
        response = await call_next(request)
        return response
    
    def _cleanup_old_requests(self, current_time: float):
        """Remove requests older than the time window."""
        for ip in list(self.requests.keys()):
            self.requests[ip] = [
                timestamp for timestamp in self.requests[ip]
                if current_time - timestamp < self.time_window
            ]
            if not self.requests[ip]:
                del self.requests[ip]
    
    def _check_rate_limit(self, client_ip: str, current_time: float) -> bool:
        """Check if the client has exceeded the rate limit."""
        if client_ip not in self.requests:
            return True
        return len(self.requests[client_ip]) < self.max_requests
    
    def _add_request(self, client_ip: str, current_time: float):
        """Add a new request to the tracking."""
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(current_time)
    
    def _get_retry_after(self, client_ip: str, current_time: float) -> int:
        """Calculate how long the client should wait before retrying."""
        if client_ip not in self.requests:
            return 0
        oldest_request = min(self.requests[client_ip])
        return int(self.time_window - (current_time - oldest_request)) 