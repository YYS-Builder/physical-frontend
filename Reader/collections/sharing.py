from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .. import models, schemas, logger, monitor, exceptions
from ..auth import access_control

class SharingManager:
    def __init__(self):
        self.logger = logger.logger

    async def share_collection(
        self,
        db: Session,
        collection_id: int,
        user_id: int,
        target_user_id: int,
        permission: str
    ) -> bool:
        """Share a collection with another user."""
        try:
            # Check collection permissions
            collection = db.query(models.Collection).filter(
                models.Collection.id == collection_id
            ).first()

            if not collection:
                return False

            if collection.owner_id != user_id and not await access_control.check_permission(
                db, user_id, "manage_collections"
            ):
                raise exceptions.AuthorizationError("Not authorized to share this collection")

            # Check if sharing already exists
            existing_share = db.query(models.CollectionShare).filter(
                models.CollectionShare.collection_id == collection_id,
                models.CollectionShare.user_id == target_user_id
            ).first()

            if existing_share:
                # Update existing share
                existing_share.permission = permission
            else:
                # Create new share
                share = models.CollectionShare(
                    collection_id=collection_id,
                    user_id=target_user_id,
                    permission=permission
                )
                db.add(share)

            db.commit()

            self.logger.info(f"Shared collection {collection_id} with user {target_user_id}")
            monitor.track_request(0)  # Track sharing operation
            return True
        except Exception as e:
            self.logger.error(f"Error sharing collection: {str(e)}")
            monitor.track_error("Sharing", str(e))
            raise

    async def unshare_collection(
        self,
        db: Session,
        collection_id: int,
        user_id: int,
        target_user_id: int
    ) -> bool:
        """Remove sharing of a collection with another user."""
        try:
            # Check collection permissions
            collection = db.query(models.Collection).filter(
                models.Collection.id == collection_id
            ).first()

            if not collection:
                return False

            if collection.owner_id != user_id and not await access_control.check_permission(
                db, user_id, "manage_collections"
            ):
                raise exceptions.AuthorizationError("Not authorized to unshare this collection")

            # Remove share
            share = db.query(models.CollectionShare).filter(
                models.CollectionShare.collection_id == collection_id,
                models.CollectionShare.user_id == target_user_id
            ).first()

            if share:
                db.delete(share)
                db.commit()

                self.logger.info(f"Unshared collection {collection_id} from user {target_user_id}")
                monitor.track_request(0)  # Track unsharing operation
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error unsharing collection: {str(e)}")
            monitor.track_error("Sharing", str(e))
            raise

    async def get_shared_collections(
        self,
        db: Session,
        user_id: int
    ) -> List[schemas.Collection]:
        """Get collections shared with a user."""
        try:
            shares = db.query(models.CollectionShare).filter(
                models.CollectionShare.user_id == user_id
            ).all()

            collections = []
            for share in shares:
                collection = db.query(models.Collection).filter(
                    models.Collection.id == share.collection_id
                ).first()
                if collection:
                    collections.append(schemas.Collection.from_orm(collection))

            self.logger.info(f"Retrieved shared collections for user {user_id}")
            monitor.track_request(0)  # Track shared collections retrieval
            return collections
        except Exception as e:
            self.logger.error(f"Error getting shared collections: {str(e)}")
            monitor.track_error("Sharing", str(e))
            raise

    async def get_collection_shares(
        self,
        db: Session,
        collection_id: int,
        user_id: int
    ) -> List[schemas.CollectionShare]:
        """Get users a collection is shared with."""
        try:
            # Check collection permissions
            collection = db.query(models.Collection).filter(
                models.Collection.id == collection_id
            ).first()

            if not collection:
                return []

            if collection.owner_id != user_id and not await access_control.check_permission(
                db, user_id, "manage_collections"
            ):
                raise exceptions.AuthorizationError("Not authorized to view collection shares")

            shares = db.query(models.CollectionShare).filter(
                models.CollectionShare.collection_id == collection_id
            ).all()

            self.logger.info(f"Retrieved shares for collection {collection_id}")
            monitor.track_request(0)  # Track shares retrieval
            return [schemas.CollectionShare.from_orm(share) for share in shares]
        except Exception as e:
            self.logger.error(f"Error getting collection shares: {str(e)}")
            monitor.track_error("Sharing", str(e))
            raise

# Create global sharing manager instance
sharing_manager = SharingManager() 