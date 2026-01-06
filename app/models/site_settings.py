"""
Site Settings Model - Site configuration and theme
"""
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base
from app.core.enums import Theme


class SiteSettings(Base):
    """Site settings model"""
    __tablename__ = "site_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    site_name = Column(String, default="Webtoon AI Translator")
    site_description = Column(Text, nullable=True)
    site_logo_url = Column(String, nullable=True)
    theme = Column(String, default=Theme.LIGHT)  # light, dark, auto
    primary_color = Column(String, default="#007bff")
    secondary_color = Column(String, default="#6c757d")
    maintenance_mode = Column(Boolean, default=False)
    maintenance_message = Column(Text, nullable=True)
    allow_registration = Column(Boolean, default=True)
    allow_guest_access = Column(Boolean, default=True)
    default_language = Column(String, default="tr")
    supported_languages = Column(JSON, default=["tr", "en"])  # List of supported languages
    settings_json = Column(JSON, nullable=True)  # Additional settings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

