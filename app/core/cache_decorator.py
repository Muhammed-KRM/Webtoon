"""
Cache Decorator - For caching function results
"""
from functools import wraps
from typing import Callable, TypeVar, Optional
import hashlib
import json
from app.services.api_cache import api_cache
from loguru import logger

T = TypeVar('T')


def cache_result(ttl: int = 300, key_prefix: str = "func"):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            key_data = {
                "func": func.__name__,
                "args": str(args),
                "kwargs": json.dumps(kwargs, sort_keys=True, default=str)
            }
            cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()}"
            
            # Try to get from cache
            if api_cache.redis:
                try:
                    cached = api_cache.redis.get(cache_key)
                    if cached:
                        logger.debug(f"Cache hit: {func.__name__}")
                        return json.loads(cached)
                except:
                    pass
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            if api_cache.redis:
                try:
                    api_cache.redis.setex(cache_key, ttl, json.dumps(result, default=str))
                    logger.debug(f"Cache set: {func.__name__}")
                except:
                    pass
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            key_data = {
                "func": func.__name__,
                "args": str(args),
                "kwargs": json.dumps(kwargs, sort_keys=True, default=str)
            }
            cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()}"
            
            # Try to get from cache
            if api_cache.redis:
                try:
                    cached = api_cache.redis.get(cache_key)
                    if cached:
                        logger.debug(f"Cache hit: {func.__name__}")
                        return json.loads(cached)
                except:
                    pass
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            if api_cache.redis:
                try:
                    api_cache.redis.setex(cache_key, ttl, json.dumps(result, default=str))
                    logger.debug(f"Cache set: {func.__name__}")
                except:
                    pass
            
            return result
        
        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

