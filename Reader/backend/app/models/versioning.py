from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class DocumentVersion(BaseModel):
    """Model for a document version."""
    version_id: str = Field(..., description="Unique identifier for the version")
    document_id: str = Field(..., description="ID of the document this version belongs to")
    content: str = Field(..., description="Content of the document version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the version")
    created_by: str = Field(..., description="User ID of the creator")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class VersionList(BaseModel):
    """Model for a list of document versions."""
    versions: List[DocumentVersion] = Field(..., description="List of document versions")
    total: int = Field(..., description="Total number of versions")

class VersionComparison(BaseModel):
    """Model for comparing two document versions."""
    version1: DocumentVersion = Field(..., description="First version to compare")
    version2: DocumentVersion = Field(..., description="Second version to compare")
    diff: str = Field(..., description="Diff between the two versions") 