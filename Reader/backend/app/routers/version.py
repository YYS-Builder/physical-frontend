from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.version import VersionService
from ..schemas.version import VersionCreate, VersionResponse, VersionDiff
from ..auth import get_current_user

router = APIRouter(prefix="/versions", tags=["versions"])

@router.post("/{document_id}", response_model=VersionResponse)
def create_version(
    document_id: str,
    version: VersionCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    service = VersionService(db)
    return service.create_version(document_id, version, current_user)

@router.get("/{document_id}", response_model=List[VersionResponse])
def get_versions(
    document_id: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    service = VersionService(db)
    return service.get_versions(document_id, skip, limit)

@router.get("/{document_id}/{version_id}", response_model=VersionResponse)
def get_version(
    document_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    service = VersionService(db)
    version = service.get_version(document_id, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version

@router.post("/{document_id}/{version_id}/restore", response_model=VersionResponse)
def restore_version(
    document_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    service = VersionService(db)
    try:
        return service.restore_version(document_id, version_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{document_id}/compare", response_model=VersionDiff)
def compare_versions(
    document_id: str,
    version1_id: str,
    version2_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    service = VersionService(db)
    try:
        return service.compare_versions(document_id, version1_id, version2_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 