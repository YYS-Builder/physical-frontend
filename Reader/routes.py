from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import magic
import os

from . import crud, models, schemas
from .database import get_db
from .auth import get_current_active_user, create_access_token
from datetime import timedelta
from .config import settings

router = APIRouter()

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.email)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user

@router.post("/projects/", response_model=schemas.Project)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    return crud.create_project(db=db, project=project, user_id=current_user.id)

@router.get("/projects/", response_model=List[schemas.Project])
def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    projects = crud.get_user_projects(db, user_id=current_user.id, skip=skip, limit=limit)
    return projects

@router.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if db_project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    return db_project

@router.post("/documents/", response_model=schemas.Document)
def create_document(
    document: schemas.DocumentCreate,
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Validate project ownership
    project = crud.get_project(db, project_id=document.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add documents to this project"
        )

    # Handle file upload if present
    if file:
        # Validate file type
        file_type = magic.from_buffer(file.file.read(2048), mime=True)
        if file_type not in settings.ALLOWED_DOCUMENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_type} not allowed"
            )
        file.file.seek(0)

        # Save file
        file_path = os.path.join(settings.UPLOAD_DIR, f"{document.title}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        document.file_path = file_path

    return crud.create_document(db=db, document=document)

@router.put("/documents/{document_id}", response_model=schemas.Document)
def update_document(
    document_id: int,
    document: schemas.DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_document = crud.get_document(db, document_id=document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    project = crud.get_project(db, project_id=db_document.project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this document")
    return crud.update_document(db=db, document_id=document_id, document=document)

@router.get("/documents/", response_model=List[schemas.Document])
def read_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    documents = crud.get_documents(db, skip=skip, limit=limit)
    return documents

@router.get("/projects/{project_id}/documents/", response_model=List[schemas.Document])
def read_project_documents(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    project = crud.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project's documents")
    documents = crud.get_project_documents(db, project_id=project_id, skip=skip, limit=limit)
    return documents

@router.post("/reading-sessions/", response_model=schemas.ReadingSession)
def create_reading_session(
    session: schemas.ReadingSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    document = crud.get_document(db, document_id=session.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    project = crud.get_project(db, project_id=document.project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to read this document")
    return crud.create_reading_session(db=db, session=session, user_id=current_user.id)

@router.put("/reading-sessions/{session_id}", response_model=schemas.ReadingSession)
def update_reading_session(
    session_id: int,
    session: schemas.ReadingSessionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_session = crud.update_reading_session(db, session_id=session_id, session=session)
    if not db_session:
        raise HTTPException(status_code=404, detail="Reading session not found")
    if db_session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this session")
    return db_session

@router.get("/reading-sessions/", response_model=List[schemas.ReadingSession])
def read_user_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    sessions = crud.get_user_reading_sessions(db, user_id=current_user.id, skip=skip, limit=limit)
    return sessions

@router.get("/documents/{document_id}/reading-sessions/", response_model=List[schemas.ReadingSession])
def read_document_sessions(
    document_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    document = crud.get_document(db, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    project = crud.get_project(db, project_id=document.project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this document's sessions")
    sessions = crud.get_document_reading_sessions(db, document_id=document_id, skip=skip, limit=limit)
    return sessions

@router.get("/documents/{document_id}/progress", response_model=schemas.ReadingProgress)
def get_document_progress(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    document = crud.get_document(db, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    project = crud.get_project(db, project_id=document.project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this document's progress")
    progress = crud.get_reading_progress(db, document_id=document_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    return progress

@router.get("/documents/analytics/", response_model=List[schemas.DocumentAnalytics])
def get_document_analytics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get analytics for all documents"""
    return crud.get_document_analytics(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/documents/{document_id}/analytics/", response_model=schemas.DocumentAnalytics)
def get_document_analytics(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get analytics for a specific document"""
    document = crud.get_document(db, document_id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    project = crud.get_project(db, project_id=document.project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this document's analytics"
        )
    
    return crud.get_document_analytics(db, document_id=document_id) 