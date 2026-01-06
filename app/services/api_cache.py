"""
API Response Caching Service
"""
import json
import hashlib
from typing import Optional, Any
from redis import Redis
from loguru import logger
from app.core.config import settings


class APICacheService:
    """Service for caching API responses"""
    
    def __init__(self):
        """Initialize Redis client"""
        try:
            self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.redis.ping()
            logger.info("API Cache Redis connection established")
        except Exception as e:
            logger.warning(f"API Cache Redis connection failed: {e}")
            self.redis = None
    
    def _generate_cache_key(self, endpoint: str, params: dict) -> str:
        """Generate cache key from endpoint and parameters"""
        # Sort params for consistent keys
        sorted_params = json.dumps(params, sort_keys=True)
        key_string = f"{endpoint}:{sorted_params}"
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"api:cache:{key_hash}"
    
    def get_cached_response(
        self,
        endpoint: str,
        params: dict,
        ttl: int = 300  # 5 minutes default
    ) -> Optional[Any]:
        """Get cached API response"""
        if not self.redis:
            return None
        
        try:
            cache_key = self._generate_cache_key(endpoint, params)
            cached_data = self.redis.get(cache_key)
            
            if cached_data:
                logger.debug(f"API cache hit: {endpoint}")
                return json.loads(cached_data)
            
            return None
        except Exception as e:
            logger.error(f"Error getting API cache: {e}")
            return None
    
    def set_cached_response(
        self,
        endpoint: str,
        params: dict,
        response: Any,
        ttl: int = 300  # 5 minutes default
    ):
        """Cache API response"""
        if not self.redis:
            return
        
        try:
            cache_key = self._generate_cache_key(endpoint, params)
            cached_data = json.dumps(response, default=str)
            self.redis.setex(cache_key, ttl, cached_data)
            logger.debug(f"API cache set: {endpoint}")
        except Exception as e:
            logger.error(f"Error setting API cache: {e}")
    
    def invalidate_cache(self, pattern: str = "api:cache:*"):
        """Invalidate cache entries matching pattern"""
        if not self.redis:
            return
        
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
                logger.info(f"Invalidated {len(keys)} API cache entries")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")


# Global instance
api_cache = APICacheService()

