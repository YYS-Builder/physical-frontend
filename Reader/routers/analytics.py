from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..database import get_db
from ..models import User, Document, ReadingSession, ReadingGoal
from ..schemas.analytics import (
    AnalyticsResponse,
    ReadingHistoryResponse,
    ReadingHabitsResponse,
    ReadingStreakResponse,
    ReadingGoalsUpdate
)
from ..auth import get_current_user

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    time_range: str = Query("30", description="Time range in days (7, 30, 90, 365, all)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive reading analytics for the current user."""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        if time_range == "all":
            start_date = None
        else:
            start_date = end_date - timedelta(days=int(time_range))

        # Base query for reading sessions
        base_query = db.query(ReadingSession).filter(
            ReadingSession.user_id == current_user.id
        )
        if start_date:
            base_query = base_query.filter(ReadingSession.start_time >= start_date)

        # Total reading time
        total_reading_time = base_query.with_entities(
            func.sum(ReadingSession.duration_minutes)
        ).scalar() or 0

        # Documents read
        documents_read = base_query.with_entities(
            func.count(func.distinct(ReadingSession.document_id))
        ).scalar() or 0

        # Average reading speed
        avg_speed = base_query.with_entities(
            func.avg(ReadingSession.reading_speed_pages_per_hour)
        ).scalar() or 0

        # Reading streak
        streak = calculate_reading_streak(db, current_user.id)

        # Top documents
        top_documents = get_top_documents(db, current_user.id, start_date)

        # Favorite reading time
        favorite_time = get_favorite_reading_time(db, current_user.id, start_date)

        # Average session length
        avg_session_length = base_query.with_entities(
            func.avg(ReadingSession.duration_minutes)
        ).scalar() or 0

        # Completion rate
        completion_rate = calculate_completion_rate(db, current_user.id, start_date)

        # Reading goals
        goals = db.query(ReadingGoal).filter(
            ReadingGoal.user_id == current_user.id
        ).first()

        # Activity data
        activity_data = get_activity_data(db, current_user.id, start_date, end_date)

        # Speed data
        speed_data = get_speed_data(db, current_user.id, start_date, end_date)

        return AnalyticsResponse(
            total_reading_time_minutes=total_reading_time,
            documents_read=documents_read,
            average_reading_speed_pages_per_hour=avg_speed,
            reading_streak_days=streak,
            top_documents=top_documents,
            favorite_reading_time=favorite_time,
            average_session_length_minutes=avg_session_length,
            completion_rate_percentage=completion_rate,
            daily_goal_current_minutes=goals.daily_current if goals else 0,
            daily_goal_target_minutes=goals.daily_target if goals else 60,
            weekly_goal_current_minutes=goals.weekly_current if goals else 0,
            weekly_goal_target_minutes=goals.weekly_target if goals else 300,
            activity_labels=[d.strftime("%Y-%m-%d") for d in activity_data["labels"]],
            activity_data=activity_data["values"],
            speed_labels=[d.strftime("%Y-%m-%d") for d in speed_data["labels"]],
            speed_data=speed_data["values"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/goals", response_model=ReadingGoalsUpdate)
async def update_reading_goals(
    goals: ReadingGoalsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update reading goals for the current user."""
    try:
        reading_goal = db.query(ReadingGoal).filter(
            ReadingGoal.user_id == current_user.id
        ).first()

        if not reading_goal:
            reading_goal = ReadingGoal(user_id=current_user.id)
            db.add(reading_goal)

        reading_goal.daily_target = goals.daily_target_minutes
        reading_goal.weekly_target = goals.weekly_target_minutes
        db.commit()

        return goals
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}/history", response_model=ReadingHistoryResponse)
async def get_reading_history(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get reading history for a specific document."""
    try:
        sessions = db.query(ReadingSession).filter(
            ReadingSession.user_id == current_user.id,
            ReadingSession.document_id == document_id
        ).order_by(ReadingSession.start_time).all()

        return ReadingHistoryResponse(
            document_id=document_id,
            sessions=[
                {
                    "start_time": session.start_time,
                    "duration_minutes": session.duration_minutes,
                    "pages_read": session.pages_read,
                    "reading_speed": session.reading_speed_pages_per_hour
                }
                for session in sessions
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/habits", response_model=ReadingHabitsResponse)
async def get_reading_habits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get reading habits for the current user."""
    try:
        # Get reading sessions for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        sessions = db.query(ReadingSession).filter(
            ReadingSession.user_id == current_user.id,
            ReadingSession.start_time >= thirty_days_ago
        ).all()

        # Calculate reading habits
        habits = {
            "favorite_time_of_day": get_favorite_time_of_day(sessions),
            "average_session_length": calculate_average_session_length(sessions),
            "most_productive_days": get_most_productive_days(sessions),
            "reading_consistency": calculate_reading_consistency(sessions)
        }

        return ReadingHabitsResponse(**habits)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/streak", response_model=ReadingStreakResponse)
async def get_reading_streak(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current reading streak for the user."""
    try:
        streak = calculate_reading_streak(db, current_user.id)
        return ReadingStreakResponse(streak_days=streak)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def calculate_reading_streak(db: Session, user_id: int) -> int:
    """Calculate the current reading streak in days."""
    today = datetime.utcnow().date()
    streak = 0
    
    while True:
        date_to_check = today - timedelta(days=streak)
        has_read = db.query(ReadingSession).filter(
            ReadingSession.user_id == user_id,
            func.date(ReadingSession.start_time) == date_to_check
        ).first()
        
        if not has_read:
            break
        streak += 1
    
    return streak

def get_top_documents(db: Session, user_id: int, start_date: Optional[datetime]) -> List[dict]:
    """Get top documents by reading time."""
    query = db.query(
        Document,
        func.sum(ReadingSession.duration_minutes).label('total_time')
    ).join(
        ReadingSession,
        Document.id == ReadingSession.document_id
    ).filter(
        ReadingSession.user_id == user_id
    )
    
    if start_date:
        query = query.filter(ReadingSession.start_time >= start_date)
    
    return [
        {
            "id": doc.id,
            "title": doc.title,
            "total_duration_minutes": total_time,
            "reading_speed_pages_per_hour": doc.average_reading_speed,
            "completion_percentage": doc.completion_percentage,
            "last_read": doc.last_read
        }
        for doc, total_time in query.group_by(Document.id)
        .order_by(func.sum(ReadingSession.duration_minutes).desc())
        .limit(5)
    ]

def get_favorite_reading_time(db: Session, user_id: int, start_date: Optional[datetime]) -> str:
    """Get the user's favorite time of day for reading."""
    query = db.query(
        func.hour(ReadingSession.start_time).label('hour'),
        func.count().label('count')
    ).filter(
        ReadingSession.user_id == user_id
    )
    
    if start_date:
        query = query.filter(ReadingSession.start_time >= start_date)
    
    result = query.group_by('hour').order_by(func.count().desc()).first()
    if result:
        hour = result[0]
        return f"{hour:02d}:00"
    return "Unknown"

def calculate_completion_rate(db: Session, user_id: int, start_date: Optional[datetime]) -> float:
    """Calculate the completion rate of started documents."""
    query = db.query(
        func.count(func.distinct(ReadingSession.document_id)).label('total'),
        func.count(func.distinct(
            ReadingSession.document_id
        )).filter(
            Document.completion_percentage == 100
        ).label('completed')
    ).join(
        Document,
        ReadingSession.document_id == Document.id
    ).filter(
        ReadingSession.user_id == user_id
    )
    
    if start_date:
        query = query.filter(ReadingSession.start_time >= start_date)
    
    result = query.first()
    if result and result[0] > 0:
        return (result[1] / result[0]) * 100
    return 0.0

def get_activity_data(db: Session, user_id: int, start_date: Optional[datetime], end_date: datetime) -> dict:
    """Get reading activity data for charts."""
    query = db.query(
        func.date(ReadingSession.start_time).label('date'),
        func.sum(ReadingSession.duration_minutes).label('total_time')
    ).filter(
        ReadingSession.user_id == user_id
    )
    
    if start_date:
        query = query.filter(ReadingSession.start_time >= start_date)
    
    results = query.group_by('date').order_by('date').all()
    
    labels = []
    values = []
    current_date = start_date.date() if start_date else (end_date - timedelta(days=30)).date()
    
    while current_date <= end_date.date():
        labels.append(current_date)
        values.append(0)
        current_date += timedelta(days=1)
    
    for date, total_time in results:
        if date in labels:
            index = labels.index(date)
            values[index] = total_time
    
    return {"labels": labels, "values": values}

def get_speed_data(db: Session, user_id: int, start_date: Optional[datetime], end_date: datetime) -> dict:
    """Get reading speed data for charts."""
    query = db.query(
        func.date(ReadingSession.start_time).label('date'),
        func.avg(ReadingSession.reading_speed_pages_per_hour).label('avg_speed')
    ).filter(
        ReadingSession.user_id == user_id
    )
    
    if start_date:
        query = query.filter(ReadingSession.start_time >= start_date)
    
    results = query.group_by('date').order_by('date').all()
    
    labels = []
    values = []
    current_date = start_date.date() if start_date else (end_date - timedelta(days=30)).date()
    
    while current_date <= end_date.date():
        labels.append(current_date)
        values.append(0)
        current_date += timedelta(days=1)
    
    for date, avg_speed in results:
        if date in labels:
            index = labels.index(date)
            values[index] = avg_speed
    
    return {"labels": labels, "values": values}

def get_favorite_time_of_day(sessions: List[ReadingSession]) -> str:
    """Get the most common time of day for reading."""
    hour_counts = {}
    for session in sessions:
        hour = session.start_time.hour
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
    
    if hour_counts:
        favorite_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        return f"{favorite_hour:02d}:00"
    return "Unknown"

def calculate_average_session_length(sessions: List[ReadingSession]) -> float:
    """Calculate average session length in minutes."""
    if not sessions:
        return 0.0
    total_time = sum(session.duration_minutes for session in sessions)
    return total_time / len(sessions)

def get_most_productive_days(sessions: List[ReadingSession]) -> List[str]:
    """Get the most productive days of the week."""
    day_counts = {}
    for session in sessions:
        day = session.start_time.strftime("%A")
        day_counts[day] = day_counts.get(day, 0) + 1
    
    return [
        day for day, _ in sorted(
            day_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
    ]

def calculate_reading_consistency(sessions: List[ReadingSession]) -> float:
    """Calculate reading consistency as a percentage of days with reading activity."""
    if not sessions:
        return 0.0
    
    unique_days = len(set(
        session.start_time.date() for session in sessions
    ))
    total_days = 30  # Last 30 days
    
    return (unique_days / total_days) * 100 