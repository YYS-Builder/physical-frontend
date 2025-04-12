from typing import List, Dict, Any
from fastapi import HTTPException
from sentence_transformers import SentenceTransformer
import numpy as np
from app.core.config import settings
from app.models.document import Document
from app.models.search import SearchResult, SearchHistory
from app.db.session import SessionLocal
from app.core.logging import logger

class SemanticSearchService:
    def __init__(self):
        self.model = SentenceTransformer(settings.SEMANTIC_SEARCH_MODEL)
        self.db = SessionLocal()
        
    async def search_documents(
        self,
        query: str,
        user_id: str,
        filters: Dict[str, Any] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchResult]:
        try:
            # Get user's accessible documents
            documents = self.db.query(Document).filter(
                Document.user_id == user_id
            ).all()
            
            if not documents:
                return []
            
            # Generate query embedding
            query_embedding = self.model.encode(query)
            
            # Calculate similarities
            results = []
            for doc in documents:
                # Get document chunks
                chunks = self.db.query(DocumentChunk).filter(
                    DocumentChunk.document_id == doc.id
                ).all()
                
                # Calculate chunk similarities
                chunk_similarities = []
                for chunk in chunks:
                    chunk_embedding = np.frombuffer(chunk.embedding)
                    similarity = np.dot(query_embedding, chunk_embedding)
                    chunk_similarities.append((chunk, similarity))
                
                # Sort chunks by similarity
                chunk_similarities.sort(key=lambda x: x[1], reverse=True)
                
                # Get top matching chunks
                top_chunks = chunk_similarities[:3]
                
                # Calculate document score
                doc_score = sum(sim for _, sim in top_chunks) / len(top_chunks)
                
                # Apply filters if provided
                if filters:
                    if not self._apply_filters(doc, filters):
                        continue
                
                # Create search result
                result = SearchResult(
                    document_id=doc.id,
                    document_name=doc.name,
                    document_type=doc.type,
                    score=doc_score,
                    matched_chunks=[chunk.content for chunk, _ in top_chunks],
                    metadata={
                        'created_at': doc.created_at,
                        'updated_at': doc.updated_at,
                        'size': doc.size
                    }
                )
                results.append(result)
            
            # Sort results by score
            results.sort(key=lambda x: x.score, reverse=True)
            
            # Save search to history
            self._save_search_history(query, user_id, results)
            
            return results[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to perform semantic search"
            )
    
    def _apply_filters(self, document: Document, filters: Dict[str, Any]) -> bool:
        """Apply search filters to document"""
        for key, value in filters.items():
            if key == 'type' and document.type != value:
                return False
            if key == 'date_range':
                start_date, end_date = value
                if not (start_date <= document.created_at <= end_date):
                    return False
            if key == 'size_range':
                min_size, max_size = value
                if not (min_size <= document.size <= max_size):
                    return False
        return True
    
    def _save_search_history(
        self,
        query: str,
        user_id: str,
        results: List[SearchResult]
    ) -> None:
        """Save search query and results to history"""
        try:
            search_history = SearchHistory(
                query=query,
                user_id=user_id,
                results_count=len(results),
                top_result_id=results[0].document_id if results else None
            )
            self.db.add(search_history)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error saving search history: {str(e)}")
            self.db.rollback()
    
    async def get_search_suggestions(
        self,
        query: str,
        user_id: str,
        limit: int = 5
    ) -> List[str]:
        """Get search suggestions based on query and user history"""
        try:
            # Get user's recent searches
            recent_searches = self.db.query(SearchHistory).filter(
                SearchHistory.user_id == user_id
            ).order_by(SearchHistory.created_at.desc()).limit(10).all()
            
            # Generate suggestions
            suggestions = set()
            for search in recent_searches:
                if query.lower() in search.query.lower():
                    suggestions.add(search.query)
            
            return list(suggestions)[:limit]
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {str(e)}")
            return []
    
    async def get_search_history(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchHistory]:
        """Get user's search history"""
        try:
            return self.db.query(SearchHistory).filter(
                SearchHistory.user_id == user_id
            ).order_by(SearchHistory.created_at.desc()).offset(offset).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting search history: {str(e)}")
            return [] 