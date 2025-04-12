from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from ..database import Base

class Document(Base):
    """Model for documents."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    file_type = Column(String, nullable=False)  # pdf, epub, txt
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_read = Column(DateTime, nullable=True)
    average_reading_speed = Column(Float, nullable=True)  # pages/hour
    completion_percentage = Column(Float, nullable=False, default=0.0)
    is_public = Column(Boolean, default=False)
    metadata = Column(Text, nullable=True)  # JSON string for additional metadata

    # Relationships
    owner = relationship("User", back_populates="documents")
    collection = relationship("Collection", back_populates="documents")
    reading_sessions = relationship("ReadingSession", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, owner_id={self.owner_id})>" 