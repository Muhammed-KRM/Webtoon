"""
Comment Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CommentBase(BaseModel):
    """Base comment schema"""
    content: str
    series_id: Optional[int] = None
    chapter_id: Optional[int] = None
    parent_comment_id: Optional[int] = None
    attachments: Optional[list] = None  # For images, gifs, etc.


class CommentCreate(CommentBase):
    """Create comment schema"""
    pass


class CommentUpdate(BaseModel):
    """Update comment schema"""
    content: str


class CommentResponse(CommentBase):
    """Comment response schema"""
    id: int
    user_id: int
    username: Optional[str] = None  # From user relationship
    is_edited: bool
    is_deleted: bool
    like_count: int
    liked_by_user: bool = False  # Whether current user liked this comment
    created_at: datetime
    updated_at: Optional[datetime] = None
    replies: List['CommentResponse'] = []
    
    class Config:
        from_attributes = True


CommentResponse.model_rebuild()

