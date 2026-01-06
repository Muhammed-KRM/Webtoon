"""
Cache Management Endpoints - Manual cache refresh
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from app.core.security import get_current_active_user, require_admin
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.core.cache_invalidation import CacheInvalidation
from app.services.api_cache import api_cache

router = APIRouter()


@router.post("/cache/refresh", response_model=BaseResponse[dict])
def refresh_cache(
    series_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    comment_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Manually refresh cache for specific entities (any authenticated user)"""
    try:
        invalidated = []
        
        if series_id:
            CacheInvalidation.invalidate_series_cache(series_id=series_id)
            invalidated.append(f"series_{series_id}")
        
        if chapter_id:
            CacheInvalidation.invalidate_chapter_cache(chapter_id=chapter_id, series_id=series_id)
            invalidated.append(f"chapter_{chapter_id}")
        
        if comment_id:
            CacheInvalidation.invalidate_comment_cache()
            invalidated.append(f"comments")
        
        if not invalidated:
            # Refresh all cache
            if api_cache.redis:
                api_cache.invalidate_cache("api:cache:*")
            invalidated.append("all")
        
        return BaseResponse.success_response(
            {"invalidated": invalidated},
            "Cache refreshed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing cache: {str(e)}"
        )


@router.get("/cache/status", response_model=BaseResponse[dict])
def get_cache_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get cache status and statistics"""
    try:
        if not api_cache.redis:
            return BaseResponse.success_response(
                {"status": "disabled", "message": "Redis cache is not available"},
                "Cache status retrieved"
            )
        
        # Get cache statistics
        try:
            info = api_cache.redis.info("memory")
            keys = api_cache.redis.keys("api:cache:*")
            
            return BaseResponse.success_response(
                {
                    "status": "enabled",
                    "total_keys": len(keys),
                    "memory_used": info.get("used_memory_human", "unknown"),
                    "memory_peak": info.get("used_memory_peak_human", "unknown")
                },
                "Cache status retrieved"
            )
        except Exception as e:
            return BaseResponse.success_response(
                {"status": "error", "error": str(e)},
                "Cache status retrieved"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting cache status: {str(e)}"
        )

