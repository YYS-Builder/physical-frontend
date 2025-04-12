from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import logger, monitor, exceptions
from .. import models, schemas
from ..config import settings

class SessionManager:
    def __init__(self):
        self.logger = logger.logger
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    async def create_session(
        self,
        db: Session,
        user: models.User,
        provider: Optional[str] = None,
        provider_token: Optional[str] = None
    ) -> schemas.Session:
        """Create a new user session."""
        try:
            # Create session record in database
            db_session = models.Session(
                user_id=user.id,
                provider=provider,
                provider_token=provider_token,
                expires_at=datetime.utcnow() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)
            )
            db.add(db_session)
            db.commit()
            db.refresh(db_session)

            # Store session in memory
            session_data = {
                "user_id": user.id,
                "email": user.email,
                "provider": provider,
                "created_at": datetime.utcnow(),
                "expires_at": db_session.expires_at
            }
            self.active_sessions[str(db_session.id)] = session_data

            self.logger.info(f"Created session for user {user.email}")
            monitor.track_request(0)  # Track session creation
            return schemas.Session.from_orm(db_session)
        except Exception as e:
            self.logger.error(f"Error creating session: {str(e)}")
            monitor.track_error("Session", str(e))
            raise exceptions.AuthenticationError("Failed to create session")

    async def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate a session and return session data if valid."""
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return None

            # Check if session is expired
            if datetime.utcnow() > session_data["expires_at"]:
                del self.active_sessions[session_id]
                return None

            return session_data
        except Exception as e:
            self.logger.error(f"Error validating session: {str(e)}")
            monitor.track_error("Session", str(e))
            return None

    async def refresh_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Refresh an existing session."""
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return None

            # Update expiration time
            new_expires_at = datetime.utcnow() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)
            session_data["expires_at"] = new_expires_at

            self.logger.info(f"Refreshed session {session_id}")
            monitor.track_request(0)  # Track session refresh
            return session_data
        except Exception as e:
            self.logger.error(f"Error refreshing session: {str(e)}")
            monitor.track_error("Session", str(e))
            return None

    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session."""
        try:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                self.logger.info(f"Invalidated session {session_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error invalidating session: {str(e)}")
            monitor.track_error("Session", str(e))
            return False

    async def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        try:
            current_time = datetime.utcnow()
            expired_sessions = [
                session_id for session_id, session_data in self.active_sessions.items()
                if current_time > session_data["expires_at"]
            ]
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
            
            if expired_sessions:
                self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        except Exception as e:
            self.logger.error(f"Error cleaning up sessions: {str(e)}")
            monitor.track_error("Session", str(e))

# Create global session manager instance
session_manager = SessionManager() 