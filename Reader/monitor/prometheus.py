from prometheus_client import start_http_server, Counter, Histogram, Gauge, Enum
import time
from typing import Dict, Any
from ..config import settings
import psutil

# API Metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

api_errors_total = Counter(
    'api_errors_total',
    'Total number of API errors',
    ['error_type', 'endpoint']
)

api_rate_limited = Counter(
    'api_rate_limited_total',
    'Total number of rate-limited requests',
    ['endpoint']
)

api_response_size = Histogram(
    'api_response_size_bytes',
    'API response size in bytes',
    ['method', 'endpoint'],
    buckets=[100, 1000, 10000, 100000, 1000000]
)

# System Metrics
system_uptime = Gauge(
    'system_uptime_seconds',
    'System uptime in seconds'
)

system_memory_usage = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

system_cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

system_disk_usage = Gauge(
    'system_disk_usage_bytes',
    'System disk usage in bytes'
)

# Application Metrics
app_health = Enum(
    'app_health',
    'Application health status',
    states=['healthy', 'degraded', 'unhealthy']
)

app_version = Gauge(
    'app_version',
    'Application version',
    ['version']
)

# Database Metrics
db_connections = Gauge(
    'db_connections_total',
    'Total number of database connections'
)

db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

class PrometheusMetrics:
    def __init__(self):
        self.start_time = time.time()
        if settings.ENABLE_METRICS:
            start_http_server(settings.METRICS_PORT)
    
    def update_system_metrics(self):
        """Update system metrics."""
        system_uptime.set(time.time() - self.start_time)
        system_memory_usage.set(psutil.virtual_memory().used)
        system_cpu_usage.set(psutil.cpu_percent())
        system_disk_usage.set(psutil.disk_usage('/').used)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics data."""
        self.update_system_metrics()
        
        return {
            "api": {
                "requests_total": api_requests_total._value.get(),
                "request_duration": api_request_duration._sum.get(),
                "errors_total": api_errors_total._value.get(),
                "rate_limited": api_rate_limited._value.get(),
                "response_size": api_response_size._sum.get()
            },
            "system": {
                "uptime": system_uptime._value.get(),
                "memory_usage": system_memory_usage._value.get(),
                "cpu_usage": system_cpu_usage._value.get(),
                "disk_usage": system_disk_usage._value.get()
            },
            "app": {
                "health": app_health._value.get(),
                "version": app_version._value.get()
            },
            "database": {
                "connections": db_connections._value.get(),
                "query_duration": db_query_duration._sum.get()
            }
        }

# Alerting rules
ALERT_RULES = {
    "high_error_rate": {
        "condition": "rate(api_errors_total[5m]) > 0.1",
        "duration": "5m",
        "severity": "critical",
        "summary": "High error rate detected",
        "description": "Error rate exceeds 10% over the last 5 minutes"
    },
    "high_latency": {
        "condition": "rate(api_request_duration_seconds_sum[5m]) / rate(api_request_duration_seconds_count[5m]) > 1",
        "duration": "5m",
        "severity": "warning",
        "summary": "High API latency detected",
        "description": "Average request duration exceeds 1 second"
    },
    "high_memory_usage": {
        "condition": "system_memory_usage_bytes / system_memory_total_bytes > 0.9",
        "duration": "5m",
        "severity": "warning",
        "summary": "High memory usage detected",
        "description": "Memory usage exceeds 90%"
    },
    "high_cpu_usage": {
        "condition": "system_cpu_usage_percent > 80",
        "duration": "5m",
        "severity": "warning",
        "summary": "High CPU usage detected",
        "description": "CPU usage exceeds 80%"
    }
}

# Global instance
prometheus_metrics = PrometheusMetrics() 