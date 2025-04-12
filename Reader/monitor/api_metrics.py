from prometheus_client import Counter, Histogram, Gauge
from typing import Dict, Any
import time
from ..monitor import monitor

# API Metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['endpoint', 'method', 'status_code']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['endpoint', 'method']
)

api_errors_total = Counter(
    'api_errors_total',
    'Total number of API errors',
    ['endpoint', 'method', 'error_type']
)

api_rate_limited = Counter(
    'api_rate_limited_total',
    'Total number of rate-limited requests',
    ['endpoint', 'method']
)

api_response_size = Histogram(
    'api_response_size_bytes',
    'API response size in bytes',
    ['endpoint', 'method']
)

class APIMonitor:
    def __init__(self):
        self.monitor = monitor
    
    async def track_request(self, endpoint: str, method: str, duration: float, status_code: int):
        """Track API request metrics."""
        # Track total requests
        api_requests_total.labels(
            endpoint=endpoint,
            method=method,
            status_code=status_code
        ).inc()
        
        # Track request duration
        api_request_duration.labels(
            endpoint=endpoint,
            method=method
        ).observe(duration)
        
        # Track errors
        if status_code >= 400:
            api_errors_total.labels(
                endpoint=endpoint,
                method=method,
                error_type=str(status_code)
            ).inc()
    
    async def track_rate_limit(self, endpoint: str, method: str):
        """Track rate-limited requests."""
        api_rate_limited.labels(
            endpoint=endpoint,
            method=method
        ).inc()
    
    async def track_response_size(self, endpoint: str, method: str, size: int):
        """Track API response size."""
        api_response_size.labels(
            endpoint=endpoint,
            method=method
        ).observe(size)
    
    async def get_api_metrics(self) -> Dict[str, Any]:
        """Get current API metrics."""
        return {
            "total_requests": api_requests_total._value.get(),
            "error_rate": api_errors_total._value.get() / api_requests_total._value.get() if api_requests_total._value.get() > 0 else 0,
            "rate_limited_requests": api_rate_limited._value.get(),
            "average_response_size": api_response_size._sum.get() / api_response_size._count.get() if api_response_size._count.get() > 0 else 0,
            "average_response_time": api_request_duration._sum.get() / api_request_duration._count.get() if api_request_duration._count.get() > 0 else 0
        }

# Global instance
api_monitor = APIMonitor() 