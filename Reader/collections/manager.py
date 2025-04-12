from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .. import models, schemas, logger, monitor, exceptions
from ..auth import access_control

class CollectionManager:
    def __init__(self):
        self.logger = logger.logger

    async def create_collection(
        self,
        db: Session,
        user_id: int,
        collection_data: Dict[str, Any]
    ) -> schemas.Collection:
        """Create a new collection."""
        try:
            # Check permissions
            if not await access_control.check_permission(db, user_id, "manage_own_collections"):
                raise exceptions.AuthorizationError("Not authorized to create collections")

            # Create collection
            collection = models.Collection(
                owner_id=user_id,
                **collection_data
            )
            db.add(collection)
            db.commit()
            db.refresh(collection)

            self.logger.info(f"Created collection {collection.id} for user {user_id}")
            monitor.track_request(0)  # Track collection creation
            return schemas.Collection.from_orm(collection)
        except Exception as e:
            self.logger.error(f"Error creating collection: {str(e)}")
            monitor.track_error("Collection", str(e))
            raise

    async def get_collection(
        self,
        db: Session,
        collection_id: int,
        user_id: int
    ) -> Optional[schemas.Collection]:
        """Get a collection by ID."""
        try:
            collection = db.query(models.Collection).filter(
                models.Collection.id == collection_id
            ).first()

            if not collection:
                return None

            # Check permissions
            if collection.owner_id != user_id and not await access_control.check_permission(
                db, user_id, "view_public_collections"
            ):
                raise exceptions.AuthorizationError("Not authorized to view this collection")

            self.logger.info(f"Retrieved collection {collection_id}")
            monitor.track_request(0)  # Track collection retrieval
            return schemas.Collection.from_orm(collection)
        except Exception as e:
            self.logger.error(f"Error getting collection: {str(e)}")
            monitor.track_error("Collection", str(e))
            raise

    async def update_collection(
        self,
        db: Session,
        collection_id: int,
        user_id: int,
        collection_data: Dict[str, Any]
    ) -> Optional[schemas.Collection]:
        """Update a collection."""
        try:
            collection = db.query(models.Collection).filter(
                models.Collection.id == collection_id
            ).first()

            if not collection:
                return None

            # Check permissions
            if collection.owner_id != user_id and not await access_control.check_permission(
                db, user_id, "manage_collections"
            ):
                raise exceptions.AuthorizationError("Not authorized to update this collection")

            # Update collection
            for key, value in collection_data.items():
                setattr(collection, key, value)

            db.commit()
            db.refresh(collection)

            self.logger.info(f"Updated collection {collection_id}")
            monitor.track_request(0)  # Track collection update
            return schemas.Collection.from_orm(collection)
        except Exception as e:
            self.logger.error(f"Error updating collection: {str(e)}")
            monitor.track_error("Collection", str(e))
            raise

    async def delete_collection(
        self,
        db: Session,
        collection_id: int,
        user_id: int
    ) -> bool:
        """Delete a collection."""
        try:
            collection = db.query(models.Collection).filter(
                models.Collection.id == collection_id
            ).first()

            if not collection:
                return False

            # Check permissions
            if collection.owner_id != user_id and not await access_control.check_permission(
                db, user_id, "manage_collections"
            ):
                raise exceptions.AuthorizationError("Not authorized to delete this collection")

            db.delete(collection)
            db.commit()

            self.logger.info(f"Deleted collection {collection_id}")
            monitor.track_request(0)  # Track collection deletion
            return True
        except Exception as e:
            self.logger.error(f"Error deleting collection: {str(e)}")
            monitor.track_error("Collection", str(e))
            raise

    async def add_document_to_collection(
        self,
        db: Session,
        collection_id: int,
        document_id: int,
        user_id: int
    ) -> bool:
        """Add a document to a collection."""
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
                raise exceptions.AuthorizationError("Not authorized to modify this collection")

            # Check document permissions
            document = db.query(models.Document).filter(
                models.Document.id == document_id
            ).first()

            if not document:
                return False

            if document.owner_id != user_id and not await access_control.check_permission(
                db, user_id, "manage_documents"
            ):
                raise exceptions.AuthorizationError("Not authorized to add this document")

            # Add document to collection
            collection_doc = models.CollectionDocument(
                collection_id=collection_id,
                document_id=document_id
            )
            db.add(collection_doc)
            db.commit()

            self.logger.info(f"Added document {document_id} to collection {collection_id}")
            monitor.track_request(0)  # Track document addition
            return True
        except Exception as e:
            self.logger.error(f"Error adding document to collection: {str(e)}")
            monitor.track_error("Collection", str(e))
            raise

    async def remove_document_from_collection(
        self,
        db: Session,
        collection_id: int,
        document_id: int,
        user_id: int
    ) -> bool:
        """Remove a document from a collection."""
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
                raise exceptions.AuthorizationError("Not authorized to modify this collection")

            # Remove document from collection
            collection_doc = db.query(models.CollectionDocument).filter(
                models.CollectionDocument.collection_id == collection_id,
                models.CollectionDocument.document_id == document_id
            ).first()

            if collection_doc:
                db.delete(collection_doc)
                db.commit()

                self.logger.info(f"Removed document {document_id} from collection {collection_id}")
                monitor.track_request(0)  # Track document removal
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing document from collection: {str(e)}")
            monitor.track_error("Collection", str(e))
            raise

# Create global collection manager instance
collection_manager = CollectionManager() 