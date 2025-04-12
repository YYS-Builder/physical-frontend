import time
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from . import models, logger

class SystemMonitor:
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "start_time": datetime.now(),
            "requests_processed": 0,
            "errors_encountered": 0,
            "average_response_time": 0,
            "total_response_time": 0,
            "active_users": 0,
            "documents_processed": 0,
            "storage_used": 0
        }
        self.logger = logger.logger

    def track_request(self, response_time: float):
        """Track API request metrics."""
        self.metrics["requests_processed"] += 1
        self.metrics["total_response_time"] += response_time
        self.metrics["average_response_time"] = (
            self.metrics["total_response_time"] / self.metrics["requests_processed"]
        )

    def track_error(self, error_type: str, error_message: str):
        """Track system errors."""
        self.metrics["errors_encountered"] += 1
        self.logger.error(f"{error_type}: {error_message}")

    def update_user_metrics(self, db: Session):
        """Update metrics related to users and documents."""
        try:
            self.metrics["active_users"] = db.query(models.User).count()
            self.metrics["documents_processed"] = db.query(models.Document).count()
            
            # Calculate storage used (in MB)
            total_size = db.query(func.sum(models.Document.file_size)).scalar() or 0
            self.metrics["storage_used"] = total_size / (1024 * 1024)  # Convert to MB
        except Exception as e:
            self.logger.error(f"Error updating metrics: {str(e)}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        uptime = datetime.now() - self.metrics["start_time"]
        return {
            **self.metrics,
            "uptime_seconds": uptime.total_seconds(),
            "uptime_hours": uptime.total_seconds() / 3600
        }

    def reset_metrics(self):
        """Reset all metrics except start_time."""
        self.metrics = {
            "start_time": self.metrics["start_time"],
            "requests_processed": 0,
            "errors_encountered": 0,
            "average_response_time": 0,
            "total_response_time": 0,
            "active_users": 0,
            "documents_processed": 0,
            "storage_used": 0
        }

# Create global monitor instance
monitor = SystemMonitor() 