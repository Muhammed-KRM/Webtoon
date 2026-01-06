"""
Public Endpoints - No authentication required
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import Optional, List
from app.core.database import get_db
from app.schemas.series import SeriesResponse, ChapterResponse, ChapterTranslationResponse
from app.schemas.comment import CommentResponse
from app.schemas.base_response import BaseResponse
from app.models.series import Series, Chapter, ChapterTranslation
from app.models.comment import Comment
from app.models.reading import Rating
from app.models.site_settings import SiteSettings

router = APIRouter()


@router.get("/public/series", response_model=BaseResponse[List[SeriesResponse]])
def list_series_public(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    genre: Optional[str] = None,
    status: Optional[str] = None,
    sort: str = Query("newest", regex="^(newest|popular|rating)$"),
    db: Session = Depends(get_db)
):
    """List all series (public, no auth required)"""
    try:
        query = db.query(Series).filter(Series.is_active == True, Series.is_published == True)
        
        # Search filter
        if search:
            query = query.filter(
                or_(
                    Series.title.ilike(f"%{search}%"),
                    Series.title_original.ilike(f"%{search}%"),
                    Series.description.ilike(f"%{search}%")
                )
            )
        
        # Genre filter
        if genre:
            query = query.filter(Series.genre == genre)
        
        # Status filter
        if status:
            query = query.filter(Series.status == status)
        
        # Sorting
        if sort == "popular":
            query = query.order_by(desc(Series.view_count))
        elif sort == "rating":
            query = query.order_by(desc(Series.rating))
        else:  # newest
            query = query.order_by(desc(Series.created_at))
        
        # Get total count
        total = query.count()
        
        # Get series
        series_list = query.offset(skip).limit(limit).all()
        
        return BaseResponse.success_response(
            [SeriesResponse.model_validate(s) for s in series_list],
            f"Found {total} series"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing series: {str(e)}"
        )


@router.get("/public/series/{series_id}", response_model=BaseResponse[dict])
def get_series_detail_public(series_id: int, db: Session = Depends(get_db)):
    """Get series detail with chapters (public, no auth required)"""
    try:
        series = db.query(Series).filter(
            Series.id == series_id,
            Series.is_active == True
        ).first()
        
        if not series:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Series not found"
            )
        
        # Get published chapters
        chapters = db.query(Chapter).filter(
            Chapter.series_id == series_id,
            Chapter.is_published == True
        ).order_by(Chapter.chapter_number).all()
        
        # Get ratings
        ratings = db.query(Rating).filter(Rating.series_id == series_id).all()
        rating_count = len(ratings)
        avg_rating = sum(r.rating for r in ratings) / rating_count if rating_count > 0 else 0
        
        # Get bookmark count (if user is authenticated, show if bookmarked)
        bookmark_count = db.query(func.count()).select_from(
            db.query(Series).filter(Series.id == series_id).subquery()
        ).scalar() or 0
        
        # Build response
        response_data = {
            "series": SeriesResponse.model_validate(series),
            "chapters": [ChapterResponse.model_validate(c) for c in chapters],
            "total_chapters": len(chapters),
            "rating": {
                "average": round(avg_rating, 2),
                "count": rating_count
            },
            "bookmark_count": bookmark_count
        }
        
        return BaseResponse.success_response(
            response_data,
            "Series detail retrieved"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting series detail: {str(e)}"
        )


@router.get("/public/chapters/{chapter_id}", response_model=BaseResponse[dict])
def get_chapter_detail_public(chapter_id: int, db: Session = Depends(get_db)):
    """Get chapter detail with available translations (public, no auth required)"""
    try:
        chapter = db.query(Chapter).filter(
            Chapter.id == chapter_id,
            Chapter.is_published == True
        ).first()
        
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        # Get available translations
        translations = db.query(ChapterTranslation).filter(
            ChapterTranslation.chapter_id == chapter_id,
            ChapterTranslation.is_published == True,
            ChapterTranslation.status == "completed"
        ).all()
        
        # Get comments count
        comment_count = db.query(Comment).filter(
            Comment.chapter_id == chapter_id,
            Comment.is_deleted == False
        ).count()
        
        response_data = {
            "chapter": ChapterResponse.model_validate(chapter),
            "series": {
                "id": chapter.series.id if chapter.series else None,
                "title": chapter.series.title if chapter.series else None
            },
            "available_translations": [
                {
                    "id": t.id,
                    "source_lang": t.source_lang,
                    "target_lang": t.target_lang,
                    "page_count": t.page_count
                }
                for t in translations
            ],
            "comment_count": comment_count,
            "previous_chapter": None,
            "next_chapter": None
        }
        
        # Get previous/next chapters
        if chapter.series:
            prev_chapter = db.query(Chapter).filter(
                Chapter.series_id == chapter.series_id,
                Chapter.chapter_number < chapter.chapter_number,
                Chapter.is_published == True
            ).order_by(desc(Chapter.chapter_number)).first()
            
            next_chapter = db.query(Chapter).filter(
                Chapter.series_id == chapter.series_id,
                Chapter.chapter_number > chapter.chapter_number,
                Chapter.is_published == True
            ).order_by(Chapter.chapter_number).first()
            
            if prev_chapter:
                response_data["previous_chapter"] = {
                    "id": prev_chapter.id,
                    "chapter_number": prev_chapter.chapter_number,
                    "title": prev_chapter.title
                }
            if next_chapter:
                response_data["next_chapter"] = {
                    "id": next_chapter.id,
                    "chapter_number": next_chapter.chapter_number,
                    "title": next_chapter.title
                }
        
        return BaseResponse.success_response(
            response_data,
            "Chapter detail retrieved"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting chapter detail: {str(e)}"
        )


@router.get("/public/chapters/{chapter_id}/read/{translation_id}", response_model=BaseResponse[dict])
def read_chapter_public(
    chapter_id: int,
    translation_id: int,
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db)
):
    """Read a chapter page (public, no auth required)"""
    try:
        translation = db.query(ChapterTranslation).filter(
            ChapterTranslation.id == translation_id,
            ChapterTranslation.chapter_id == chapter_id,
            ChapterTranslation.is_published == True,
            ChapterTranslation.status == "completed"
        ).first()
        
        if not translation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation not found or not published"
            )
        
        # Get chapter info
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        
        # Build page URLs
        from app.services.file_manager import FileManager
        file_manager = FileManager()
        
        # Get storage path
        storage_path = file_manager.get_chapter_path(
            series_name=chapter.series.title if chapter and chapter.series else "Unknown",
            chapter_number=chapter.chapter_number if chapter else 1,
            source_lang=translation.source_lang,
            target_lang=translation.target_lang
        )
        
        if not storage_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter files not found"
            )
        
        # Increment view count
        translation.view_count += 1
        if chapter:
            chapter.view_count += 1
        db.commit()
        
        # Build page list
        import os
        pages = []
        if storage_path.exists():
            for i in range(1, translation.page_count + 1):
                page_file = storage_path / f"page_{i:03d}.jpg"
                if page_file.exists():
                    # Sanitize series name for URL
                    safe_series_name = chapter.series.title.replace(" ", "_") if chapter and chapter.series else "Unknown"
                    pages.append({
                        "page_number": i,
                        "url": f"/api/v1/files/{safe_series_name}/{translation.source_lang}_to_{translation.target_lang}/chapter_{chapter.chapter_number:04d}/page_{i:03d}.jpg"
                    })
        
        return BaseResponse.success_response(
            {
                "chapter_id": chapter_id,
                "translation_id": translation_id,
                "current_page": page,
                "total_pages": translation.page_count,
                "pages": pages,
                "source_lang": translation.source_lang,
                "target_lang": translation.target_lang
            },
            "Chapter pages retrieved"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading chapter: {str(e)}"
        )


@router.get("/public/comments", response_model=BaseResponse[List[CommentResponse]])
def list_comments_public(
    series_id: Optional[int] = Query(None),
    chapter_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List comments (public, no auth required)"""
    try:
        query = db.query(Comment).filter(Comment.is_deleted == False)
        
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
            
            comment_list.append(comment_data)
        
        return BaseResponse.success_response(
            comment_list,
            f"Found {len(comment_list)} comments"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing comments: {str(e)}"
        )

