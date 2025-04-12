from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.search import SearchResult, SearchFilters
from app.services.sentiment_analysis import SentimentAnalysisService
from app.services.entity_extraction import EntityExtractionService
from app.services.document_classification import DocumentClassificationService
from app.services.semantic_search import SemanticSearchService
from app.services.faceted_search import FacetedSearchService
from app.core.logging import logger

router = APIRouter()

@router.get("/documents/{document_id}/sentiment", response_model=dict)
async def get_sentiment_analysis(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get sentiment analysis for a document"""
    try:
        service = SentimentAnalysisService()
        result = await service.analyze_document(document_id, current_user.id)
        return result
    except Exception as e:
        logger.error(f"Error getting sentiment analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get sentiment analysis"
        )

@router.get("/documents/{document_id}/entities", response_model=List[dict])
async def get_entities(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get extracted entities from a document"""
    try:
        service = EntityExtractionService()
        result = await service.extract_entities(document_id, current_user.id)
        return result
    except Exception as e:
        logger.error(f"Error extracting entities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to extract entities"
        )

@router.get("/documents/{document_id}/classification", response_model=dict)
async def get_classification(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get document classification"""
    try:
        service = DocumentClassificationService()
        result = await service.classify_document(document_id, current_user.id)
        return result
    except Exception as e:
        logger.error(f"Error classifying document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to classify document"
        )

@router.post("/documents/search", response_model=List[SearchResult])
async def search_documents(
    query: str,
    filters: Optional[SearchFilters] = None,
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Search documents using semantic search"""
    try:
        service = SemanticSearchService()
        results = await service.search_documents(
            query=query,
            user_id=current_user.id,
            filters=filters,
            limit=limit,
            offset=offset
        )
        return results
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to search documents"
        )

@router.get("/documents/facets", response_model=dict)
async def get_facets(
    filters: Optional[SearchFilters] = None,
    current_user: User = Depends(get_current_user)
):
    """Get available search facets"""
    try:
        service = FacetedSearchService()
        facets = await service.get_facets(
            user_id=current_user.id,
            base_filters=filters
        )
        return facets
    except Exception as e:
        logger.error(f"Error getting facets: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get search facets"
        )

@router.get("/documents/{document_id}/chunks", response_model=List[dict])
async def get_document_chunks(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get document chunks"""
    try:
        service = SemanticSearchService()
        chunks = await service.get_document_chunks(document_id, current_user.id)
        return chunks
    except Exception as e:
        logger.error(f"Error getting document chunks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get document chunks"
        )

@router.get("/documents/search/suggestions", response_model=List[str])
async def get_search_suggestions(
    query: str,
    limit: int = 5,
    current_user: User = Depends(get_current_user)
):
    """Get search suggestions"""
    try:
        service = SemanticSearchService()
        suggestions = await service.get_search_suggestions(
            query=query,
            user_id=current_user.id,
            limit=limit
        )
        return suggestions
    except Exception as e:
        logger.error(f"Error getting search suggestions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get search suggestions"
        )

@router.get("/documents/search/history", response_model=List[dict])
async def get_search_history(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get search history"""
    try:
        service = SemanticSearchService()
        history = await service.get_search_history(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        return history
    except Exception as e:
        logger.error(f"Error getting search history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get search history"
        ) 