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
    
    def _generate_lock_key(self, chapter_url: str, target_lang: str, translate_type: int) -> str:
        """Generate lock key for preventing duplicate translations"""
        import hashlib
        key_string = f"{chapter_url}:{target_lang}:{translate_type}"
        return f"webtoon:lock:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def acquire_translation_lock(
        self,
        chapter_url: str,
        target_lang: str = "tr",
        translate_type: int = 1,
        timeout: int = 3600  # 1 hour default timeout
    ) -> bool:
        """
        Acquire a lock for translation to prevent duplicate jobs
        
        Args:
            chapter_url: Chapter URL
            target_lang: Target language
            translate_type: Translation type (1 = AI, 2 = Free)
            timeout: Lock timeout in seconds (default: 1 hour)
            
        Returns:
            True if lock acquired, False if already locked
        """
        if not self.redis:
            return True  # No Redis, allow translation (fallback)
        
        try:
            lock_key = self._generate_lock_key(chapter_url, target_lang, translate_type)
            # Try to set lock (SET NX EX - set if not exists with expiration)
            result = self.redis.set(lock_key, "locked", nx=True, ex=timeout)
            if result:
                logger.info(f"Acquired translation lock for: {chapter_url}")
                return True
            else:
                logger.warning(f"Translation already in progress for: {chapter_url}")
                return False
        except Exception as e:
            logger.error(f"Error acquiring lock: {e}")
            return True  # On error, allow translation (fail open)
    
    def release_translation_lock(
        self,
        chapter_url: str,
        target_lang: str = "tr",
        translate_type: int = 1
    ):
        """
        Release translation lock
        
        Args:
            chapter_url: Chapter URL
            target_lang: Target language
            translate_type: Translation type
        """
        if not self.redis:
            return
        
        try:
            lock_key = self._generate_lock_key(chapter_url, target_lang, translate_type)
            self.redis.delete(lock_key)
            logger.info(f"Released translation lock for: {chapter_url}")
        except Exception as e:
            logger.error(f"Error releasing lock: {e}")
    
    def is_translation_locked(
        self,
        chapter_url: str,
        target_lang: str = "tr",
        translate_type: int = 1
    ) -> bool:
        """
        Check if translation is currently locked (in progress)
        
        Args:
            chapter_url: Chapter URL
            target_lang: Target language
            translate_type: Translation type
            
        Returns:
            True if locked, False otherwise
        """
        if not self.redis:
            return False
        
        try:
            lock_key = self._generate_lock_key(chapter_url, target_lang, translate_type)
            return self.redis.exists(lock_key) > 0
        except Exception as e:
            logger.error(f"Error checking lock: {e}")
            return False

