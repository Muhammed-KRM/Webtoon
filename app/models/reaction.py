"""
Reaction Model - Emoji/GIF/Memoji reactions
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.core.enums import ReactionType


class Reaction(Base):
    """Reaction model - emoji, gif, memoji reactions"""
    __tablename__ = "reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Target entity (one of these will be set)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True, index=True)
    
    # Reaction type and content
    reaction_type = Column(String, nullable=False)  # emoji, gif, memoji (use ReactionType enum)
    reaction_value = Column(String, nullable=False)  # emoji code, gif URL, memoji data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="reactions")
    series = relationship("Series", backref="reactions")
    chapter = relationship("Chapter", backref="reactions")
    comment = relationship("Comment", backref="reactions")
    
    # Unique constraint: one reaction per user per entity
    __table_args__ = (
        UniqueConstraint('user_id', 'series_id', name='unique_user_series_reaction'),
        UniqueConstraint('user_id', 'chapter_id', name='unique_user_chapter_reaction'),
        UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_reaction'),
    )

