from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from . import models, schemas
from .auth import get_password_hash

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate, user_id: int):
    db_project = models.Project(**project.dict(), owner_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_user_projects(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Project).filter(models.Project.owner_id == user_id).offset(skip).limit(limit).all()

def create_document(db: Session, document: schemas.DocumentCreate):
    db_document = models.Document(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def update_document(db: Session, document_id: int, document: schemas.DocumentUpdate):
    db_document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not db_document:
        return None
    
    update_data = document.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_document, key, value)
    
    # Update reading progress if current_page or total_pages changed
    if "current_page" in update_data or "total_pages" in update_data:
        if db_document.total_pages and db_document.current_page:
            db_document.reading_progress = (db_document.current_page / db_document.total_pages) * 100
    
    db.commit()
    db.refresh(db_document)
    return db_document

def get_documents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Document).offset(skip).limit(limit).all()

def get_project_documents(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Document).filter(models.Document.project_id == project_id).offset(skip).limit(limit).all()

def get_document(db: Session, document_id: int):
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def create_reading_session(db: Session, session: schemas.ReadingSessionCreate, user_id: int):
    db_session = models.ReadingSession(**session.dict(), user_id=user_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_reading_session(db: Session, session_id: int, session: schemas.ReadingSessionUpdate):
    db_session = db.query(models.ReadingSession).filter(models.ReadingSession.id == session_id).first()
    if not db_session:
        return None
    
    update_data = session.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_session, key, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session

def get_user_reading_sessions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ReadingSession).filter(models.ReadingSession.user_id == user_id).offset(skip).limit(limit).all()

def get_document_reading_sessions(db: Session, document_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ReadingSession).filter(models.ReadingSession.document_id == document_id).offset(skip).limit(limit).all()

def get_reading_progress(db: Session, document_id: int):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        return None
    
    last_session = db.query(models.ReadingSession).filter(
        models.ReadingSession.document_id == document_id
    ).order_by(models.ReadingSession.start_time.desc()).first()
    
    return schemas.ReadingProgress(
        document_id=document.id,
        current_page=document.current_page,
        total_pages=document.total_pages,
        reading_progress=document.reading_progress,
        last_read=last_session.start_time if last_session else document.created_at
    )

def get_document_analytics(db: Session, document_id: int) -> Optional[schemas.DocumentAnalytics]:
    """Calculate analytics for a specific document."""
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        return None

    # Get all reading sessions for this document
    sessions = db.query(models.ReadingSession).filter(
        models.ReadingSession.document_id == document_id
    ).all()

    if not sessions:
        return schemas.DocumentAnalytics(
            document_id=document_id,
            total_sessions=0,
            total_duration_minutes=0,
            total_pages_read=0,
            average_session_duration=0,
            average_pages_per_session=0,
            last_read=None,
            reading_speed_pages_per_hour=0,
            completion_percentage=0
        )

    total_duration = sum(session.duration_minutes for session in sessions)
    total_pages = sum(session.pages_read for session in sessions)
    total_sessions = len(sessions)

    # Calculate averages
    avg_duration = total_duration / total_sessions
    avg_pages = total_pages / total_sessions

    # Calculate reading speed (pages per hour)
    reading_speed = (total_pages / total_duration) * 60 if total_duration > 0 else 0

    # Get last read time
    last_read = max(session.end_time for session in sessions)

    # Calculate completion percentage
    completion = (total_pages / document.total_pages) * 100 if document.total_pages > 0 else 0

    return schemas.DocumentAnalytics(
        document_id=document_id,
        total_sessions=total_sessions,
        total_duration_minutes=total_duration,
        total_pages_read=total_pages,
        average_session_duration=avg_duration,
        average_pages_per_session=avg_pages,
        last_read=last_read,
        reading_speed_pages_per_hour=reading_speed,
        completion_percentage=completion
    )

def get_all_document_analytics(db: Session, user_id: int) -> List[schemas.DocumentAnalytics]:
    """Get analytics for all documents owned by a user."""
    documents = db.query(models.Document).filter(models.Document.owner_id == user_id).all()
    return [get_document_analytics(db, doc.id) for doc in documents if get_document_analytics(db, doc.id)] 