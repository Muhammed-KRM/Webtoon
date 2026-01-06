"""
Tag and Category Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

# Many-to-many relationship table for Series-Tag
series_tags = Table(
    'series_tags',
    Base.metadata,
    Column('series_id', Integer, ForeignKey('series.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
    Index('ix_series_tags_series', 'series_id'),
    Index('ix_series_tags_tag', 'tag_id')
)


class Tag(Base):
    """Tag model - e.g., 'comedy', 'action', 'romance'"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)  # e.g., "comedy", "action"
    slug = Column(String, nullable=False, unique=True, index=True)  # URL-friendly version
    description = Column(String, nullable=True)
    usage_count = Column(Integer, default=0)  # How many series use this tag
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    series = relationship("Series", secondary=series_tags, back_populates="tags")


class Category(Base):
    """Category model - Main genre categories"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)  # e.g., "Action", "Romance"
    slug = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=True)
    icon_url = Column(String, nullable=True)  # Category icon
    order = Column(Integer, default=0)  # Display order
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    series = relationship("Series", back_populates="category")
