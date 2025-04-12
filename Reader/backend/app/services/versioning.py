from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.version import DocumentVersion
from ..schemas.version import VersionCreate, VersionResponse, VersionDiff
import uuid
from datetime import datetime
import difflib

class VersioningService:
    def __init__(self, db: Session):
        self.db = db

    def create_version(self, document_id: str, version: VersionCreate, user_id: str) -> VersionResponse:
        # Get the latest version number
        latest_version = self.db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id
        ).order_by(DocumentVersion.version_number.desc()).first()

        version_number = 1 if not latest_version else latest_version.version_number + 1

        # Create new version
        db_version = DocumentVersion(
            id=str(uuid.uuid4()),
            document_id=document_id,
            version_number=version_number,
            content=version.content,
            metadata=version.metadata or {},
            created_at=datetime.utcnow(),
            created_by=user_id
        )

        self.db.add(db_version)
        self.db.commit()
        self.db.refresh(db_version)

        return VersionResponse.from_orm(db_version)

    def get_versions(self, document_id: str, skip: int = 0, limit: int = 10) -> List[VersionResponse]:
        versions = self.db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id
        ).order_by(DocumentVersion.version_number.desc()).offset(skip).limit(limit).all()

        return [VersionResponse.from_orm(version) for version in versions]

    def get_version(self, document_id: str, version_id: str) -> Optional[VersionResponse]:
        version = self.db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id,
            DocumentVersion.id == version_id
        ).first()

        return VersionResponse.from_orm(version) if version else None

    def restore_version(self, document_id: str, version_id: str, user_id: str) -> VersionResponse:
        # Get the version to restore
        version = self.db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id,
            DocumentVersion.id == version_id
        ).first()

        if not version:
            raise ValueError("Version not found")

        # Create a new version with the restored content
        return self.create_version(
            document_id=document_id,
            version=VersionCreate(
                content=version.content,
                metadata=version.metadata
            ),
            user_id=user_id
        )

    def compare_versions(self, document_id: str, version_id1: str, version_id2: str) -> VersionDiff:
        # Get both versions
        version1 = self.db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id,
            DocumentVersion.id == version_id1
        ).first()

        version2 = self.db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id,
            DocumentVersion.id == version_id2
        ).first()

        if not version1 or not version2:
            raise ValueError("One or both versions not found")

        # Generate diff
        diff = difflib.unified_diff(
            version1.content.splitlines(),
            version2.content.splitlines(),
            lineterm=''
        )

        return VersionDiff(diff='\n'.join(diff)) 