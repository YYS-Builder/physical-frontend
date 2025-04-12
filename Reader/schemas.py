from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class DocumentBase(BaseModel):
    title: str
    content: str
    total_pages: Optional[int] = None

class DocumentCreate(DocumentBase):
    project_id: int

class Document(DocumentBase):
    id: int
    project_id: int
    current_page: int
    reading_progress: float
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    current_page: Optional[int] = None
    total_pages: Optional[int] = None

class ReadingSessionBase(BaseModel):
    document_id: int
    notes: Optional[str] = None

class ReadingSessionCreate(ReadingSessionBase):
    pass

class ReadingSession(ReadingSessionBase):
    id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[int]
    pages_read: int

    class Config:
        orm_mode = True

class ReadingSessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    pages_read: Optional[int] = None
    notes: Optional[str] = None

class ReadingProgress(BaseModel):
    document_id: int
    current_page: int
    total_pages: int
    reading_progress: float
    last_read: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class DocumentAnalytics(BaseModel):
    document_id: int
    total_sessions: int
    total_duration_minutes: int
    total_pages_read: int
    average_session_duration: float
    average_pages_per_session: float
    last_read: Optional[datetime]
    reading_speed_pages_per_hour: float
    completion_percentage: float

    class Config:
        orm_mode = True 