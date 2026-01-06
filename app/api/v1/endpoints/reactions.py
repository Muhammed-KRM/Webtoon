"""
Reaction Endpoints - Emoji/GIF/Memoji reactions
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_user_optional
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.models.reaction import Reaction
from app.models.series import Series, Chapter
from app.models.comment import Comment
from app.services.api_cache import api_cache
from app.core.cache_invalidation import CacheInvalidation
from sqlalchemy.orm import joinedload

router = APIRouter()


@router.post("/reactions", response_model=BaseResponse[dict])
def add_reaction(
    reaction_type: str = Query(..., regex="^(emoji|gif|memoji)$"),
    reaction_value: str = Query(...),
    series_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    comment_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add reaction to series, chapter, or comment"""
    try:
        # Validate that exactly one target is provided
        targets = [series_id, chapter_id, comment_id]
        if sum(1 for t in targets if t is not None) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exactly one of series_id, chapter_id, or comment_id must be provided"
            )
        
        # Check if reaction already exists
        query = db.query(Reaction).filter(Reaction.user_id == current_user.id)
        if series_id:
            query = query.filter(Reaction.series_id == series_id)
            # Verify series exists
            series = db.query(Series).filter(Series.id == series_id).first()
            if not series:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Series not found"
                )
        if chapter_id:
            query = query.filter(Reaction.chapter_id == chapter_id)
            # Verify chapter exists
            chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
            if not chapter:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chapter not found"
                )
        if comment_id:
            query = query.filter(Reaction.comment_id == comment_id)
            # Verify comment exists
            comment = db.query(Comment).filter(Comment.id == comment_id).first()
            if not comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Comment not found"
                )
        
        existing = query.first()
        
        if existing:
            # Update existing reaction
            existing.reaction_type = reaction_type
            existing.reaction_value = reaction_value
        else:
            # Create new reaction
            new_reaction = Reaction(
                user_id=current_user.id,
                series_id=series_id,
                chapter_id=chapter_id,
                comment_id=comment_id,
                reaction_type=reaction_type,
                reaction_value=reaction_value
            )
            db.add(new_reaction)
        
        db.commit()
        
        # Invalidate cache
        CacheInvalidation.invalidate_reaction_cache(
            series_id=series_id,
            chapter_id=chapter_id,
            comment_id=comment_id
        )
        
        return BaseResponse.success_response(
            {
                "reaction_type": reaction_type,
                "reaction_value": reaction_value,
                "series_id": series_id,
                "chapter_id": chapter_id,
                "comment_id": comment_id
            },
            "Reaction added"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding reaction: {str(e)}"
        )


@router.delete("/reactions", response_model=BaseResponse[dict])
def remove_reaction(
    series_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    comment_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove reaction from series, chapter, or comment"""
    try:
        # Validate that exactly one target is provided
        targets = [series_id, chapter_id, comment_id]
        if sum(1 for t in targets if t is not None) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exactly one of series_id, chapter_id, or comment_id must be provided"
            )
        
        query = db.query(Reaction).filter(Reaction.user_id == current_user.id)
        if series_id:
            query = query.filter(Reaction.series_id == series_id)
        if chapter_id:
            query = query.filter(Reaction.chapter_id == chapter_id)
        if comment_id:
            query = query.filter(Reaction.comment_id == comment_id)
        
        reaction = query.first()
        if reaction:
            db.delete(reaction)
            db.commit()
            
            # Invalidate cache
            CacheInvalidation.invalidate_reaction_cache(
                series_id=series_id,
                chapter_id=chapter_id,
                comment_id=comment_id
            )
        
        return BaseResponse.success_response(
            {"removed": True},
            "Reaction removed"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing reaction: {str(e)}"
        )


@router.get("/reactions", response_model=BaseResponse[dict])
def get_reactions(
    series_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    comment_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get reactions for series, chapter, or comment (public, cached)"""
    try:
        # Validate that exactly one target is provided
        targets = [series_id, chapter_id, comment_id]
        if sum(1 for t in targets if t is not None) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exactly one of series_id, chapter_id, or comment_id must be provided"
            )
        
        # Check cache
        cache_params = {"series_id": series_id, "chapter_id": chapter_id, "comment_id": comment_id, "user_id": current_user.id if current_user else None}
        cached = api_cache.get_cached_response("/api/v1/reactions", cache_params, ttl=180)  # 3 min
        if cached:
            return BaseResponse.success_response(
                cached.get("data", {}),
                cached.get("message", "Reactions retrieved")
            )
        
        # Optimize query
        query = db.query(Reaction).options(
            joinedload(Reaction.user)
        )
        if series_id:
            query = query.filter(Reaction.series_id == series_id)
        if chapter_id:
            query = query.filter(Reaction.chapter_id == chapter_id)
        if comment_id:
            query = query.filter(Reaction.comment_id == comment_id)
        
        reactions = query.all()
        
        # Group by reaction value
        reaction_counts = {}
        user_reaction = None
        
        for reaction in reactions:
            key = f"{reaction.reaction_type}:{reaction.reaction_value}"
            if key not in reaction_counts:
                reaction_counts[key] = {
                    "type": reaction.reaction_type,
                    "value": reaction.reaction_value,
                    "count": 0,
                    "users": []
                }
            reaction_counts[key]["count"] += 1
            reaction_counts[key]["users"].append({
                "user_id": reaction.user_id,
                "username": reaction.user.username if reaction.user else None
            })
            
            # Check if current user reacted
            if current_user and reaction.user_id == current_user.id:
                user_reaction = {
                    "type": reaction.reaction_type,
                    "value": reaction.reaction_value
                }
        
        return BaseResponse.success_response(
            {
                "reactions": list(reaction_counts.values()),
                "total": len(reactions),
                "user_reaction": user_reaction
            }
        
        # Cache result
        api_cache.set_cached_response(
            "/api/v1/reactions",
            cache_params,
            {"data": response_data, "message": "Reactions retrieved"},
            ttl=180
        )
        
        return BaseResponse.success_response(
            response_data,
            "Reactions retrieved"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting reactions: {str(e)}"
        )

