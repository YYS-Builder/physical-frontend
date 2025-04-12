from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
from ..monitor.api_metrics import api_monitor

class APIMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Track metrics
        await api_monitor.track_request(
            endpoint=request.url.path,
            method=request.method,
            duration=duration,
            status_code=response.status_code
        )
        
        # Track response size
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        await api_monitor.track_response_size(
            endpoint=request.url.path,
            method=request.method,
            size=len(response_body)
        )
        
        # Reconstruct response
        return response 