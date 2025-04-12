from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.version import Version
from ..schemas.version import VersionCreate, VersionResponse, VersionDiff
from ..utils.diff import generate_diff

class VersionService:
    def __init__(self, db: Session):
        self.db = db

    def create_version(self, document_id: str, version: VersionCreate, user_id: str) -> VersionResponse:
        # Get the latest version number
        latest_version = self.db.query(Version).filter(
            Version.document_id == document_id
        ).order_by(Version.version_number.desc()).first()
        
        version_number = 1 if not latest_version else latest_version.version_number + 1
        
        # Create new version
        db_version = Version(
            document_id=document_id,
            version_number=version_number,
            content=version.content,
            metadata=version.metadata,
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        self.db.add(db_version)
        self.db.commit()
        self.db.refresh(db_version)
        
        return VersionResponse.from_orm(db_version)

    def get_versions(self, document_id: str, skip: int = 0, limit: int = 10) -> List[VersionResponse]:
        versions = self.db.query(Version).filter(
            Version.document_id == document_id
        ).order_by(Version.version_number.desc()).offset(skip).limit(limit).all()
        
        return [VersionResponse.from_orm(version) for version in versions]

    def get_version(self, document_id: str, version_id: str) -> Optional[VersionResponse]:
        version = self.db.query(Version).filter(
            Version.document_id == document_id,
            Version.id == version_id
        ).first()
        
        return VersionResponse.from_orm(version) if version else None

    def restore_version(self, document_id: str, version_id: str) -> VersionResponse:
        version = self.db.query(Version).filter(
            Version.document_id == document_id,
            Version.id == version_id
        ).first()
        
        if not version:
            raise ValueError("Version not found")
            
        # Create a new version with the restored content
        new_version = Version(
            document_id=document_id,
            version_number=version.version_number + 1,
            content=version.content,
            metadata=version.metadata,
            created_by=version.created_by,
            created_at=datetime.utcnow()
        )
        
        self.db.add(new_version)
        self.db.commit()
        self.db.refresh(new_version)
        
        return VersionResponse.from_orm(new_version)

    def compare_versions(self, document_id: str, version1_id: str, version2_id: str) -> VersionDiff:
        version1 = self.db.query(Version).filter(
            Version.document_id == document_id,
            Version.id == version1_id
        ).first()
        
        version2 = self.db.query(Version).filter(
            Version.document_id == document_id,
            Version.id == version2_id
        ).first()
        
        if not version1 or not version2:
            raise ValueError("One or both versions not found")
            
        diff = generate_diff(version1.content, version2.content)
        
        return VersionDiff(
            diff=diff,
            version1_id=version1_id,
            version2_id=version2_id,
            document_id=document_id
        ) 