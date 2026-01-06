"""
Rate Limiting Middleware
"""
from fastapi import Request, HTTPException, status
from typing import Callable
from datetime import datetime, timedelta
import redis
from app.core.config import settings
from loguru import logger

# Redis client for rate limiting
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis connection failed for rate limiting: {e}")
    redis_client = None


def rate_limit(
    max_requests: int = 10,
    window_seconds: int = 60,
    key_prefix: str = "rate_limit"
):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
        key_prefix: Redis key prefix
    """
    def decorator(func: Callable):
        async def wrapper(request: Request, *args, **kwargs):
            if redis_client is None:
                # If Redis is not available, skip rate limiting
                return await func(request, *args, **kwargs)
            
            # Get user ID from token (if authenticated)
            user_id = None
            if hasattr(request.state, "user"):
                user_id = request.state.user.id
            
            # Use IP address as fallback
            client_ip = request.client.host if request.client else "unknown"
            identifier = f"user_{user_id}" if user_id else f"ip_{client_ip}"
            
            # Create rate limit key
            key = f"{key_prefix}:{identifier}"
            
            # Get current count
            current = redis_client.get(key)
            if current is None:
                # First request in window
                redis_client.setex(key, window_seconds, 1)
                return await func(request, *args, **kwargs)
            
            current_count = int(current)
            if current_count >= max_requests:
                # Rate limit exceeded
                ttl = redis_client.ttl(key)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {ttl} seconds."
                )
            
            # Increment counter
            redis_client.incr(key)
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def check_rate_limit(
    identifier: str,
    max_requests: int = 10,
    window_seconds: int = 60,
    key_prefix: str = "rate_limit"
) -> tuple[bool, int]:
    """
    Check rate limit for an identifier
    
    Returns:
        (is_allowed, remaining_requests)
    """
    if redis_client is None:
        return True, max_requests
    
    key = f"{key_prefix}:{identifier}"
    current = redis_client.get(key)
    
    if current is None:
        redis_client.setex(key, window_seconds, 1)
        return True, max_requests - 1
    
    current_count = int(current)
    if current_count >= max_requests:
        ttl = redis_client.ttl(key)
        return False, 0
    
    redis_client.incr(key)
    return True, max_requests - current_count - 1

