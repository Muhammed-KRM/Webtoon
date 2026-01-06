"""
Scraper Configuration Model - Dynamic CSS selector management
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from app.db.base import Base


class ScraperConfig(Base):
    """Scraper configuration for dynamic CSS selector management"""
    __tablename__ = "scraper_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    site_name = Column(String, nullable=False, unique=True, index=True)  # webtoons.com, asuracomic.net
    site_domain = Column(String, nullable=False)  # www.webtoons.com
    is_active = Column(Boolean, default=True)
    
    # CSS Selectors (stored as JSON for flexibility)
    selectors = Column(JSON, nullable=False, default=dict)  # {
    #     "container": "div.reading-content",
    #     "image": "img",
    #     "image_attr": "data-src",
    #     "title": "h1.chapter-title",
    #     "next_chapter": "a.next-chapter"
    # }
    
    # Fallback selectors (if primary fails)
    fallback_selectors = Column(JSON, nullable=True, default=dict)
    
    # Additional config
    config = Column(JSON, nullable=True, default=dict)  # {
    #     "user_agent": "...",
    #     "headers": {...},
    #     "timeout": 30,
    #     "retry_count": 3
    # }
    
    # Metadata
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(String, nullable=True)  # Admin username
    notes = Column(Text, nullable=True)  # Admin notes about changes
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

