from typing import Optional, Dict, Any
from fastapi import HTTPException
from . import logger, monitor, exceptions
from ..config import settings

class OAuthProvider:
    def __init__(self, provider_name: str, client_id: str, client_secret: str, redirect_uri: str):
        self.provider_name = provider_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.logger = logger.logger

    async def get_authorization_url(self, state: str) -> str:
        """Get the authorization URL for the OAuth provider."""
        try:
            # TODO: Implement provider-specific authorization URL generation
            auth_url = f"https://{self.provider_name}.com/oauth/authorize"
            params = {
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "state": state,
                "response_type": "code",
                "scope": "openid profile email"
            }
            return f"{auth_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        except Exception as e:
            self.logger.error(f"Error generating authorization URL: {str(e)}")
            monitor.track_error("OAuth", str(e))
            raise exceptions.AuthenticationError("Failed to generate authorization URL")

    async def get_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        try:
            # TODO: Implement provider-specific token exchange
            token_data = {
                "access_token": "dummy_token",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "dummy_refresh_token"
            }
            return token_data
        except Exception as e:
            self.logger.error(f"Error exchanging token: {str(e)}")
            monitor.track_error("OAuth", str(e))
            raise exceptions.AuthenticationError("Failed to exchange authorization code")

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from the OAuth provider."""
        try:
            # TODO: Implement provider-specific user info retrieval
            user_info = {
                "sub": "user_id",
                "email": "user@example.com",
                "name": "User Name",
                "picture": "https://example.com/avatar.jpg"
            }
            return user_info
        except Exception as e:
            self.logger.error(f"Error getting user info: {str(e)}")
            monitor.track_error("OAuth", str(e))
            raise exceptions.AuthenticationError("Failed to get user information")

class OAuthManager:
    def __init__(self):
        self.providers: Dict[str, OAuthProvider] = {}
        self.logger = logger.logger

    def register_provider(self, provider_name: str, **kwargs) -> None:
        """Register a new OAuth provider."""
        try:
            provider = OAuthProvider(provider_name, **kwargs)
            self.providers[provider_name] = provider
            self.logger.info(f"Registered OAuth provider: {provider_name}")
        except Exception as e:
            self.logger.error(f"Error registering provider {provider_name}: {str(e)}")
            monitor.track_error("OAuth", str(e))
            raise

    def get_provider(self, provider_name: str) -> Optional[OAuthProvider]:
        """Get a registered OAuth provider."""
        return self.providers.get(provider_name)

    async def handle_callback(self, provider_name: str, code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth callback and return user information."""
        try:
            provider = self.get_provider(provider_name)
            if not provider:
                raise exceptions.AuthenticationError(f"Provider {provider_name} not found")

            # Exchange code for token
            token_data = await provider.get_token(code)
            
            # Get user information
            user_info = await provider.get_user_info(token_data["access_token"])
            
            # Add provider-specific information
            user_info["provider"] = provider_name
            user_info["access_token"] = token_data["access_token"]
            user_info["refresh_token"] = token_data.get("refresh_token")

            return user_info
        except Exception as e:
            self.logger.error(f"Error handling OAuth callback: {str(e)}")
            monitor.track_error("OAuth", str(e))
            raise

# Create global OAuth manager instance
oauth_manager = OAuthManager()

# Register providers from settings
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth_manager.register_provider(
        "google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )

if settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET:
    oauth_manager.register_provider(
        "github",
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        redirect_uri=settings.GITHUB_REDIRECT_URI
    ) 