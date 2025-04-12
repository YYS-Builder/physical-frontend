from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import time
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from . import models, schemas
from .database import engine, get_db
from .config import settings
from .routes import router
from .middleware import setup_middleware
from .logger import logger
from .api import collections, documents, ai, auth
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.api_metrics import APIMetricsMiddleware
from .middleware.versioning import VersioningMiddleware
from .docs.api_docs import custom_openapi
from .auth.security import validate_signed_request, get_api_key
from .monitor.prometheus import prometheus_metrics
from .middleware.security import security_middleware
from .monitor import monitor

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url=settings.DOCS_URL if settings.ENABLE_DOCS else None,
    redoc_url=settings.REDOC_URL if settings.ENABLE_DOCS else None,
    openapi_url=settings.OPENAPI_URL if settings.ENABLE_DOCS else None
)

# Setup middleware
setup_middleware(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add versioning middleware
app.add_middleware(VersioningMiddleware)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.RATE_LIMIT_MAX_REQUESTS,
    time_window=settings.RATE_LIMIT_TIME_WINDOW
)

# Add API metrics middleware
app.add_middleware(APIMetricsMiddleware)

# Add security middleware
@app.middleware("http")
async def security_middleware_wrapper(request: Request, call_next):
    try:
        await security_middleware(request)
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Security middleware error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Include API routes
app.include_router(router, prefix="/api/v1")
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(collections.router, prefix="/collections", tags=["Collections"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])

# Custom OpenAPI schema
app.openapi = custom_openapi

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Reader API")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Reader API")

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "supported_versions": ["1.0.0", "1.1.0"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

@app.get("/metrics")
async def metrics():
    """Metrics endpoint returning Prometheus metrics."""
    return prometheus_metrics.get_metrics()

# Add API key dependency for all routes except health check and metrics
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    if request.url.path not in ["/health", "/metrics"]:
        await get_api_key(request.headers.get("X-API-Key"))
    response = await call_next(request)
    return response 