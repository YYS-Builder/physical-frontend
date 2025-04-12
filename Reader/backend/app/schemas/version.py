from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class DocumentVersionBase(BaseModel):
    """Base schema for document version."""
    document_id: str = Field(..., description="ID of the document")
    version_number: int = Field(..., description="Version number")
    content: str = Field(..., description="Content of the document version")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Metadata associated with the version")

class DocumentVersionCreate(DocumentVersionBase):
    """Schema for creating a new document version."""
    created_by: str = Field(..., description="ID of the user creating the version")

class DocumentVersion(DocumentVersionBase):
    """Schema for document version response."""
    id: str = Field(..., description="Unique identifier for the version")
    created_by: str = Field(..., description="ID of the user who created the version")
    created_at: datetime = Field(..., description="Timestamp when the version was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the version was last updated")

    class Config:
        orm_mode = True

class VersionComparison(BaseModel):
    """Schema for version comparison results."""
    version1_id: str = Field(..., description="ID of the first version")
    version2_id: str = Field(..., description="ID of the second version")
    content_diff: List[str] = Field(..., description="Differences in content between versions")
    metadata_diff: Dict[str, Dict[str, str]] = Field(..., description="Differences in metadata between versions")

class VersionList(BaseModel):
    """Schema for list of document versions."""
    versions: List[DocumentVersion] = Field(..., description="List of document versions")
    total: int = Field(..., description="Total number of versions")
    skip: int = Field(..., description="Number of versions skipped")
    limit: int = Field(..., description="Maximum number of versions returned")

class VersionBase(BaseModel):
    content: str
    metadata: Optional[dict] = None

class VersionCreate(VersionBase):
    pass

class VersionResponse(VersionBase):
    id: str
    document_id: str
    version_number: int
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class VersionDiff(BaseModel):
    version1_id: str
    version2_id: str
    diff: str
    changes: List[str] = Field(default_factory=list) 