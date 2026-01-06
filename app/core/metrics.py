"""
Metrics and Telemetry
"""
from typing import Dict
from datetime import datetime
import redis
from app.core.config import settings
from loguru import logger

try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis connection failed for metrics: {e}")
    redis_client = None


class MetricsCollector:
    """Collect and store application metrics"""
    
    @staticmethod
    def increment_counter(key: str, value: int = 1):
        """Increment a counter metric"""
        if redis_client is None:
            return
        
        try:
            redis_client.incrby(f"metrics:counter:{key}", value)
            # Set expiry (30 days)
            redis_client.expire(f"metrics:counter:{key}", 2592000)
        except Exception as e:
            logger.warning(f"Error incrementing counter: {e}")
    
    @staticmethod
    def record_timing(key: str, duration: float):
        """Record a timing metric"""
        if redis_client is None:
            return
        
        try:
            # Store in sorted set (for percentile calculations)
            redis_client.zadd(f"metrics:timing:{key}", {str(datetime.now().timestamp()): duration})
            # Keep only last 1000 entries
            redis_client.zremrangebyrank(f"metrics:timing:{key}", 0, -1001)
        except Exception as e:
            logger.warning(f"Error recording timing: {e}")
    
    @staticmethod
    def get_counter(key: str) -> int:
        """Get counter value"""
        if redis_client is None:
            return 0
        
        try:
            value = redis_client.get(f"metrics:counter:{key}")
            return int(value) if value else 0
        except Exception as e:
            logger.warning(f"Error getting counter: {e}")
            return 0
    
    @staticmethod
    def get_timing_stats(key: str) -> Dict:
        """Get timing statistics"""
        if redis_client is None:
            return {}
        
        try:
            values = redis_client.zrange(f"metrics:timing:{key}", 0, -1, withscores=True)
            if not values:
                return {}
            
            durations = [float(score) for _, score in values]
            durations.sort()
            
            count = len(durations)
            if count == 0:
                return {}
            
            return {
                "count": count,
                "min": min(durations),
                "max": max(durations),
                "avg": sum(durations) / count,
                "p50": durations[count // 2] if count > 0 else 0,
                "p95": durations[int(count * 0.95)] if count > 1 else durations[0],
                "p99": durations[int(count * 0.99)] if count > 1 else durations[0]
            }
        except Exception as e:
            logger.warning(f"Error getting timing stats: {e}")
            return {}


# Global metrics collector
metrics = MetricsCollector()

