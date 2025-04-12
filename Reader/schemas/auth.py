from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

class APIKeyBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    expires_at: Optional[datetime] = None

class APIKeyCreate(APIKeyBase):
    pass

class APIKeyUpdate(APIKeyBase):
    pass

class APIKeyInDB(APIKeyBase):
    id: int
    user_id: int
    key: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 