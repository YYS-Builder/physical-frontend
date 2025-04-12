from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..services.versioning import VersioningService
from ..models.versioning import DocumentVersion, VersionList, VersionComparison
from ..auth.auth import get_current_user

router = APIRouter(prefix="/api/versions", tags=["versioning"])

@router.post("/{document_id}", response_model=DocumentVersion)
async def create_version(
    document_id: str,
    content: str,
    metadata: dict = None,
    current_user: str = Depends(get_current_user),
    versioning_service: VersioningService = Depends()
):
    """Create a new version of a document."""
    try:
        version = await versioning_service.create_version(
            document_id=document_id,
            content=content,
            metadata=metadata or {},
            created_by=current_user
        )
        return version
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}", response_model=VersionList)
async def get_versions(
    document_id: str,
    skip: int = 0,
    limit: int = 10,
    versioning_service: VersioningService = Depends()
):
    """Get all versions of a document."""
    try:
        versions = await versioning_service.get_versions(
            document_id=document_id,
            skip=skip,
            limit=limit
        )
        return versions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}/{version_id}", response_model=DocumentVersion)
async def get_version(
    document_id: str,
    version_id: str,
    versioning_service: VersioningService = Depends()
):
    """Get a specific version of a document."""
    try:
        version = await versioning_service.get_version(
            document_id=document_id,
            version_id=version_id
        )
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")
        return version
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{document_id}/{version_id}/restore")
async def restore_version(
    document_id: str,
    version_id: str,
    current_user: str = Depends(get_current_user),
    versioning_service: VersioningService = Depends()
):
    """Restore a document to a specific version."""
    try:
        await versioning_service.restore_version(
            document_id=document_id,
            version_id=version_id,
            restored_by=current_user
        )
        return {"message": "Version restored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}/compare", response_model=VersionComparison)
async def compare_versions(
    document_id: str,
    version1_id: str,
    version2_id: str,
    versioning_service: VersioningService = Depends()
):
    """Compare two versions of a document."""
    try:
        comparison = await versioning_service.compare_versions(
            document_id=document_id,
            version1_id=version1_id,
            version2_id=version2_id
        )
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 