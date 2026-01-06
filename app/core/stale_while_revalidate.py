"""
Stale-While-Revalidate Pattern - Show cached data immediately, refresh in background
"""
from typing import Optional, Callable, Any
from app.services.api_cache import api_cache
from loguru import logger
import asyncio
from threading import Thread
import time


class StaleWhileRevalidate:
    """Stale-while-revalidate cache pattern"""
    
    @staticmethod
    def get_with_revalidate(
        cache_key: str,
        fetch_func: Callable,
        ttl: int = 300,
        stale_ttl: int = 600,  # How long to keep stale data
        *args,
        **kwargs
    ) -> Any:
        """
        Get data with stale-while-revalidate pattern
        
        Args:
            cache_key: Cache key
            fetch_func: Function to fetch fresh data
            ttl: Fresh data TTL
            stale_ttl: Stale data TTL (longer)
            *args, **kwargs: Arguments for fetch_func
        
        Returns:
            Cached data (may be stale), refreshes in background
        """
        if not api_cache.redis:
            # No cache, fetch directly
            return fetch_func(*args, **kwargs)
        
        try:
            # Try to get fresh cache
            cached = api_cache.redis.get(cache_key)
            if cached:
                import json
                data = json.loads(cached)
                
                # Check if stale (TTL expired but still in cache)
                ttl_remaining = api_cache.redis.ttl(cache_key)
                
                if ttl_remaining > 0:
                    # Fresh data
                    return data
                elif ttl_remaining == -1 or ttl_remaining < -stale_ttl:
                    # Stale data, refresh in background
                    Thread(
                        target=StaleWhileRevalidate._refresh_cache,
                        args=(cache_key, fetch_func, ttl, args, kwargs),
                        daemon=True
                    ).start()
                    return data
                else:
                    # Stale but acceptable, refresh in background
                    Thread(
                        target=StaleWhileRevalidate._refresh_cache,
                        args=(cache_key, fetch_func, ttl, args, kwargs),
                        daemon=True
                    ).start()
                    return data
            
            # No cache, fetch and cache
            fresh_data = fetch_func(*args, **kwargs)
            StaleWhileRevalidate._set_cache(cache_key, fresh_data, ttl)
            return fresh_data
            
        except Exception as e:
            logger.error(f"Error in stale-while-revalidate: {e}")
            # Fallback to direct fetch
            return fetch_func(*args, **kwargs)
    
    @staticmethod
    def _refresh_cache(cache_key: str, fetch_func: Callable, ttl: int, args: tuple, kwargs: dict):
        """Refresh cache in background"""
        try:
            fresh_data = fetch_func(*args, **kwargs)
            StaleWhileRevalidate._set_cache(cache_key, fresh_data, ttl)
            logger.debug(f"Cache refreshed in background: {cache_key}")
        except Exception as e:
            logger.error(f"Error refreshing cache: {e}")
    
    @staticmethod
    def _set_cache(cache_key: str, data: Any, ttl: int):
        """Set cache"""
        try:
            import json
            api_cache.redis.setex(cache_key, ttl, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Error setting cache: {e}")

