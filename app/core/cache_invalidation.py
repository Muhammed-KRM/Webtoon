"""
Cache Invalidation Service - Aggressive invalidation on data changes
"""
from app.services.api_cache import api_cache
from loguru import logger
from typing import Optional
import hashlib
import json


class CacheInvalidation:
    """Service for invalidating cache when data changes"""
    
    @staticmethod
    def invalidate_series_cache(series_id: Optional[int] = None):
        """Invalidate series-related cache"""
        try:
            if api_cache.redis:
                # Invalidate series list (all variations)
                patterns = [
                    "api:cache:*series*",
                    "api:cache:*public/series*",
                    f"series_count:*"
                ]
                for pattern in patterns:
                    api_cache.invalidate_cache(pattern)
                
                # Invalidate series detail
                if series_id:
                    patterns = [
                        f"api:cache:*series/{series_id}*",
                        f"api:cache:*public/series/{series_id}*"
                    ]
                    for pattern in patterns:
                        api_cache.invalidate_cache(pattern)
                
                # Also invalidate chapter list for this series
                if series_id:
                    CacheInvalidation.invalidate_chapter_cache(series_id=series_id)
                
                logger.info(f"Invalidated series cache for series_id={series_id}")
        except Exception as e:
            logger.error(f"Error invalidating series cache: {e}")
    
    @staticmethod
    def invalidate_chapter_cache(chapter_id: Optional[int] = None, series_id: Optional[int] = None):
        """Invalidate chapter-related cache"""
        try:
            if api_cache.redis:
                # Invalidate chapter list
                if series_id:
                    patterns = [
                        f"api:cache:*series/{series_id}/chapters*",
                        f"api:cache:*public/series/{series_id}/chapters*"
                    ]
                    for pattern in patterns:
                        api_cache.invalidate_cache(pattern)
                
                # Invalidate chapter detail
                if chapter_id:
                    patterns = [
                        f"api:cache:*chapters/{chapter_id}*",
                        f"api:cache:*public/chapters/{chapter_id}*"
                    ]
                    for pattern in patterns:
                        api_cache.invalidate_cache(pattern)
                
                # Invalidate chapter translations
                if chapter_id:
                    api_cache.invalidate_cache(f"api:cache:*chapters/{chapter_id}/translations*")
                
                # Also invalidate series cache (series detail shows chapters)
                if series_id:
                    CacheInvalidation.invalidate_series_cache(series_id=series_id)
                
                logger.info(f"Invalidated chapter cache for chapter_id={chapter_id}, series_id={series_id}")
        except Exception as e:
            logger.error(f"Error invalidating chapter cache: {e}")
    
    @staticmethod
    def invalidate_comment_cache(series_id: Optional[int] = None, chapter_id: Optional[int] = None):
        """Invalidate comment cache - AGGRESSIVE"""
        try:
            if api_cache.redis:
                # Invalidate ALL comment caches (comments change frequently)
                patterns = [
                    "api:cache:*comments*",
                    "api:cache:*public/comments*"
                ]
                for pattern in patterns:
                    api_cache.invalidate_cache(pattern)
                
                # Also invalidate series/chapter detail (they show comment counts)
                if series_id:
                    CacheInvalidation.invalidate_series_cache(series_id=series_id)
                if chapter_id:
                    CacheInvalidation.invalidate_chapter_cache(chapter_id=chapter_id)
                
                logger.info(f"Invalidated comment cache (series_id={series_id}, chapter_id={chapter_id})")
        except Exception as e:
            logger.error(f"Error invalidating comment cache: {e}")
    
    @staticmethod
    def invalidate_user_cache(user_id: int):
        """Invalidate user-specific cache"""
        try:
            if api_cache.redis:
                api_cache.invalidate_cache(f"api:cache:*{user_id}*")
                api_cache.invalidate_cache(f"api:cache:*reading/history/{user_id}*")
                api_cache.invalidate_cache(f"api:cache:*bookmarks/{user_id}*")
                logger.info(f"Invalidated user cache for user_id={user_id}")
        except Exception as e:
            logger.error(f"Error invalidating user cache: {e}")
    
    @staticmethod
    def invalidate_reaction_cache(series_id: Optional[int] = None, chapter_id: Optional[int] = None, comment_id: Optional[int] = None):
        """Invalidate reaction cache"""
        try:
            if api_cache.redis:
                # Invalidate all reaction caches
                patterns = [
                    "api:cache:*reactions*"
                ]
                for pattern in patterns:
                    api_cache.invalidate_cache(pattern)
                
                # Also invalidate related entity caches (they show reaction counts)
                if series_id:
                    CacheInvalidation.invalidate_series_cache(series_id=series_id)
                if chapter_id:
                    CacheInvalidation.invalidate_chapter_cache(chapter_id=chapter_id)
                if comment_id:
                    CacheInvalidation.invalidate_comment_cache()
                
                logger.info(f"Invalidated reaction cache")
        except Exception as e:
            logger.error(f"Error invalidating reaction cache: {e}")

