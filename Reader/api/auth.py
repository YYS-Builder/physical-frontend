from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from config.database import get_db
from models.schemas import (
    UserCreate,
    User,
    Token,
    APIKey,
    APIKeyCreate,
    SuccessResponse
)
from utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_active_user,
    create_api_key,
    log_security_event
)
from .. import models, schemas, crud

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/register", response_model=User)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log security event
    log_security_event(
        "user_registered",
        user_id=db_user.id,
        details={"email": user.email}
    )
    
    return db_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    # Log security event
    log_security_event(
        "user_login",
        user_id=user.id,
        details={"email": user.email}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/api-keys", response_model=APIKey)
async def create_api_key_endpoint(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new API key."""
    from config.database import APIKey
    
    # Generate API key
    key = create_api_key()
    
    # Create API key record
    db_api_key = APIKey(
        user_id=current_user.id,
        key=key,
        name=api_key_data.name,
        description=api_key_data.description,
        expires_at=api_key_data.expires_at,
        is_active=True
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    # Log security event
    log_security_event(
        "api_key_created",
        user_id=current_user.id,
        details={"api_key_id": db_api_key.id}
    )
    
    return db_api_key

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information."""
    return current_user

@router.put("/me", response_model=User)
async def update_user(
    user_update: UserCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    # Update user data
    current_user.email = user_update.email
    current_user.hashed_password = get_password_hash(user_update.password)
    db.commit()
    db.refresh(current_user)
    
    # Log security event
    log_security_event(
        "user_updated",
        user_id=current_user.id,
        details={"email": user_update.email}
    )
    
    return current_user

@router.delete("/me", response_model=SuccessResponse)
async def delete_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete current user account."""
    # Log security event before deletion
    log_security_event(
        "user_deleted",
        user_id=current_user.id,
        details={"email": current_user.email}
    )
    
    # Delete user
    db.delete(current_user)
    db.commit()
    
    return {"message": "User deleted successfully"} 