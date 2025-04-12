from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, crud
from ..auth import access_control, session_manager
from ..collections import manager, sharing, backup
from ..database import get_db

router = APIRouter()

@router.post("/collections/", response_model=schemas.Collection)
async def create_collection(
    collection: schemas.CollectionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Create a new collection."""
    return await manager.collection_manager.create_collection(
        db=db,
        collection=collection,
        user_id=current_user.id
    )

@router.get("/collections/{collection_id}", response_model=schemas.Collection)
async def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Get a collection by ID."""
    collection = await manager.collection_manager.get_collection(
        db=db,
        collection_id=collection_id,
        user_id=current_user.id
    )
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection

@router.put("/collections/{collection_id}", response_model=schemas.Collection)
async def update_collection(
    collection_id: int,
    collection: schemas.CollectionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Update a collection."""
    updated_collection = await manager.collection_manager.update_collection(
        db=db,
        collection_id=collection_id,
        collection=collection,
        user_id=current_user.id
    )
    if not updated_collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return updated_collection

@router.delete("/collections/{collection_id}")
async def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Delete a collection."""
    success = await manager.collection_manager.delete_collection(
        db=db,
        collection_id=collection_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Collection not found")
    return {"message": "Collection deleted successfully"}

@router.post("/collections/{collection_id}/documents/{document_id}")
async def add_document_to_collection(
    collection_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Add a document to a collection."""
    success = await manager.collection_manager.add_document_to_collection(
        db=db,
        collection_id=collection_id,
        document_id=document_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Collection or document not found")
    return {"message": "Document added to collection successfully"}

@router.delete("/collections/{collection_id}/documents/{document_id}")
async def remove_document_from_collection(
    collection_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Remove a document from a collection."""
    success = await manager.collection_manager.remove_document_from_collection(
        db=db,
        collection_id=collection_id,
        document_id=document_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Collection or document not found")
    return {"message": "Document removed from collection successfully"}

@router.post("/collections/{collection_id}/share/{user_id}")
async def share_collection(
    collection_id: int,
    user_id: int,
    permission: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Share a collection with another user."""
    success = await sharing.sharing_manager.share_collection(
        db=db,
        collection_id=collection_id,
        owner_id=current_user.id,
        shared_with_id=user_id,
        permission=permission
    )
    if not success:
        raise HTTPException(status_code=404, detail="Collection or user not found")
    return {"message": "Collection shared successfully"}

@router.delete("/collections/{collection_id}/share/{user_id}")
async def unshare_collection(
    collection_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Remove sharing of a collection with another user."""
    success = await sharing.sharing_manager.unshare_collection(
        db=db,
        collection_id=collection_id,
        owner_id=current_user.id,
        shared_with_id=user_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Collection or user not found")
    return {"message": "Collection unshared successfully"}

@router.get("/collections/shared", response_model=List[schemas.Collection])
async def get_shared_collections(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Get collections shared with the current user."""
    return await sharing.sharing_manager.get_shared_collections(
        db=db,
        user_id=current_user.id
    )

@router.post("/collections/{collection_id}/backup")
async def create_backup(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Create a backup of a collection."""
    backup_file = await backup.backup_manager.create_backup(
        db=db,
        collection_id=collection_id,
        user_id=current_user.id
    )
    if not backup_file:
        raise HTTPException(status_code=404, detail="Collection not found")
    return {"backup_file": backup_file}

@router.post("/collections/restore")
async def restore_backup(
    backup_file: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Restore a collection from backup."""
    collection = await backup.backup_manager.restore_backup(
        db=db,
        backup_file=backup_file,
        user_id=current_user.id
    )
    if not collection:
        raise HTTPException(status_code=404, detail="Backup file not found")
    return collection

@router.get("/collections/{collection_id}/backups")
async def list_backups(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """List available backups for a collection."""
    backups = await backup.backup_manager.list_backups(
        db=db,
        collection_id=collection_id,
        user_id=current_user.id
    )
    return {"backups": backups} 