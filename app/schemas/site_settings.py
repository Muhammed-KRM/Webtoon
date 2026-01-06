"""
Site Settings Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SiteSettingsResponse(BaseModel):
    """Site settings response"""
    id: int
    site_name: str
    site_description: Optional[str] = None
    site_logo_url: Optional[str] = None
    theme: str
    primary_color: str
    secondary_color: str
    maintenance_mode: bool
    maintenance_message: Optional[str] = None
    allow_registration: bool
    allow_guest_access: bool
    default_language: str
    supported_languages: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SiteSettingsUpdate(BaseModel):
    """Update site settings"""
    site_name: Optional[str] = None
    site_description: Optional[str] = None
    site_logo_url: Optional[str] = None
    theme: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None
    allow_registration: Optional[bool] = None
    allow_guest_access: Optional[bool] = None
    default_language: Optional[str] = None
    supported_languages: Optional[List[str]] = None

