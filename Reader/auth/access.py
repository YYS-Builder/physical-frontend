from typing import List, Optional, Set
from sqlalchemy.orm import Session
from . import logger, monitor, exceptions
from .. import models, schemas

class AccessControl:
    def __init__(self):
        self.logger = logger.logger
        self.role_permissions: Dict[str, Set[str]] = {
            "admin": {
                "manage_users",
                "manage_documents",
                "manage_collections",
                "view_analytics",
                "manage_settings"
            },
            "user": {
                "manage_own_documents",
                "manage_own_collections",
                "view_own_analytics"
            },
            "guest": {
                "view_public_documents",
                "view_public_collections"
            }
        }

    async def check_permission(
        self,
        db: Session,
        user_id: int,
        permission: str,
        resource_id: Optional[int] = None,
        resource_type: Optional[str] = None
    ) -> bool:
        """Check if a user has a specific permission."""
        try:
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if not user:
                return False

            # Check role-based permissions
            if user.role in self.role_permissions:
                if permission in self.role_permissions[user.role]:
                    return True

            # Check resource-specific permissions
            if resource_id and resource_type:
                if resource_type == "document":
                    document = db.query(models.Document).filter(models.Document.id == resource_id).first()
                    if document and document.owner_id == user_id:
                        return True
                elif resource_type == "collection":
                    collection = db.query(models.Collection).filter(models.Collection.id == resource_id).first()
                    if collection and collection.owner_id == user_id:
                        return True

            self.logger.warning(f"Permission denied: {user_id} - {permission}")
            monitor.track_request(0)  # Track permission check
            return False
        except Exception as e:
            self.logger.error(f"Error checking permission: {str(e)}")
            monitor.track_error("AccessControl", str(e))
            return False

    async def get_user_permissions(self, db: Session, user_id: int) -> Set[str]:
        """Get all permissions for a user."""
        try:
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if not user:
                return set()

            permissions = set()
            if user.role in self.role_permissions:
                permissions.update(self.role_permissions[user.role])

            self.logger.info(f"Retrieved permissions for user {user_id}")
            monitor.track_request(0)  # Track permissions retrieval
            return permissions
        except Exception as e:
            self.logger.error(f"Error getting permissions: {str(e)}")
            monitor.track_error("AccessControl", str(e))
            return set()

    async def grant_permission(
        self,
        db: Session,
        user_id: int,
        permission: str,
        resource_id: Optional[int] = None,
        resource_type: Optional[str] = None
    ) -> bool:
        """Grant a permission to a user."""
        try:
            # Check if permission exists
            if not any(permission in perms for perms in self.role_permissions.values()):
                return False

            # Create permission record
            permission_record = models.Permission(
                user_id=user_id,
                permission=permission,
                resource_id=resource_id,
                resource_type=resource_type
            )
            db.add(permission_record)
            db.commit()

            self.logger.info(f"Granted permission {permission} to user {user_id}")
            monitor.track_request(0)  # Track permission grant
            return True
        except Exception as e:
            self.logger.error(f"Error granting permission: {str(e)}")
            monitor.track_error("AccessControl", str(e))
            return False

    async def revoke_permission(
        self,
        db: Session,
        user_id: int,
        permission: str,
        resource_id: Optional[int] = None,
        resource_type: Optional[str] = None
    ) -> bool:
        """Revoke a permission from a user."""
        try:
            permission_record = db.query(models.Permission).filter(
                models.Permission.user_id == user_id,
                models.Permission.permission == permission,
                models.Permission.resource_id == resource_id,
                models.Permission.resource_type == resource_type
            ).first()

            if permission_record:
                db.delete(permission_record)
                db.commit()

                self.logger.info(f"Revoked permission {permission} from user {user_id}")
                monitor.track_request(0)  # Track permission revocation
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error revoking permission: {str(e)}")
            monitor.track_error("AccessControl", str(e))
            return False

# Create global access control instance
access_control = AccessControl() 