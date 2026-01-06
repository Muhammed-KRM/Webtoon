"""
Reading History and Bookmarks Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.models.reading import ReadingHistory, Bookmark, Rating
from app.models.series import Series, Chapter
from app.core.cache_invalidation import CacheInvalidation

router = APIRouter()


@router.post("/reading/history", response_model=BaseResponse[dict])
def update_reading_history(
    chapter_id: int,
    translation_id: Optional[int] = None,
    last_page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update reading history"""
    try:
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        # Calculate progress
        total_pages = chapter.page_count or 1
        progress = min(1.0, last_page / total_pages) if total_pages > 0 else 0.0
        is_completed = progress >= 1.0
        
        # Find or create reading history
        history = db.query(ReadingHistory).filter(
            ReadingHistory.user_id == current_user.id,
            ReadingHistory.chapter_id == chapter_id
        ).first()
        
        if history:
            history.last_page = last_page
            history.progress = progress
            history.is_completed = is_completed
            if translation_id:
                history.translation_id = translation_id
        else:
            history = ReadingHistory(
                user_id=current_user.id,
                chapter_id=chapter_id,
                translation_id=translation_id,
                last_page=last_page,
                progress=progress,
                is_completed=is_completed
            )
            db.add(history)
        
        db.commit()
        db.refresh(history)
        
        # Invalidate cache
        CacheInvalidation.invalidate_user_cache(current_user.id)
        
        return BaseResponse.success_response(
            {
                "chapter_id": chapter_id,
                "last_page": last_page,
                "progress": progress,
                "is_completed": is_completed
            },
            "Reading history updated"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating reading history: {str(e)}"
        )


@router.get("/reading/history", response_model=BaseResponse[list])
def get_reading_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's reading history"""
    try:
        history = db.query(ReadingHistory).filter(
            ReadingHistory.user_id == current_user.id
        ).order_by(desc(ReadingHistory.updated_at)).offset(skip).limit(limit).all()
        
        history_list = []
        for h in history:
            history_list.append({
                "chapter_id": h.chapter_id,
                "chapter_title": h.chapter.title if h.chapter else None,
                "series_title": h.chapter.series.title if h.chapter and h.chapter.series else None,
                "last_page": h.last_page,
                "progress": h.progress,
                "is_completed": h.is_completed,
                "read_at": h.read_at.isoformat() if h.read_at else None
            })
        
        return BaseResponse.success_response(
            history_list,
            f"Found {len(history_list)} reading history entries"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting reading history: {str(e)}"
        )


@router.post("/bookmarks", response_model=BaseResponse[dict])
def add_bookmark(
    series_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add series to bookmarks"""
    try:
        series = db.query(Series).filter(Series.id == series_id).first()
        if not series:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Series not found"
            )
        
        bookmark = db.query(Bookmark).filter(
            Bookmark.user_id == current_user.id,
            Bookmark.series_id == series_id
        ).first()
        
        if bookmark:
            bookmark.is_favorite = True
            if notes:
                bookmark.notes = notes
        else:
            bookmark = Bookmark(
                user_id=current_user.id,
                series_id=series_id,
                notes=notes
            )
            db.add(bookmark)
        
        db.commit()
        
        # Invalidate cache
        CacheInvalidation.invalidate_user_cache(current_user.id)
        CacheInvalidation.invalidate_series_cache(series_id=series_id)  # Bookmark count changes
        
        return BaseResponse.success_response(
            {"series_id": series_id, "is_favorite": True},
            "Bookmark added"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding bookmark: {str(e)}"
        )


@router.delete("/bookmarks/{series_id}", response_model=BaseResponse[dict])
def remove_bookmark(
    series_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove series from bookmarks"""
    try:
        bookmark = db.query(Bookmark).filter(
            Bookmark.user_id == current_user.id,
            Bookmark.series_id == series_id
        ).first()
        
        if bookmark:
            db.delete(bookmark)
            db.commit()
        
        return BaseResponse.success_response(
            {"series_id": series_id},
            "Bookmark removed"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing bookmark: {str(e)}"
        )


@router.get("/bookmarks", response_model=BaseResponse[list])
def get_bookmarks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's bookmarks"""
    try:
        bookmarks = db.query(Bookmark).filter(
            Bookmark.user_id == current_user.id,
            Bookmark.is_favorite == True
        ).order_by(desc(Bookmark.created_at)).offset(skip).limit(limit).all()
        
        bookmark_list = []
        for b in bookmarks:
            bookmark_list.append({
                "series_id": b.series_id,
                "series_title": b.series.title if b.series else None,
                "notes": b.notes,
                "created_at": b.created_at.isoformat() if b.created_at else None
            })
        
        return BaseResponse.success_response(
            bookmark_list,
            f"Found {len(bookmark_list)} bookmarks"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting bookmarks: {str(e)}"
        )


@router.post("/ratings", response_model=BaseResponse[dict])
def add_rating(
    series_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    rating: int = Query(..., ge=1, le=5),
    review: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add rating to series or chapter"""
    try:
        if not series_id and not chapter_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either series_id or chapter_id must be provided"
            )
        
        # Check if rating already exists
        existing = db.query(Rating).filter(
            Rating.user_id == current_user.id
        )
        if series_id:
            existing = existing.filter(Rating.series_id == series_id)
        if chapter_id:
            existing = existing.filter(Rating.chapter_id == chapter_id)
        existing = existing.first()
        
        if existing:
            existing.rating = rating
            if review:
                existing.review = review
        else:
            new_rating = Rating(
                user_id=current_user.id,
                series_id=series_id,
                chapter_id=chapter_id,
                rating=rating,
                review=review
            )
            db.add(new_rating)
        
        db.commit()
        
        # Update series/chapter average rating
        if series_id:
            series = db.query(Series).filter(Series.id == series_id).first()
            if series:
                ratings = db.query(Rating).filter(Rating.series_id == series_id).all()
                if ratings:
                    series.rating = sum(r.rating for r in ratings) / len(ratings)
                    series.rating_count = len(ratings)
                    db.commit()
                    
                    # Invalidate cache (rating changed)
                    CacheInvalidation.invalidate_series_cache(series_id=series_id)
        
        # Also invalidate chapter cache if chapter rating
        if chapter_id:
            CacheInvalidation.invalidate_chapter_cache(chapter_id=chapter_id)
        
        return BaseResponse.success_response(
            {"rating": rating, "series_id": series_id, "chapter_id": chapter_id},
            "Rating added"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding rating: {str(e)}"
        )

