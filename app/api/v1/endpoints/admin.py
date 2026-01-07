"""
Admin Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_active_user, require_admin, require_adminadmin, get_password_hash
from app.schemas.base_response import BaseResponse
from app.schemas.auth import UserResponse
from app.models.user import User
from app.services.cache_service import CacheService
from app.core.enums import UserRole
from loguru import logger
import redis
from app.core.config import settings

router = APIRouter()
cache_service = CacheService()


class CreateAdminRequest(BaseModel):
    """Create admin user request"""
    username: str
    email: str
    password: str


@router.post("/users/create-adminadmin", response_model=BaseResponse[UserResponse])
def create_adminadmin_user(
    admin_data: CreateAdminRequest,
    db: Session = Depends(get_db)
):
    """
    Create first AdminAdmin user (first-time setup only, no auth required)
    This endpoint allows creating the first AdminAdmin user without authentication.
    After first AdminAdmin is created, this endpoint should be disabled.
    """
    try:
        # Check if any AdminAdmin already exists
        existing_adminadmin = db.query(User).filter(User.role == UserRole.ADMINADMIN).first()
        if existing_adminadmin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="AdminAdmin user already exists. Use AdminAdmin account to create new admins."
            )
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == admin_data.username) | (User.email == admin_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Create AdminAdmin user
        hashed_password = get_password_hash(admin_data.password)
        adminadmin_user = User(
            username=admin_data.username,
            email=admin_data.email,
            hashed_password=hashed_password,
            role=UserRole.ADMINADMIN,
            is_active=True
        )
        
        db.add(adminadmin_user)
        db.commit()
        db.refresh(adminadmin_user)
        
        logger.info(f"AdminAdmin user created: {adminadmin_user.username}")
        
        return BaseResponse.success_response(
            UserResponse.model_validate(adminadmin_user),
            "AdminAdmin user created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating AdminAdmin user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating AdminAdmin user: {str(e)}"
        )


@router.post("/users/create-admin", response_model=BaseResponse[UserResponse])
def create_admin_user(
    admin_data: CreateAdminRequest,
    current_user: User = Depends(require_adminadmin),
    db: Session = Depends(get_db)
):
    """
    Create admin user (AdminAdmin only)
    Only AdminAdmin users can create new admin users.
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == admin_data.username) | (User.email == admin_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Create admin user
        hashed_password = get_password_hash(admin_data.password)
        admin_user = User(
            username=admin_data.username,
            email=admin_data.email,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        logger.info(f"Admin user created by {current_user.username}: {admin_user.username}")
        
        return BaseResponse.success_response(
            UserResponse.model_validate(admin_user),
            "Admin user created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating admin user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating admin user: {str(e)}"
        )


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

