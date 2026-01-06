"""
Series Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SeriesBase(BaseModel):
    """Base series schema"""
    title: str
    title_original: Optional[str] = None
    description: str  # Required - series must have description
    cover_image_url: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None  # Legacy field
    category_id: Optional[int] = None  # New category relationship
    tags: Optional[List[str]] = None  # List of tag names (e.g., ["comedy", "action"])
    source_url: Optional[str] = None
    source_site: Optional[str] = None


class SeriesCreate(SeriesBase):
    """Create series schema"""
    pass


class SeriesUpdate(BaseModel):
    """Update series schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None


class SeriesResponse(SeriesBase):
    """Series response schema"""
    id: int
    status: str
    is_active: bool
    is_featured: bool
    view_count: int
    rating: int
    rating_count: int
    category_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChapterBase(BaseModel):
    """Base chapter schema"""
    chapter_number: int
    title: Optional[str] = None
    source_url: Optional[str] = None


class ChapterCreate(ChapterBase):
    """Create chapter schema"""
    series_id: int


class ChapterResponse(ChapterBase):
    """Chapter response schema"""
    id: int
    series_id: int
    page_count: int
    view_count: int
    is_published: bool
    published_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChapterTranslationResponse(BaseModel):
    """Chapter translation response"""
    id: int
    chapter_id: int
    source_lang: str
    target_lang: str
    storage_path: str
    page_count: int
    status: str
    is_published: bool
    view_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True
