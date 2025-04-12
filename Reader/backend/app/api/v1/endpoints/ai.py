from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from app.models.document import Document
from app.services.ai_service import ai_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/documents/{document_id}/summarize")
async def summarize_document(
    document_id: str,
    max_length: int = 500,
    current_user: User = Depends(get_current_user)
) -> str:
    """Generate a summary of the document."""
    try:
        document = await Document.get(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check if user has access to the document
        if not document.is_accessible_by(current_user):
            raise HTTPException(status_code=403, detail="Not authorized to access this document")
        
        summary = await ai_service.summarize_document(document, max_length)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/keywords")
async def extract_keywords(
    document_id: str,
    num_keywords: int = 10,
    current_user: User = Depends(get_current_user)
) -> List[str]:
    """Extract keywords from the document."""
    try:
        document = await Document.get(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document.is_accessible_by(current_user):
            raise HTTPException(status_code=403, detail="Not authorized to access this document")
        
        keywords = await ai_service.extract_keywords(document, num_keywords)
        return keywords
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/sentiment")
async def analyze_sentiment(
    document_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, float]:
    """Analyze the sentiment of the document."""
    try:
        document = await Document.get(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document.is_accessible_by(current_user):
            raise HTTPException(status_code=403, detail="Not authorized to access this document")
        
        sentiment = await ai_service.analyze_sentiment(document)
        return sentiment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/classify")
async def classify_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, float]]:
    """Classify the document into categories."""
    try:
        document = await Document.get(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document.is_accessible_by(current_user):
            raise HTTPException(status_code=403, detail="Not authorized to access this document")
        
        categories = await ai_service.classify_document(document)
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/entities")
async def get_entities(
    document_id: str,
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, str]]:
    """Extract named entities from the document."""
    try:
        document = await Document.get(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document.is_accessible_by(current_user):
            raise HTTPException(status_code=403, detail="Not authorized to access this document")
        
        entities = await ai_service.get_entities(document)
        return entities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 