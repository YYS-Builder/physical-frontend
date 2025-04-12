from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class ReadingSession(BaseModel):
    start_time: datetime
    duration_minutes: float
    pages_read: int
    reading_speed: float

class TopDocument(BaseModel):
    id: int
    title: str
    total_duration_minutes: float
    reading_speed_pages_per_hour: float
    completion_percentage: float
    last_read: datetime

class ReadingHistoryResponse(BaseModel):
    document_id: int
    sessions: List[ReadingSession]

class ReadingHabitsResponse(BaseModel):
    favorite_time_of_day: str
    average_session_length: float
    most_productive_days: List[str]
    reading_consistency: float

class ReadingStreakResponse(BaseModel):
    streak_days: int

class ReadingGoalsUpdate(BaseModel):
    daily_target_minutes: int
    weekly_target_minutes: int

class AnalyticsResponse(BaseModel):
    total_reading_time_minutes: float
    documents_read: int
    average_reading_speed_pages_per_hour: float
    reading_streak_days: int
    top_documents: List[TopDocument]
    favorite_reading_time: str
    average_session_length_minutes: float
    completion_rate_percentage: float
    daily_goal_current_minutes: float
    daily_goal_target_minutes: int
    weekly_goal_current_minutes: float
    weekly_goal_target_minutes: int
    activity_labels: List[str]
    activity_data: List[float]
    speed_labels: List[str]
    speed_data: List[float] 