from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from ..models.versioning import DocumentVersion, VersionList, VersionComparison
from ..services.versioning import VersioningService
from ..dependencies import get_current_user, get_versioning_service, get_db
from ..schemas.version import VersionCreate, VersionResponse, VersionDiff

router = APIRouter(prefix="/api/versioning", tags=["versioning"])

@router.post("/documents/{document_id}/versions", response_model=VersionResponse)
async def create_version(
    document_id: str,
    version: VersionCreate,
    db = Depends(get_db)
):
    """Create a new version of a document."""
    service = VersioningService(db)
    try:
        new_version = await service.create_version(
            document_id=document_id,
            content=version.content,
            metadata=version.metadata
        )
        return VersionResponse.from_orm(new_version)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/documents/{document_id}/versions", response_model=List[VersionResponse])
async def get_versions(
    document_id: str,
    db = Depends(get_db)
):
    """Get all versions of a document."""
    service = VersioningService(db)
    versions = await service.get_versions(document_id)
    return [VersionResponse.from_orm(v) for v in versions]

@router.get("/documents/{document_id}/versions/{version_id}", response_model=VersionResponse)
async def get_version(
    document_id: str,
    version_id: str,
    db = Depends(get_db)
):
    """Get a specific version of a document."""
    service = VersioningService(db)
    try:
        version = await service.get_version(document_id, version_id)
        return VersionResponse.from_orm(version)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/documents/{document_id}/versions/{version_id}/restore", response_model=VersionResponse)
async def restore_version(
    document_id: str,
    version_id: str,
    db = Depends(get_db)
):
    """Restore a specific version of a document."""
    service = VersioningService(db)
    try:
        new_version = await service.restore_version(document_id, version_id)
        return VersionResponse.from_orm(new_version)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/documents/{document_id}/versions/{version_id}/diff", response_model=VersionDiff)
async def compare_versions(
    document_id: str,
    version_id: str,
    compare_to: str,
    db = Depends(get_db)
):
    """Compare two versions of a document."""
    service = VersioningService(db)
    try:
        diff = await service.compare_versions(document_id, version_id, compare_to)
        return VersionDiff(diff=diff)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 