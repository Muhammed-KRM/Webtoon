"""
Site Settings Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.site_settings import SiteSettingsResponse, SiteSettingsUpdate
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.models.site_settings import SiteSettings
from app.services.api_cache import api_cache

router = APIRouter()


@router.get("/settings", response_model=BaseResponse[SiteSettingsResponse])
def get_site_settings(db: Session = Depends(get_db)):
    """Get site settings (public)"""
    settings = db.query(SiteSettings).first()
    
    if not settings:
        # Create default settings
        settings = SiteSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return BaseResponse.success_response(
        SiteSettingsResponse.model_validate(settings),
        "Site settings retrieved"
    )


@router.put("/settings", response_model=BaseResponse[SiteSettingsResponse])
def update_site_settings(
    settings_data: SiteSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update site settings (Admin only)"""
    try:
        settings = db.query(SiteSettings).first()
        
        if not settings:
            settings = SiteSettings()
            db.add(settings)
        
        # Update fields
        update_data = settings_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(settings, key, value)
        
        db.commit()
        db.refresh(settings)
        
        # Invalidate all cache (site settings affect everything)
        if api_cache.redis:
            api_cache.invalidate_cache("api:cache:*")
        
        return BaseResponse.success_response(
            SiteSettingsResponse.model_validate(settings),
            "Site settings updated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating site settings: {str(e)}"
        )

