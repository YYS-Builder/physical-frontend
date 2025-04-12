from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path
from sqlalchemy.orm import Session
from .. import models, schemas, logger, monitor, exceptions, storage
from ..auth import access_control

class BackupManager:
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.logger = logger.logger

    async def create_backup(
        self,
        db: Session,
        collection_id: int,
        user_id: int
    ) -> Optional[str]:
        """Create a backup of a collection."""
        try:
            # Check collection permissions
            collection = db.query(models.Collection).filter(
                models.Collection.id == collection_id
            ).first()

            if not collection:
                return None

            if collection.owner_id != user_id and not await access_control.check_permission(
                db, user_id, "manage_collections"
            ):
                raise exceptions.AuthorizationError("Not authorized to backup this collection")

            # Get collection data
            collection_data = {
                "id": collection.id,
                "name": collection.name,
                "description": collection.description,
                "created_at": collection.created_at.isoformat(),
                "updated_at": collection.updated_at.isoformat(),
                "owner_id": collection.owner_id,
                "documents": []
            }

            # Get collection documents
            documents = db.query(models.Document).join(
                models.CollectionDocument
            ).filter(
                models.CollectionDocument.collection_id == collection_id
            ).all()

            for document in documents:
                document_data = {
                    "id": document.id,
                    "title": document.title,
                    "description": document.description,
                    "file_path": document.file_path,
                    "file_size": document.file_size,
                    "created_at": document.created_at.isoformat(),
                    "updated_at": document.updated_at.isoformat()
                }
                collection_data["documents"].append(document_data)

            # Create backup file
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"collection_{collection_id}_{timestamp}.json"
            
            with open(backup_file, "w") as f:
                json.dump(collection_data, f, indent=2)

            self.logger.info(f"Created backup for collection {collection_id}")
            monitor.track_request(0)  # Track backup creation
            return str(backup_file)
        except Exception as e:
            self.logger.error(f"Error creating backup: {str(e)}")
            monitor.track_error("Backup", str(e))
            raise

    async def restore_backup(
        self,
        db: Session,
        backup_file: str,
        user_id: int
    ) -> Optional[schemas.Collection]:
        """Restore a collection from backup."""
        try:
            # Check if backup file exists
            backup_path = Path(backup_file)
            if not backup_path.exists():
                return None

            # Load backup data
            with open(backup_path, "r") as f:
                backup_data = json.load(f)

            # Create or update collection
            collection = db.query(models.Collection).filter(
                models.Collection.id == backup_data["id"]
            ).first()

            if collection:
                # Update existing collection
                if collection.owner_id != user_id and not await access_control.check_permission(
                    db, user_id, "manage_collections"
                ):
                    raise exceptions.AuthorizationError("Not authorized to restore this collection")

                collection.name = backup_data["name"]
                collection.description = backup_data["description"]
            else:
                # Create new collection
                collection = models.Collection(
                    id=backup_data["id"],
                    name=backup_data["name"],
                    description=backup_data["description"],
                    owner_id=user_id
                )
                db.add(collection)

            db.commit()
            db.refresh(collection)

            # Restore documents
            for doc_data in backup_data["documents"]:
                document = db.query(models.Document).filter(
                    models.Document.id == doc_data["id"]
                ).first()

                if not document:
                    document = models.Document(
                        id=doc_data["id"],
                        title=doc_data["title"],
                        description=doc_data["description"],
                        file_path=doc_data["file_path"],
                        file_size=doc_data["file_size"],
                        owner_id=user_id
                    )
                    db.add(document)

                # Add to collection
                collection_doc = db.query(models.CollectionDocument).filter(
                    models.CollectionDocument.collection_id == collection.id,
                    models.CollectionDocument.document_id == document.id
                ).first()

                if not collection_doc:
                    collection_doc = models.CollectionDocument(
                        collection_id=collection.id,
                        document_id=document.id
                    )
                    db.add(collection_doc)

            db.commit()

            self.logger.info(f"Restored collection from backup {backup_file}")
            monitor.track_request(0)  # Track backup restoration
            return schemas.Collection.from_orm(collection)
        except Exception as e:
            self.logger.error(f"Error restoring backup: {str(e)}")
            monitor.track_error("Backup", str(e))
            raise

    async def list_backups(
        self,
        db: Session,
        collection_id: int,
        user_id: int
    ) -> List[str]:
        """List available backups for a collection."""
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
                raise exceptions.AuthorizationError("Not authorized to list backups for this collection")

            # List backup files
            backups = []
            for file in self.backup_dir.glob(f"collection_{collection_id}_*.json"):
                backups.append(str(file))

            self.logger.info(f"Listed backups for collection {collection_id}")
            monitor.track_request(0)  # Track backup listing
            return backups
        except Exception as e:
            self.logger.error(f"Error listing backups: {str(e)}")
            monitor.track_error("Backup", str(e))
            raise

# Create global backup manager instance
backup_manager = BackupManager() 