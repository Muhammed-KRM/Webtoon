"""
Reading History and User Preferences Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class ReadingHistory(Base):
    """User reading history"""
    __tablename__ = "reading_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)
    translation_id = Column(Integer, ForeignKey("chapter_translations.id"), nullable=True)
    last_page = Column(Integer, default=1)  # Last read page number
    progress = Column(Float, default=0.0)  # 0.0 to 1.0 (percentage)
    is_completed = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="reading_history")
    chapter = relationship("Chapter", backref="reading_history")
    translation = relationship("ChapterTranslation", backref="reading_history")
    
    # Unique constraint: one reading history per user per chapter
    __table_args__ = (
        {"sqlite_autoincrement": True} if hasattr(Base, 'metadata') else {}
    )


class Bookmark(Base):
    """User bookmarks (favorites)"""
    __tablename__ = "bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=False, index=True)
    is_favorite = Column(Boolean, default=True)
    notes = Column(String, nullable=True)  # User notes about the series
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="bookmarks")
    series = relationship("Series", backref="bookmarks")
    
    # Unique constraint: one bookmark per user per series
    __table_args__ = (
        {"sqlite_autoincrement": True} if hasattr(Base, 'metadata') else {}
    )


class Rating(Base):
    """Series and chapter ratings"""
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review = Column(String, nullable=True)  # Optional review text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="ratings")
    series = relationship("Series", backref="ratings")
    chapter = relationship("Chapter", backref="ratings")
    
    # Unique constraint: one rating per user per series/chapter
    __table_args__ = (
        {"sqlite_autoincrement": True} if hasattr(Base, 'metadata') else {}
    )


class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # translation_completed, new_chapter, comment_reply, etc.
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    link = Column(String, nullable=True)  # URL to related content
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="notifications")

