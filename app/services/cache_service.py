"""
Cache Service - Redis cache management
"""
import json
import base64
from typing import Optional, Dict, Any
from redis import Redis
from loguru import logger
from app.core.config import settings


class CacheService:
    """Service for caching processed images and translations"""
    
    def __init__(self):
        """Initialize Redis client"""
        try:
            self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=False)
            self.redis.ping()  # Test connection
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.redis = None
    
    def _generate_cache_key(self, chapter_url: str, target_lang: str, mode: str) -> str:
        """Generate cache key for a chapter"""
        import hashlib
        key_string = f"{chapter_url}:{target_lang}:{mode}"
        return f"webtoon:translation:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def get_cached_result(
        self,
        chapter_url: str,
        target_lang: str = "tr",
        mode: str = "clean"
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached translation result
        
        Returns:
            Cached result if exists, None otherwise
        """
        if not self.redis:
            return None
        
        try:
            cache_key = self._generate_cache_key(chapter_url, target_lang, mode)
            cached_data = self.redis.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for: {chapter_url}")
                return json.loads(cached_data)
            
            return None
        except Exception as e:
            logger.error(f"Error getting cache: {e}")
            return None
    
    def set_cached_result(
        self,
        chapter_url: str,
        result: Dict[str, Any],
        target_lang: str = "tr",
        mode: str = "clean",
        ttl: int = 86400 * 30  # 30 days
    ):
        """
        Cache translation result
        
        Args:
            chapter_url: Chapter URL
            result: Translation result to cache
            target_lang: Target language
            mode: Processing mode
            ttl: Time to live in seconds (default: 30 days)
        """
        if not self.redis:
            return
        
        try:
            cache_key = self._generate_cache_key(chapter_url, target_lang, mode)
            cached_data = json.dumps(result)
            self.redis.setex(cache_key, ttl, cached_data)
            logger.info(f"Cached result for: {chapter_url}")
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
    
    def clear_cache(self, pattern: str = "webtoon:*"):
        """Clear cache entries matching pattern"""
        if not self.redis:
            return
        
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache entries")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

