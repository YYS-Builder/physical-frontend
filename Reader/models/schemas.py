from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8)

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class APIKeyBase(BaseModel):
    name: str
    description: Optional[str] = None
    expires_at: Optional[datetime] = None

class APIKeyCreate(APIKeyBase):
    pass

class APIKey(APIKeyBase):
    id: int
    user_id: int
    key: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CollectionBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False

class CollectionCreate(CollectionBase):
    pass

class Collection(CollectionBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ImageBase(BaseModel):
    filename: str
    metadata: Optional[dict] = None

class ImageCreate(ImageBase):
    collection_id: int

class Image(ImageBase):
    id: int
    original_path: str
    processed_path: Optional[str]
    collection_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ProcessingJobBase(BaseModel):
    image_id: int
    job_type: str

class EmbedJobCreate(ProcessingJobBase):
    data: str
    job_type: str = "embed"

class ExtractJobCreate(ProcessingJobBase):
    job_type: str = "extract"

class ProcessingJob(ProcessingJobBase):
    id: int
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class HealthCheck(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

class SuccessResponse(BaseModel):
    message: str 