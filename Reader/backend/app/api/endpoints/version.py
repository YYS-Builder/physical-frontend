from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.version import DocumentVersion, DocumentVersionCreate, VersionComparison, VersionList
from app.services.versioning import VersioningService
from app.database import get_db
from app.auth import get_current_user

router = APIRouter()

@router.post("/documents/{document_id}/versions", response_model=DocumentVersion)
async def create_version(
    document_id: str,
    version: DocumentVersionCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Create a new version of a document."""
    service = VersioningService(db)
    return service.create_version(document_id, version.content, version.metadata, current_user)

@router.get("/documents/{document_id}/versions", response_model=VersionList)
async def get_versions(
    document_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get all versions of a document."""
    service = VersioningService(db)
    versions = service.get_versions(document_id, skip, limit)
    return versions

@router.get("/documents/{document_id}/versions/{version_id}", response_model=DocumentVersion)
async def get_version(
    document_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get a specific version of a document."""
    service = VersioningService(db)
    version = service.get_version(document_id, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version

@router.post("/documents/{document_id}/versions/{version_id}/restore", response_model=DocumentVersion)
async def restore_version(
    document_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Restore a document to a specific version."""
    service = VersioningService(db)
    try:
        return service.restore_version(document_id, version_id, current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}/versions/compare", response_model=VersionComparison)
async def compare_versions(
    document_id: str,
    version1_id: str = Query(..., description="ID of the first version"),
    version2_id: str = Query(..., description="ID of the second version"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Compare two versions of a document."""
    service = VersioningService(db)
    try:
        return service.compare_versions(document_id, version1_id, version2_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 