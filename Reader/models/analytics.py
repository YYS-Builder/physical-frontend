from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from ..database import Base

class ReadingSession(Base):
    """Model for tracking individual reading sessions."""
    __tablename__ = "reading_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, nullable=False)
    pages_read = Column(Integer, nullable=False)
    reading_speed_pages_per_hour = Column(Float, nullable=False)
    completion_percentage = Column(Float, nullable=False, default=0.0)
    notes = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="reading_sessions")
    document = relationship("Document", back_populates="reading_sessions")

    def __repr__(self):
        return f"<ReadingSession(id={self.id}, user_id={self.user_id}, document_id={self.document_id})>"

class ReadingGoal(Base):
    """Model for tracking user reading goals."""
    __tablename__ = "reading_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    daily_target = Column(Integer, nullable=False, default=60)  # minutes
    daily_current = Column(Integer, nullable=False, default=0)  # minutes
    weekly_target = Column(Integer, nullable=False, default=300)  # minutes
    weekly_current = Column(Integer, nullable=False, default=0)  # minutes
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reading_goals")

    def __repr__(self):
        return f"<ReadingGoal(id={self.id}, user_id={self.user_id})>"

class ReadingStats(Base):
    """Model for storing aggregated reading statistics."""
    __tablename__ = "reading_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    total_reading_time = Column(Float, nullable=False)  # minutes
    documents_read = Column(Integer, nullable=False)
    average_speed = Column(Float, nullable=False)  # pages/hour
    streak_days = Column(Integer, nullable=False)
    completion_rate = Column(Float, nullable=False)  # percentage

    # Relationships
    user = relationship("User", back_populates="reading_stats")

    def __repr__(self):
        return f"<ReadingStats(id={self.id}, user_id={self.user_id}, date={self.date})>" 