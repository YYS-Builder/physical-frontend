from typing import Dict, List, Optional, Set
from pydantic import BaseModel
from datetime import datetime
from app.models.document import Document
from app.models.user import User
from app.services.base import BaseService

class CollaborationSession(BaseModel):
    document_id: str
    users: Set[str]
    last_activity: datetime
    changes: List[Dict]

class UserPresence(BaseModel):
    user_id: str
    document_id: str
    last_seen: datetime
    status: str  # "active", "idle", "away"

class CollaborationService(BaseService):
    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.presence: Dict[str, UserPresence] = {}
        
    async def join_session(
        self,
        document: Document,
        user: User
    ) -> CollaborationSession:
        """Join a collaboration session for a document."""
        if document.id not in self.sessions:
            self.sessions[document.id] = CollaborationSession(
                document_id=document.id,
                users=set(),
                last_activity=datetime.utcnow(),
                changes=[]
            )
        
        session = self.sessions[document.id]
        session.users.add(user.id)
        session.last_activity = datetime.utcnow()
        
        # Update user presence
        self.presence[f"{user.id}:{document.id}"] = UserPresence(
            user_id=user.id,
            document_id=document.id,
            last_seen=datetime.utcnow(),
            status="active"
        )
        
        return session
    
    async def leave_session(
        self,
        document: Document,
        user: User
    ) -> bool:
        """Leave a collaboration session."""
        if document.id in self.sessions:
            session = self.sessions[document.id]
            session.users.discard(user.id)
            session.last_activity = datetime.utcnow()
            
            # Remove user presence
            self.presence.pop(f"{user.id}:{document.id}", None)
            
            # Clean up empty sessions
            if not session.users:
                del self.sessions[document.id]
            
            return True
        return False
    
    async def update_presence(
        self,
        document: Document,
        user: User,
        status: str
    ) -> UserPresence:
        """Update user presence status."""
        presence_key = f"{user.id}:{document.id}"
        if presence_key in self.presence:
            self.presence[presence_key].status = status
            self.presence[presence_key].last_seen = datetime.utcnow()
        else:
            self.presence[presence_key] = UserPresence(
                user_id=user.id,
                document_id=document.id,
                last_seen=datetime.utcnow(),
                status=status
            )
        return self.presence[presence_key]
    
    async def get_session_users(
        self,
        document: Document
    ) -> List[UserPresence]:
        """Get all users in a collaboration session."""
        return [
            presence for presence in self.presence.values()
            if presence.document_id == document.id
        ]
    
    async def apply_change(
        self,
        document: Document,
        user: User,
        change: Dict
    ) -> bool:
        """Apply a change to the document."""
        if document.id in self.sessions:
            session = self.sessions[document.id]
            if user.id in session.users:
                change["timestamp"] = datetime.utcnow().isoformat()
                change["user_id"] = user.id
                session.changes.append(change)
                session.last_activity = datetime.utcnow()
                return True
        return False
    
    async def get_changes(
        self,
        document: Document,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """Get changes since a specific timestamp."""
        if document.id in self.sessions:
            session = self.sessions[document.id]
            if since:
                return [
                    change for change in session.changes
                    if datetime.fromisoformat(change["timestamp"]) > since
                ]
            return session.changes
        return []
    
    async def cleanup_inactive_sessions(self, timeout: int = 300):
        """Clean up inactive collaboration sessions."""
        now = datetime.utcnow()
        inactive_sessions = [
            doc_id for doc_id, session in self.sessions.items()
            if (now - session.last_activity).total_seconds() > timeout
        ]
        
        for doc_id in inactive_sessions:
            del self.sessions[doc_id]
            
        # Clean up presence for inactive users
        inactive_presence = [
            key for key, presence in self.presence.items()
            if (now - presence.last_seen).total_seconds() > timeout
        ]
        
        for key in inactive_presence:
            del self.presence[key] 