"""
Admin Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_admin
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.services.cache_service import CacheService
from loguru import logger
import redis
from app.core.config import settings

router = APIRouter()
cache_service = CacheService()


@router.delete("/cache/clear", response_model=BaseResponse[dict])
def clear_cache(
    current_user: User = Depends(require_admin)
):
    """Clear all cache (Redis and disk)"""
    try:
        # Clear Redis cache
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.flushdb()
            logger.info("Redis cache cleared")
        except Exception as e:
            logger.warning(f"Error clearing Redis cache: {e}")
        
        # Clear disk cache (if implemented)
        # cache_service.clear_disk_cache()
        
        return BaseResponse.success_response(
            {"cleared": True},
            "Cache cleared successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )


@router.get("/stats", response_model=BaseResponse[dict])
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get system statistics"""
    try:
        from app.models.job import TranslationJob
        from sqlalchemy import func
        
        # Get job statistics
        total_jobs = db.query(func.count(TranslationJob.id)).scalar()
        from app.core.enums import JobStatus
        
        completed_jobs = db.query(func.count(TranslationJob.id)).filter(
            TranslationJob.status == JobStatus.COMPLETED
        ).scalar()
        failed_jobs = db.query(func.count(TranslationJob.id)).filter(
            TranslationJob.status == JobStatus.FAILED
        ).scalar()
        pending_jobs = db.query(func.count(TranslationJob.id)).filter(
            TranslationJob.status == JobStatus.PENDING
        ).scalar()
        
        # Get user statistics
        total_users = db.query(func.count(User.id)).scalar()
        active_users = db.query(func.count(User.id)).filter(
            User.is_active == True
        ).scalar()
        
        return BaseResponse.success_response(
            {
                "jobs": {
                    "total": total_jobs,
                    "completed": completed_jobs,
                    "failed": failed_jobs,
                    "pending": pending_jobs
                },
                "users": {
                    "total": total_users,
                    "active": active_users
                }
            },
            "Statistics retrieved"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )

