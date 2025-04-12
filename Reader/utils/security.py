from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import logging

from config.database import get_db
from models.schemas import TokenData
from config.database import User

# Configure logging
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

def create_api_key() -> str:
    """Generate a new API key."""
    # Generate a secure random string
    import secrets
    return secrets.token_urlsafe(32)

def verify_api_key(api_key: str, db: Session) -> Optional[User]:
    """Verify an API key and return the associated user."""
    from config.database import APIKey
    api_key_obj = db.query(APIKey).filter(
        APIKey.key == api_key,
        APIKey.is_active == True,
        APIKey.expires_at > datetime.utcnow()
    ).first()
    
    if not api_key_obj:
        return None
        
    return db.query(User).filter(User.id == api_key_obj.user_id).first()

def log_security_event(
    event_type: str,
    user_id: Optional[int] = None,
    details: Optional[dict] = None
) -> None:
    """Log a security-related event."""
    from config.database import AuditLog
    db = next(get_db())
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=event_type,
            resource_type="security",
            resource_id=0,
            details=details
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        logger.error(f"Error logging security event: {e}")
        db.rollback()
    finally:
        db.close() 