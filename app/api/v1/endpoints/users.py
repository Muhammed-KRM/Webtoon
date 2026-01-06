"""
User Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.security import get_current_active_user, get_password_hash
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.core.cache_invalidation import CacheInvalidation

router = APIRouter()


class UpdateUserRequest(BaseModel):
    """Update user request"""
    email: EmailStr = None
    password: str = None


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    old_password: str
    new_password: str


@router.get("/profile", response_model=BaseResponse[dict])
def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    return BaseResponse.success_response(
        {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        },
        "Profile retrieved"
    )


@router.put("/profile", response_model=BaseResponse[dict])
def update_profile(
    request: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user profile"""
    try:
        # Update email if provided
        if request.email and request.email != current_user.email:
            # Check if email already exists
            existing = db.query(User).filter(User.email == request.email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            current_user.email = request.email
        
        # Update password if provided
        if request.password:
            current_user.hashed_password = get_password_hash(request.password)
        
        db.commit()
        db.refresh(current_user)
        
        # Invalidate user cache
        CacheInvalidation.invalidate_user_cache(current_user.id)
        
        return BaseResponse.success_response(
            {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email
            },
            "Profile updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )


@router.post("/change-password", response_model=BaseResponse[dict])
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Change user password"""
    try:
        from app.core.security import verify_password
        
        # Verify old password
        if not verify_password(request.old_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )
        
        # Update password
        current_user.hashed_password = get_password_hash(request.new_password)
        db.commit()
        
        # Invalidate user cache (security: force re-authentication)
        CacheInvalidation.invalidate_user_cache(current_user.id)
        
        return BaseResponse.success_response(
            {"message": "Password changed successfully"},
            "Password changed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error changing password: {str(e)}"
        )

