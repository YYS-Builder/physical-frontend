from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class SearchResult(BaseModel):
    """Model for search results"""
    document_id: str
    document_name: str
    document_type: str
    score: float
    matched_chunks: List[str]
    metadata: Dict[str, Any]

class SearchHistory(Base):
    """Model for search history"""
    __tablename__ = "search_history"
    
    id = Column(String, primary_key=True, index=True)
    query = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    results_count = Column(Integer, nullable=False)
    top_result_id = Column(String, ForeignKey("documents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="search_history")
    top_result = relationship("Document", back_populates="search_history")

class DocumentChunk(Base):
    """Model for document chunks with embeddings"""
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    content = Column(String, nullable=False)
    embedding = Column(JSON, nullable=False)  # Store embeddings as JSON
    index = Column(Integer, nullable=False)
    total_chunks = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")

class SearchFilters(BaseModel):
    """Model for search filters"""
    type: Optional[str] = None
    date_range: Optional[tuple[datetime, datetime]] = None
    size_range: Optional[tuple[int, int]] = None
    tags: Optional[List[str]] = None
    user_id: Optional[str] = None

class SearchQuery(BaseModel):
    """Model for search query"""
    query: str = Field(..., min_length=1)
    filters: Optional[SearchFilters] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class SearchResponse(BaseModel):
    """Model for search response"""
    results: List[SearchResult]
    total: int
    suggestions: List[str]
    filters: Optional[Dict[str, Any]] = None 