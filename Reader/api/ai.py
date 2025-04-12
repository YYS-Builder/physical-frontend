from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from .. import models, schemas
from ..ai.interface import ai_pipeline
from ..auth import session_manager
from ..database import get_db

router = APIRouter()

@router.post("/documents/{document_id}/process")
async def process_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Process a document using AI."""
    # Get document from database
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Process document through AI pipeline
    result = await ai_pipeline.process_new_document(document)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {result['error']}"
        )
    
    # Update document in database
    document.analysis = result["analysis"]
    document.embeddings = result["embeddings"]
    db.commit()
    
    return result

@router.get("/documents/{document_id}/analysis")
async def get_document_analysis(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Get AI analysis for a document."""
    # Get document from database
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not document.analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document analysis not available"
        )
    
    return document.analysis

@router.post("/analytics/{analytics_id}/analyze")
async def analyze_reading_session(
    analytics_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Analyze a reading session using AI."""
    # Get analytics from database
    analytics = db.query(models.DocumentAnalytics).filter(
        models.DocumentAnalytics.id == analytics_id,
        models.DocumentAnalytics.user_id == current_user.id
    ).first()
    
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analytics not found"
        )
    
    # Analyze reading session through AI pipeline
    result = await ai_pipeline.analyze_reading_session(analytics)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing reading session: {result['error']}"
        )
    
    # Update analytics in database
    analytics.patterns = result["patterns"]
    analytics.recommendations = result["recommendations"]
    db.commit()
    
    return result

@router.get("/analytics/{analytics_id}/insights")
async def get_reading_insights(
    analytics_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(session_manager.get_current_user)
):
    """Get AI insights for a reading session."""
    # Get analytics from database
    analytics = db.query(models.DocumentAnalytics).filter(
        models.DocumentAnalytics.id == analytics_id,
        models.DocumentAnalytics.user_id == current_user.id
    ).first()
    
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analytics not found"
        )
    
    if not analytics.patterns or not analytics.recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading insights not available"
        )
    
    return {
        "patterns": analytics.patterns,
        "recommendations": analytics.recommendations
    } 