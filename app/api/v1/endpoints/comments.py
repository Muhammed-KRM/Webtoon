"""
Comment Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_user_optional
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.models.comment import Comment
from app.models.reading import Rating
from app.models.comment_like import CommentLike
from app.services.api_cache import api_cache
from app.core.query_optimizer import QueryOptimizer
from app.core.cache_invalidation import CacheInvalidation
from sqlalchemy.orm import joinedload, selectinload

router = APIRouter()


@router.get("/comments", response_model=BaseResponse[list])
def list_comments(
    series_id: Optional[int] = Query(None),
    chapter_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """List comments (public, auth optional, cached)"""
    try:
        # Check cache
        cache_params = {
            "series_id": series_id,
            "chapter_id": chapter_id,
            "skip": skip,
            "limit": limit
        }
        cached = api_cache.get_cached_response("/api/v1/comments", cache_params, ttl=180)  # 3 min
        if cached:
            return BaseResponse.success_response(
                cached.get("data", []),
                cached.get("message", "Found comments")
            )
        
        # Optimize query with eager loading
        query = db.query(Comment).options(
            joinedload(Comment.user),
            selectinload(Comment.replies).joinedload(Comment.user),
            selectinload(Comment.likes)
        ).filter(Comment.is_deleted == False)
        
        if series_id:
            query = query.filter(Comment.series_id == series_id)
        if chapter_id:
            query = query.filter(Comment.chapter_id == chapter_id)
        
        # Only top-level comments (no parent)
        query = query.filter(Comment.parent_comment_id == None)
        
        comments = query.order_by(desc(Comment.created_at)).offset(skip).limit(limit).all()
        
        # Build response with replies
        comment_list = []
        for comment in comments:
            comment_data = CommentResponse.model_validate(comment)
            comment_data.username = comment.user.username if comment.user else None
            
            # Get replies
            replies = db.query(Comment).filter(
                Comment.parent_comment_id == comment.id,
                Comment.is_deleted == False
            ).order_by(Comment.created_at).all()
            comment_data.replies = [CommentResponse.model_validate(r) for r in replies]
            
            # Check if current user liked this comment (if authenticated)
            if current_user:
                liked = db.query(CommentLike).filter(
                    CommentLike.user_id == current_user.id,
                    CommentLike.comment_id == comment.id
                ).first() is not None
                comment_data.liked_by_user = liked
            else:
                comment_data.liked_by_user = False
            
            comment_list.append(comment_data)
        
        # Cache result
        api_cache.set_cached_response(
            "/api/v1/comments",
            cache_params,
            {"data": [c.model_dump() if hasattr(c, 'model_dump') else c for c in comment_list], "message": f"Found {len(comment_list)} comments"},
            ttl=180
        )
        
        return BaseResponse.success_response(
            comment_list,
            f"Found {len(comment_list)} comments"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing comments: {str(e)}"
        )


@router.post("/comments", response_model=BaseResponse[CommentResponse])
def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new comment (requires authentication)"""
    try:
        new_comment = Comment(
            user_id=current_user.id,
            **comment_data.model_dump()
        )
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        # Invalidate cache
        CacheInvalidation.invalidate_comment_cache(
            series_id=comment_data.series_id,
            chapter_id=comment_data.chapter_id
        )
        
        response = CommentResponse.model_validate(new_comment)
        response.username = current_user.username
        
        return BaseResponse.success_response(
            response,
            "Comment created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating comment: {str(e)}"
        )


@router.post("/comments/{comment_id}/like", response_model=BaseResponse[dict])
def like_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Like/unlike a comment (requires authentication)"""
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Check if already liked
        existing_like = db.query(CommentLike).filter(
            CommentLike.user_id == current_user.id,
            CommentLike.comment_id == comment_id
        ).first()
        
        if existing_like:
            # Unlike
            db.delete(existing_like)
            comment.like_count = max(0, comment.like_count - 1)
            liked = False
        else:
            # Like
            new_like = CommentLike(
                user_id=current_user.id,
                comment_id=comment_id
            )
            db.add(new_like)
            comment.like_count += 1
            liked = True
        
        db.commit()
        
        return BaseResponse.success_response(
            {
                "comment_id": comment_id,
                "like_count": comment.like_count,
                "liked": liked
            },
            "Comment liked" if liked else "Comment unliked"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error liking comment: {str(e)}"
        )


@router.post("/comments/{comment_id}/reply", response_model=BaseResponse[CommentResponse])
def reply_to_comment(
    comment_id: int,
    content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reply to a comment (requires authentication)"""
    try:
        parent_comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )
        
        # Create reply
        reply = Comment(
            user_id=current_user.id,
            series_id=parent_comment.series_id,
            chapter_id=parent_comment.chapter_id,
            parent_comment_id=comment_id,
            content=content,
            attachments=None  # Can be extended for gif/memoji
        )
        db.add(reply)
        db.commit()
        db.refresh(reply)
        
        # Invalidate cache
        CacheInvalidation.invalidate_comment_cache(
            series_id=parent_comment.series_id,
            chapter_id=parent_comment.chapter_id
        )
        
        # Send notification to parent comment author
        if parent_comment.user_id != current_user.id:
            try:
                from app.services.notification_service import NotificationService
                NotificationService.notify_comment_reply(
                    db=db,
                    user_id=parent_comment.user_id,
                    comment_id=comment_id,
                    commenter_username=current_user.username
                )
            except Exception as e:
                pass  # Don't fail if notification fails
        
        response = CommentResponse.model_validate(reply)
        response.username = current_user.username
        
        return BaseResponse.success_response(
            response,
            "Reply created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating reply: {str(e)}"
        )


@router.put("/comments/{comment_id}", response_model=BaseResponse[CommentResponse])
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a comment (only own comments)"""
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        if comment.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own comments"
            )
        
        comment.content = comment_data.content
        comment.is_edited = True
        db.commit()
        db.refresh(comment)
        
        # Invalidate cache
        CacheInvalidation.invalidate_comment_cache(
            series_id=comment.series_id,
            chapter_id=comment.chapter_id
        )
        
        response = CommentResponse.model_validate(comment)
        response.username = comment.user.username if comment.user else None
        
        return BaseResponse.success_response(
            response,
            "Comment updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating comment: {str(e)}"
        )


@router.delete("/comments/{comment_id}", response_model=BaseResponse[dict])
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a comment (soft delete)"""
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        if comment.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own comments"
            )
        
        comment.is_deleted = True
        db.commit()
        
        # Invalidate cache
        CacheInvalidation.invalidate_comment_cache(
            series_id=comment.series_id,
            chapter_id=comment.chapter_id
        )
        
        return BaseResponse.success_response(
            {"comment_id": comment_id},
            "Comment deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting comment: {str(e)}"
        )
