from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from ..database import Base

class User(Base):
    """Model for user accounts."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    collections = relationship("Collection", back_populates="owner")
    documents = relationship("Document", back_populates="owner")
    reading_sessions = relationship("ReadingSession", back_populates="user")
    reading_goals = relationship("ReadingGoal", back_populates="user", uselist=False)
    reading_stats = relationship("ReadingStats", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>" 