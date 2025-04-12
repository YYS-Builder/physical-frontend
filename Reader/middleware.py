from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from typing import Dict, Any, Optional
from .logger import error_logger, api_logger
from .config import settings
import json
from .exceptions import ReaderException
from .monitor import monitor

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.app = app

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        try:
            response = await call_next(request)
            return response
        except ReaderException as e:
            error_logger.error(f"Reader error: {str(e)}", exc_info=True)
            monitor.track_error("Reader", str(e))
            return Response(
                status_code=e.status_code,
                content=json.dumps({"detail": str(e)}),
                media_type="application/json"
            )
        except Exception as e:
            error_logger.error(f"Error processing request: {str(e)}", exc_info=True)
            monitor.track_error("System", str(e))
            return Response(
                status_code=500,
                content=json.dumps({"detail": "Internal server error occurred"}),
                media_type="application/json"
            )

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.max_requests = settings.RATE_LIMIT_REQUESTS
        self.time_window = settings.RATE_LIMIT_WINDOW
        self.requests: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        # Clean up old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                t for t in self.requests[client_ip]
                if current_time - t < self.time_window
            ]

        # Check rate limit
        if client_ip in self.requests and len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"}
            )

        # Add current request
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(current_time)

        response = await call_next(request)
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.app = app

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        # Log request
        api_logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client": request.client.host if request.client else None
            }
        )

        # Process request
        response = await call_next(request)

        # Log response
        api_logger.info(
            f"Response: {request.method} {request.url.path} {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "response_time": response.headers.get("X-Response-Time")
            }
        )

        return response

class ResponseTimeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.app = app

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Response-Time"] = str(process_time)
        return response

def setup_middleware(app: FastAPI) -> None:
    """Set up all middleware for the application."""
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimiterMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(ResponseTimeMiddleware) 