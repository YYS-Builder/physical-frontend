from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Awaitable
from ..config import settings

class VersioningMiddleware(BaseHTTPMiddleware):
    """Middleware for API version negotiation."""
    
    def __init__(self, app):
        super().__init__(app)
        self.supported_versions = ["1.0.0", "1.1.0"]  # Add more versions as needed
        self.default_version = settings.API_VERSION
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Get requested version from header or query parameter
        requested_version = (
            request.headers.get("X-API-Version") or
            request.query_params.get("api-version") or
            self.default_version
        )
        
        # Validate version
        if requested_version not in self.supported_versions:
            requested_version = self.default_version
        
        # Add version to request state
        request.state.api_version = requested_version
        
        # Process request
        response = await call_next(request)
        
        # Add version headers to response
        response.headers["X-API-Version"] = requested_version
        response.headers["X-API-Supported-Versions"] = ", ".join(self.supported_versions)
        
        return response 