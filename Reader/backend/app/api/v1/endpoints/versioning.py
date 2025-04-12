from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.versioning import VersioningService
from app.schemas.version import DocumentVersion, VersionComparison
from app.core.auth import get_current_user

router = APIRouter()
versioning_service = VersioningService()

@router.post("/documents/{document_id}/versions", response_model=DocumentVersion)
async def create_version(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Create a new version of a document."""
    try:
        version = versioning_service.create_version(db, document_id, current_user)
        return version
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}/versions", response_model=List[DocumentVersion])
async def get_versions(
    document_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get all versions of a document."""
    try:
        versions = versioning_service.get_versions(db, document_id, skip, limit)
        return versions
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}/versions/{version_id}", response_model=DocumentVersion)
async def get_version(
    document_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get a specific version of a document."""
    try:
        version = versioning_service.get_version(db, document_id, version_id)
        return version
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/versions/{version_id}/restore", response_model=DocumentVersion)
async def restore_version(
    document_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Restore a document to a specific version."""
    try:
        version = versioning_service.restore_version(db, document_id, version_id, current_user)
        return version
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}/versions/compare", response_model=VersionComparison)
async def compare_versions(
    document_id: str,
    version1_id: str,
    version2_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Compare two versions of a document."""
    try:
        comparison = versioning_service.compare_versions(db, document_id, version1_id, version2_id)
        return comparison
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 