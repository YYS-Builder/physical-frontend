from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.auth import User, APIKey
from ..schemas.auth import UserCreate, UserUpdate, APIKeyCreate, APIKeyUpdate
from ..utils.auth import get_password_hash, verify_password, create_access_token
from ..utils.security import generate_api_key

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user: UserCreate) -> User:
        db_user = User(
            email=user.email,
            hashed_password=get_password_hash(user.password),
            is_active=user.is_active,
            is_superuser=user.is_superuser
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, user_id: int, user: UserUpdate) -> User:
        db_user = self.get_user(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = user.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token_for_user(self, user: User) -> str:
        return create_access_token(data={"sub": user.id})

    def get_api_key(self, api_key_id: int) -> Optional[APIKey]:
        return self.db.query(APIKey).filter(APIKey.id == api_key_id).first()

    def get_api_key_by_key(self, key: str) -> Optional[APIKey]:
        return self.db.query(APIKey).filter(APIKey.key == key).first()

    def create_api_key(self, user_id: int, api_key: APIKeyCreate) -> APIKey:
        db_api_key = APIKey(
            user_id=user_id,
            name=api_key.name,
            key=generate_api_key(),
            description=api_key.description,
            is_active=api_key.is_active,
            expires_at=api_key.expires_at
        )
        self.db.add(db_api_key)
        self.db.commit()
        self.db.refresh(db_api_key)
        return db_api_key

    def update_api_key(self, api_key_id: int, api_key: APIKeyUpdate) -> APIKey:
        db_api_key = self.get_api_key(api_key_id)
        if not db_api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        update_data = api_key.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_api_key, key, value)
        
        self.db.commit()
        self.db.refresh(db_api_key)
        return db_api_key

    def delete_api_key(self, api_key_id: int) -> None:
        db_api_key = self.get_api_key(api_key_id)
        if not db_api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        self.db.delete(db_api_key)
        self.db.commit() 