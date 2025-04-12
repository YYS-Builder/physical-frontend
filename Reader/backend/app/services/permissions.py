from typing import Dict, List, Optional
from pydantic import BaseModel
from app.models.document import Document
from app.models.user import User
from app.services.base import BaseService

class Permission(BaseModel):
    user_id: str
    document_id: str
    level: str  # "read", "write", "admin"
    granted_by: str
    granted_at: str

class ShareLink(BaseModel):
    document_id: str
    token: str
    expires_at: Optional[str]
    password: Optional[str]
    permission_level: str

class PermissionService(BaseService):
    def __init__(self):
        self.permissions: Dict[str, List[Permission]] = {}
        self.share_links: Dict[str, ShareLink] = {}
        
    async def grant_permission(
        self,
        document: Document,
        user: User,
        level: str,
        granted_by: User
    ) -> Permission:
        """Grant permission to a user for a document."""
        permission = Permission(
            user_id=user.id,
            document_id=document.id,
            level=level,
            granted_by=granted_by.id,
            granted_at=str(datetime.utcnow())
        )
        
        if document.id not in self.permissions:
            self.permissions[document.id] = []
        
        self.permissions[document.id].append(permission)
        return permission
    
    async def revoke_permission(
        self,
        document: Document,
        user: User
    ) -> bool:
        """Revoke a user's permission for a document."""
        if document.id in self.permissions:
            self.permissions[document.id] = [
                p for p in self.permissions[document.id]
                if p.user_id != user.id
            ]
            return True
        return False
    
    async def get_permissions(
        self,
        document: Document
    ) -> List[Permission]:
        """Get all permissions for a document."""
        return self.permissions.get(document.id, [])
    
    async def check_permission(
        self,
        document: Document,
        user: User,
        required_level: str
    ) -> bool:
        """Check if a user has the required permission level."""
        if document.id not in self.permissions:
            return False
            
        for permission in self.permissions[document.id]:
            if permission.user_id == user.id:
                return self._is_level_sufficient(
                    permission.level,
                    required_level
                )
        return False
    
    async def create_share_link(
        self,
        document: Document,
        permission_level: str,
        expires_at: Optional[str] = None,
        password: Optional[str] = None
    ) -> ShareLink:
        """Create a shareable link for a document."""
        token = self._generate_token()
        share_link = ShareLink(
            document_id=document.id,
            token=token,
            expires_at=expires_at,
            password=password,
            permission_level=permission_level
        )
        
        self.share_links[token] = share_link
        return share_link
    
    async def validate_share_link(
        self,
        token: str,
        password: Optional[str] = None
    ) -> Optional[ShareLink]:
        """Validate a share link and return the associated permission level."""
        if token not in self.share_links:
            return None
            
        share_link = self.share_links[token]
        
        # Check expiration
        if share_link.expires_at and datetime.fromisoformat(share_link.expires_at) < datetime.utcnow():
            return None
            
        # Check password
        if share_link.password and share_link.password != password:
            return None
            
        return share_link
    
    def _is_level_sufficient(self, user_level: str, required_level: str) -> bool:
        """Check if a user's permission level is sufficient."""
        level_hierarchy = {
            "admin": 3,
            "write": 2,
            "read": 1
        }
        return level_hierarchy.get(user_level, 0) >= level_hierarchy.get(required_level, 0)
    
    def _generate_token(self) -> str:
        """Generate a unique token for share links."""
        return secrets.token_urlsafe(32) 