"""
Comment Model - User comments on series and chapters
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Comment(Base):
    """Comment model"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True, index=True)
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)  # For replies
    content = Column(Text, nullable=False)
    attachments = Column(JSON, nullable=True)  # For images, gifs, etc.
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    like_count = Column(Integer, default=0)  # Denormalized count for performance
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="comments")
    series = relationship("Series", back_populates="comments")
    chapter = relationship("Chapter", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

