from fastapi.openapi.utils import get_openapi
from typing import Dict, Any
from ..config import settings

def custom_openapi() -> Dict[str, Any]:
    """Generate custom OpenAPI schema with detailed documentation."""
    if settings.ENABLE_DOCS:
        return get_openapi(
            title="Reader API",
            version=settings.API_VERSION,
            description="""
            # Reader API Documentation

            ## Overview
            The Reader API provides endpoints for document management and reading analytics.
            
            ## Authentication
            All endpoints require authentication using either:
            - JWT Bearer token
            - API Key with request signing
            
            ## Rate Limiting
            API requests are limited to {max_requests} requests per {time_window} seconds.
            
            ## Error Handling
            The API uses standard HTTP status codes and returns detailed error messages.
            
            ## Response Format
            All responses follow the format:
            ```json
            {
                "status": "success|error",
                "data": { ... },
                "message": "Optional message"
            }
            ```
            """.format(
                max_requests=settings.RATE_LIMIT_MAX_REQUESTS,
                time_window=settings.RATE_LIMIT_TIME_WINDOW
            ),
            routes=[],
            servers=[
                {"url": "http://localhost:8000", "description": "Development server"},
                {"url": "https://api.reader.com", "description": "Production server"}
            ],
            components={
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT Bearer token authentication"
                    },
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key",
                        "description": "API key authentication"
                    }
                },
                "schemas": {
                    "Error": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "error"},
                            "message": {"type": "string", "example": "Error message"},
                            "code": {"type": "integer", "example": 400}
                        }
                    },
                    "Success": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "success"},
                            "data": {"type": "object"},
                            "message": {"type": "string", "example": "Success message"}
                        }
                    }
                }
            },
            tags=[
                {
                    "name": "Authentication",
                    "description": "User authentication and authorization endpoints"
                },
                {
                    "name": "Collections",
                    "description": "Document collection management endpoints"
                },
                {
                    "name": "Documents",
                    "description": "Document management and reading endpoints"
                },
                {
                    "name": "AI Features",
                    "description": "AI-powered document analysis endpoints"
                }
            ]
        )
    return {} 