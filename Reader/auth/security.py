from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from typing import Optional
import hmac
import hashlib
import time
from ..config import settings

api_key_header = APIKeyHeader(name="X-API-Key")

class SecurityManager:
    def __init__(self):
        self.api_keys = {}  # In production, store in database
        self.request_signatures = {}
    
    async def validate_api_key(self, api_key: str) -> bool:
        """Validate API key."""
        # In production, validate against database
        return api_key in self.api_keys
    
    async def generate_request_signature(self, request: Request) -> str:
        """Generate request signature."""
        # Get request data
        method = request.method
        path = request.url.path
        timestamp = str(int(time.time()))
        body = await request.body()
        
        # Create signature string
        signature_string = f"{method}{path}{timestamp}{body.decode()}"
        
        # Generate HMAC signature
        signature = hmac.new(
            settings.SECRET_KEY.encode(),
            signature_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    async def validate_request_signature(self, request: Request) -> bool:
        """Validate request signature."""
        # Get signature from header
        signature = request.headers.get("X-Request-Signature")
        if not signature:
            return False
        
        # Get timestamp from header
        timestamp = request.headers.get("X-Request-Timestamp")
        if not timestamp:
            return False
        
        # Check if request is too old (5 minutes)
        if int(time.time()) - int(timestamp) > 300:
            return False
        
        # Generate expected signature
        expected_signature = await self.generate_request_signature(request)
        
        # Compare signatures
        return hmac.compare_digest(signature, expected_signature)
    
    async def validate_request(self, request: Request) -> bool:
        """Validate API request."""
        # Check API key
        api_key = request.headers.get("X-API-Key")
        if not api_key or not await self.validate_api_key(api_key):
            return False
        
        # Check request signature
        if not await self.validate_request_signature(request):
            return False
        
        return True

# Global instance
security_manager = SecurityManager()

async def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    """Dependency to validate API key."""
    if not await security_manager.validate_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return api_key

async def validate_signed_request(request: Request) -> None:
    """Middleware to validate signed requests."""
    if not await security_manager.validate_request(request):
        raise HTTPException(
            status_code=401,
            detail="Invalid request signature"
        ) 