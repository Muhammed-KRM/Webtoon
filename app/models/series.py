"""
Series Model - Webtoon series management
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.core.enums import SeriesStatus, TranslationStatus


class Series(Base):
    """Webtoon series model"""
    __tablename__ = "series"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    title_original = Column(String, nullable=True)
    description = Column(Text, nullable=False)  # Made required - series must have description
    cover_image_url = Column(String, nullable=True)
    author = Column(String, nullable=True)
    genre = Column(String, nullable=True)  # Legacy field - kept for backward compatibility
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)  # New category relationship
    status = Column(String, default=SeriesStatus.ONGOING)  # ongoing, completed, hiatus
    source_url = Column(String, nullable=True)  # Original source URL
    source_site = Column(String, nullable=True)  # webtoons.com, asurascans.com.tr
    is_active = Column(Boolean, default=True)
    is_published = Column(Boolean, default=True)  # Published to public
    is_featured = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    rating = Column(Integer, default=0)  # Average rating
    rating_count = Column(Integer, default=0)
    extra_data = Column(JSON, nullable=True)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    chapters = relationship("Chapter", back_populates="series", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="series", cascade="all, delete-orphan")
    category = relationship("Category", back_populates="series")
    tags = relationship("Tag", secondary="series_tags", back_populates="series")


class Chapter(Base):
    """Chapter model"""
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=False, index=True)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    page_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    series = relationship("Series", back_populates="chapters")
    translations = relationship("ChapterTranslation", back_populates="chapter", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="chapter", cascade="all, delete-orphan")


class ChapterTranslation(Base):
    """Chapter translation model - stores translated versions"""
    __tablename__ = "chapter_translations"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)
    source_lang = Column(String, nullable=False)  # en, ko, ja
    target_lang = Column(String, nullable=False)  # tr, en, es
    storage_path = Column(String, nullable=False)  # Path to translated images
    page_count = Column(Integer, default=0)
    translation_job_id = Column(String, nullable=True)  # Celery task ID
    status = Column(String, default=TranslationStatus.PENDING)  # pending, processing, completed, failed
    is_published = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    chapter = relationship("Chapter", back_populates="translations")
    
    # Unique constraint: one translation per chapter per language pair
    __table_args__ = (
        {"sqlite_autoincrement": True} if hasattr(Base, 'metadata') else {}
    )

