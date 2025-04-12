from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from ..services.versioning import VersioningService
from ..models.versioning import DocumentVersion, VersionList, VersionComparison
from ..dependencies import get_versioning_service

router = APIRouter(prefix="/documents/{document_id}/versions", tags=["versioning"])

@router.post("", response_model=DocumentVersion)
async def create_version(
    document_id: str,
    content: str,
    metadata: dict,
    created_by: str,
    versioning_service: VersioningService = Depends(get_versioning_service)
):
    """Create a new version of a document."""
    return await versioning_service.create_version(
        document_id=document_id,
        content=content,
        metadata=metadata,
        created_by=created_by
    )

@router.get("", response_model=VersionList)
async def get_versions(
    document_id: str,
    skip: int = 0,
    limit: int = 10,
    versioning_service: VersioningService = Depends(get_versioning_service)
):
    """Get all versions of a document."""
    return await versioning_service.get_versions(
        document_id=document_id,
        skip=skip,
        limit=limit
    )

@router.get("/{version_id}", response_model=DocumentVersion)
async def get_version(
    document_id: str,
    version_id: str,
    versioning_service: VersioningService = Depends(get_versioning_service)
):
    """Get a specific version of a document."""
    version = await versioning_service.get_version(
        document_id=document_id,
        version_id=version_id
    )
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version

@router.post("/{version_id}/restore", response_model=DocumentVersion)
async def restore_version(
    document_id: str,
    version_id: str,
    created_by: str,
    versioning_service: VersioningService = Depends(get_versioning_service)
):
    """Restore a document to a specific version."""
    return await versioning_service.restore_version(
        document_id=document_id,
        version_id=version_id,
        created_by=created_by
    )

@router.get("/{version_id}/compare/{other_version_id}", response_model=VersionComparison)
async def compare_versions(
    document_id: str,
    version_id: str,
    other_version_id: str,
    versioning_service: VersioningService = Depends(get_versioning_service)
):
    """Compare two versions of a document."""
    return await versioning_service.compare_versions(
        document_id=document_id,
        version_id=version_id,
        other_version_id=other_version_id
    ) 