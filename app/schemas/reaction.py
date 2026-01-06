"""
Reaction Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReactionCreate(BaseModel):
    """Create reaction schema"""
    reaction_type: str  # emoji, gif, memoji
    reaction_value: str  # emoji code, gif URL, memoji data
    series_id: Optional[int] = None
    chapter_id: Optional[int] = None
    comment_id: Optional[int] = None


class ReactionResponse(BaseModel):
    """Reaction response schema"""
    id: int
    user_id: int
    username: Optional[str] = None
    reaction_type: str
    reaction_value: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReactionSummary(BaseModel):
    """Reaction summary (grouped by value)"""
    type: str
    value: str
    count: int
    users: List[dict]


class ReactionsResponse(BaseModel):
    """Reactions response with summary"""
    reactions: List[ReactionSummary]
    total: int
    user_reaction: Optional[dict] = None

