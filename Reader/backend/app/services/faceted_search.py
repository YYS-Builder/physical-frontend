from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.search import SearchFilters, SearchResult
from app.core.logging import logger
from sqlalchemy import func, and_, or_

class FacetedSearchService:
    def __init__(self):
        self.db = SessionLocal()
    
    async def get_facets(
        self,
        user_id: str,
        base_filters: Optional[SearchFilters] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get available facets for filtering"""
        try:
            # Build base query
            query = self.db.query(Document).filter(Document.user_id == user_id)
            
            # Apply base filters if provided
            if base_filters:
                query = self._apply_filters(query, base_filters)
            
            # Get document types
            types = query.with_entities(
                Document.type,
                func.count(Document.id).label('count')
            ).group_by(Document.type).all()
            
            # Get date ranges
            dates = query.with_entities(
                func.date_trunc('month', Document.created_at).label('month'),
                func.count(Document.id).label('count')
            ).group_by('month').order_by('month').all()
            
            # Get size ranges
            sizes = query.with_entities(
                func.width_bucket(Document.size, 0, 1000000000, 10).label('bucket'),
                func.count(Document.id).label('count')
            ).group_by('bucket').order_by('bucket').all()
            
            # Get tags
            tags = query.with_entities(
                func.unnest(Document.tags).label('tag'),
                func.count(Document.id).label('count')
            ).group_by('tag').order_by('count').all()
            
            return {
                'types': [{'value': t[0], 'count': t[1]} for t in types],
                'dates': [{'value': d[0].isoformat(), 'count': d[1]} for d in dates],
                'sizes': [{'value': s[0], 'count': s[1]} for s in sizes],
                'tags': [{'value': t[0], 'count': t[1]} for t in tags]
            }
            
        except Exception as e:
            logger.error(f"Error getting facets: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to get search facets"
            )
    
    def _apply_filters(
        self,
        query,
        filters: SearchFilters
    ):
        """Apply filters to query"""
        if filters.type:
            query = query.filter(Document.type == filters.type)
        
        if filters.date_range:
            start_date, end_date = filters.date_range
            query = query.filter(
                Document.created_at.between(start_date, end_date)
            )
        
        if filters.size_range:
            min_size, max_size = filters.size_range
            query = query.filter(
                Document.size.between(min_size, max_size)
            )
        
        if filters.tags:
            query = query.filter(
                Document.tags.overlap(filters.tags)
            )
        
        if filters.user_id:
            query = query.filter(Document.user_id == filters.user_id)
        
        return query
    
    async def search_with_facets(
        self,
        user_id: str,
        filters: SearchFilters,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search documents with facet filters"""
        try:
            # Build base query
            query = self.db.query(Document).filter(Document.user_id == user_id)
            
            # Apply filters
            query = self._apply_filters(query, filters)
            
            # Get total count
            total = query.count()
            
            # Get paginated results
            documents = query.offset(offset).limit(limit).all()
            
            # Convert to search results
            results = []
            for doc in documents:
                result = SearchResult(
                    document_id=doc.id,
                    document_name=doc.name,
                    document_type=doc.type,
                    score=1.0,  # Faceted search doesn't use scores
                    matched_chunks=[],  # No chunks for faceted search
                    metadata={
                        'created_at': doc.created_at,
                        'updated_at': doc.updated_at,
                        'size': doc.size,
                        'tags': doc.tags
                    }
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in faceted search: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to perform faceted search"
            )
    
    async def get_facet_counts(
        self,
        user_id: str,
        facet: str,
        filters: Optional[SearchFilters] = None
    ) -> Dict[str, int]:
        """Get counts for a specific facet"""
        try:
            # Build base query
            query = self.db.query(Document).filter(Document.user_id == user_id)
            
            # Apply filters if provided
            if filters:
                query = self._apply_filters(query, filters)
            
            if facet == 'type':
                counts = query.with_entities(
                    Document.type,
                    func.count(Document.id)
                ).group_by(Document.type).all()
                return {t[0]: t[1] for t in counts}
            
            elif facet == 'date':
                counts = query.with_entities(
                    func.date_trunc('month', Document.created_at),
                    func.count(Document.id)
                ).group_by('month').all()
                return {d[0].isoformat(): d[1] for d in counts}
            
            elif facet == 'size':
                counts = query.with_entities(
                    func.width_bucket(Document.size, 0, 1000000000, 10),
                    func.count(Document.id)
                ).group_by('bucket').all()
                return {str(s[0]): s[1] for s in counts}
            
            elif facet == 'tags':
                counts = query.with_entities(
                    func.unnest(Document.tags),
                    func.count(Document.id)
                ).group_by('tag').all()
                return {t[0]: t[1] for t in counts}
            
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid facet: {facet}"
                )
            
        except Exception as e:
            logger.error(f"Error getting facet counts: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to get facet counts"
            ) 