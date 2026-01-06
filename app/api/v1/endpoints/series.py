"""
Series Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_active_user, require_admin
from app.schemas.series import (
    SeriesCreate, SeriesUpdate, SeriesResponse,
    ChapterCreate, ChapterResponse, ChapterTranslationResponse
)
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.models.series import Series, Chapter, ChapterTranslation
from app.models.subscription import Subscription
from app.services.file_manager import FileManager
from app.services.api_cache import api_cache
from app.core.query_optimizer import QueryOptimizer
from app.core.cache_invalidation import CacheInvalidation
from app.core.enums import TranslateType, TranslationStatus, SeriesStatus
from sqlalchemy.orm import joinedload, selectinload

router = APIRouter()


@router.get("/series", response_model=BaseResponse[List[SeriesResponse]])
def list_series(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    genre: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all series with pagination and filters (public, cached)"""
    try:
        # Check cache
        cache_params = {
            "skip": skip,
            "limit": limit,
            "search": search,
            "genre": genre,
            "status": status
        }
        cached = api_cache.get_cached_response("/api/v1/series", cache_params, ttl=300)
        if cached:
            return BaseResponse.success_response(
                [SeriesResponse.model_validate(s) for s in cached.get("data", [])],
                cached.get("message", "Found series")
            )
        
        query = db.query(Series).filter(
            Series.is_active == True,
            Series.is_published == True
        )
        
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
            # status is already validated as SeriesStatus enum value
            query = query.filter(Series.status == status)
        
        # Get total count
        total = query.count()
        
        # Get series
        series_list = query.order_by(desc(Series.created_at)).offset(skip).limit(limit).all()
        
        # Convert to response format
        response_data = [SeriesResponse.model_validate(s) for s in series_list]
        
        # Cache result
        api_cache.set_cached_response(
            "/api/v1/series",
            cache_params,
            {"data": [s.model_dump() for s in response_data], "total": total, "message": f"Found {total} series"},
            ttl=300
        )
        
        return BaseResponse.success_response(
            response_data,
            f"Found {total} series"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing series: {str(e)}"
        )


@router.get("/series/{series_id}", response_model=BaseResponse[SeriesResponse])
def get_series(series_id: int, db: Session = Depends(get_db)):
    """Get series details (public, cached)"""
    # Check cache
    cache_params = {"series_id": series_id}
    cached = api_cache.get_cached_response(f"/api/v1/series/{series_id}", cache_params, ttl=600)
    if cached:
        return BaseResponse.success_response(
            SeriesResponse.model_validate(cached.get("data")),
            cached.get("message", "Series retrieved")
        )
    
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.is_active == True
    ).first()
    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )
    
    # Increment view count (async, don't block)
    series.view_count += 1
    db.commit()
    
    response_data = SeriesResponse.model_validate(series)
    
    # Cache result
    api_cache.set_cached_response(
        f"/api/v1/series/{series_id}",
        cache_params,
        {"data": response_data.model_dump(), "message": "Series retrieved"},
        ttl=600
    )
    
    return BaseResponse.success_response(
        response_data,
        "Series retrieved"
    )


@router.post("/series", response_model=BaseResponse[SeriesResponse])
def create_series(
    series_data: SeriesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new series (Admin only)"""
    try:
        from app.services.series_manager import SeriesManager
        
        # Validate description
        if not series_data.description or not series_data.description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Series description is required"
            )
        
        # Use SeriesManager to create or get series (handles duplicates)
        series, is_new = SeriesManager.create_or_get_series(
            db=db,
            title=series_data.title,
            description=series_data.description,
            source_url=series_data.source_url,
            source_site=series_data.source_site,
            author=series_data.author,
            cover_image_url=series_data.cover_image_url,
            category_id=series_data.category_id,
            tags=series_data.tags,
            genre=series_data.genre
        )
        
        # Invalidate cache
        CacheInvalidation.invalidate_series_cache()
        
        message = "Series created successfully" if is_new else "Series already exists, updated metadata"
        
        return BaseResponse.success_response(
            SeriesResponse.model_validate(series),
            message
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating series: {str(e)}"
        )


@router.put("/series/{series_id}", response_model=BaseResponse[SeriesResponse])
def update_series(
    series_id: int,
    series_data: SeriesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a series (Admin only)"""
    try:
        series = db.query(Series).filter(Series.id == series_id).first()
        if not series:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Series not found"
            )
        
        # Update fields
        update_data = series_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(series, field, value)
        
        db.commit()
        db.refresh(series)
        
        # Invalidate cache
        CacheInvalidation.invalidate_series_cache(series_id)
        
        return BaseResponse.success_response(
            SeriesResponse.model_validate(series),
            "Series updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating series: {str(e)}"
        )


@router.delete("/series/{series_id}", response_model=BaseResponse[dict])
def delete_series(
    series_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a series (Admin only) - Soft delete by setting is_active=False"""
    try:
        series = db.query(Series).filter(Series.id == series_id).first()
        if not series:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Series not found"
            )
        
        # Soft delete
        series.is_active = False
        series.is_published = False
        db.commit()
        
        # Invalidate cache
        CacheInvalidation.invalidate_series_cache(series_id)
        
        return BaseResponse.success_response(
            {"series_id": series_id, "deleted": True},
            "Series deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting series: {str(e)}"
        )


@router.get("/series/{series_id}/chapters", response_model=BaseResponse[List[ChapterResponse]])
def list_chapters(
    series_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List chapters for a series (public, cached)"""
    try:
        # Check cache
        cache_params = {"series_id": series_id, "skip": skip, "limit": limit}
        cached = api_cache.get_cached_response(f"/api/v1/series/{series_id}/chapters", cache_params, ttl=300)
        if cached:
            return BaseResponse.success_response(
                [ChapterResponse.model_validate(c) for c in cached.get("data", [])],
                cached.get("message", "Found chapters")
            )
        
        # Optimize query
        chapters = db.query(Chapter).options(
            selectinload(Chapter.translations),
            joinedload(Chapter.series)
        ).filter(
            Chapter.series_id == series_id,
            Chapter.is_published == True
        ).order_by(Chapter.chapter_number).offset(skip).limit(limit).all()
        
        response_data = [ChapterResponse.model_validate(c) for c in chapters]
        
        # Cache result
        api_cache.set_cached_response(
            f"/api/v1/series/{series_id}/chapters",
            cache_params,
            {"data": [c.model_dump() for c in response_data], "message": f"Found {len(chapters)} chapters"},
            ttl=300
        )
        
        return BaseResponse.success_response(
            response_data,
            f"Found {len(chapters)} chapters"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing chapters: {str(e)}"
        )


@router.get("/chapters/{chapter_id}/translations", response_model=BaseResponse[List[ChapterTranslationResponse]])
def get_chapter_translations(
    chapter_id: int,
    source_lang: Optional[str] = None,
    target_lang: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get available translations for a chapter (public, cached)"""
    try:
        # Check cache
        cache_params = {"chapter_id": chapter_id, "source_lang": source_lang, "target_lang": target_lang}
        cached = api_cache.get_cached_response(f"/api/v1/chapters/{chapter_id}/translations", cache_params, ttl=600)
        if cached:
            return BaseResponse.success_response(
                [ChapterTranslationResponse.model_validate(t) for t in cached.get("data", [])],
                cached.get("message", "Translations retrieved")
            )
        
        query = db.query(ChapterTranslation).filter(
            ChapterTranslation.chapter_id == chapter_id,
            ChapterTranslation.is_published == True,
            ChapterTranslation.status == TranslationStatus.COMPLETED
        )
        
        if source_lang:
            query = query.filter(ChapterTranslation.source_lang == source_lang)
        if target_lang:
            query = query.filter(ChapterTranslation.target_lang == target_lang)
        
        translations = query.all()
        
        response_data = [ChapterTranslationResponse.model_validate(t) for t in translations]
        
        # Cache result
        api_cache.set_cached_response(
            f"/api/v1/chapters/{chapter_id}/translations",
            cache_params,
            {"data": [t.model_dump() for t in response_data], "message": f"Found {len(translations)} translations"},
            ttl=600
        )
        
        return BaseResponse.success_response(
            response_data,
            f"Found {len(translations)} translations"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting translations: {str(e)}"
        )


@router.post("/chapters/{chapter_id}/translate", response_model=BaseResponse[dict])
def request_chapter_translation(
    chapter_id: int,
    target_lang: str,
    translate_type: int = Query(1, description="1 = AI (OpenAI GPT-4o-mini), 2 = Free (Google Translate/DeepL)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Request translation for a chapter (Premium feature)"""
    try:
        # Check if user has premium subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.is_active == True
        ).first()
        
        if not subscription or subscription.plan_type != "premium":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Premium subscription required"
            )
        
        # Get chapter
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        # Check if translation already exists
        existing = db.query(ChapterTranslation).filter(
            ChapterTranslation.chapter_id == chapter_id,
            ChapterTranslation.target_lang == target_lang,
            ChapterTranslation.status == TranslationStatus.COMPLETED
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Translation already exists"
            )
        
        # Check chapter limit
        if subscription.monthly_chapter_limit > 0:
            if subscription.used_chapters_this_month >= subscription.monthly_chapter_limit:
                # Calculate extra cost
                extra_chapters = 1
                cost = float(subscription.price_per_extra_chapter) * extra_chapters
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=f"Monthly limit reached. Cost for {extra_chapters} extra chapter(s): ${cost:.2f}"
                )
        
        # Create ChapterTranslation record
        chapter_translation = ChapterTranslation(
            chapter_id=chapter.id,
            source_lang="en",  # Detect from chapter
            target_lang=target_lang,
            storage_path="",  # Will be set when translation completes
            status="pending",
            translation_job_id=""
        )
        db.add(chapter_translation)
        
        # Validate translate_type
        if translate_type not in [TranslateType.AI, TranslateType.FREE]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"translate_type must be {TranslateType.AI} (AI) or {TranslateType.FREE} (Free)"
            )
        
        # Start translation task
        from app.operations.translation_manager import process_chapter_task
        
        task = process_chapter_task.delay(
            chapter_url=chapter.source_url or "",
            target_lang=target_lang,
            source_lang="en",
            mode="clean",
            use_cache=(translate_type == TranslateType.AI),  # Use Cached Input only for AI
            series_name=chapter.series.title if chapter.series else None,
            translate_type=translate_type
        )
        
        # Update ChapterTranslation with task ID
        chapter_translation.translation_job_id = task.id
        
        # Update subscription usage
        subscription.used_chapters_this_month += 1
        
        db.commit()
        
        return BaseResponse.success_response(
            {
                "chapter_id": chapter_id,
                "target_lang": target_lang,
                "task_id": task.id,
                "translation_id": chapter_translation.id
            },
            "Translation requested. Will be processed and published automatically."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error requesting translation: {str(e)}"
        )


@router.put("/chapters/{chapter_id}", response_model=BaseResponse[ChapterResponse])
def update_chapter(
    chapter_id: int,
    chapter_data: ChapterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a chapter (Admin only)"""
    try:
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        # Update fields
        update_data = chapter_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != "series_id":  # Don't allow changing series_id
                setattr(chapter, field, value)
        
        db.commit()
        db.refresh(chapter)
        
        # Invalidate cache
        CacheInvalidation.invalidate_chapter_cache(chapter_id)
        CacheInvalidation.invalidate_series_cache(chapter.series_id)
        
        return BaseResponse.success_response(
            ChapterResponse.model_validate(chapter),
            "Chapter updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating chapter: {str(e)}"
        )


@router.delete("/chapters/{chapter_id}", response_model=BaseResponse[dict])
def delete_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a chapter (Admin only) - Soft delete by setting is_published=False"""
    try:
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        # Soft delete
        chapter.is_published = False
        db.commit()
        
        # Invalidate cache
        CacheInvalidation.invalidate_chapter_cache(chapter_id)
        CacheInvalidation.invalidate_series_cache(chapter.series_id)
        
        return BaseResponse.success_response(
            {"chapter_id": chapter_id, "deleted": True},
            "Chapter deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting chapter: {str(e)}"
        )


@router.post("/chapters/{chapter_id}/publish", response_model=BaseResponse[dict])
def publish_chapter(
    chapter_id: int,
    publish: bool = Query(True, description="True to publish, False to unpublish"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Publish or unpublish a chapter (Admin only)"""
    try:
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        chapter.is_published = publish
        if publish:
            chapter.published_at = datetime.utcnow()
        db.commit()
        
        # Invalidate cache
        CacheInvalidation.invalidate_chapter_cache(chapter_id)
        CacheInvalidation.invalidate_series_cache(chapter.series_id)
        
        return BaseResponse.success_response(
            {
                "chapter_id": chapter_id,
                "is_published": publish
            },
            f"Chapter {'published' if publish else 'unpublished'} successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating chapter publish status: {str(e)}"
        )


@router.post("/chapters/{chapter_id}/translations/{translation_id}/publish", response_model=BaseResponse[dict])
def publish_translation(
    chapter_id: int,
    translation_id: int,
    publish: bool = Query(True, description="True to publish, False to unpublish"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Publish or unpublish a translation (Admin only)"""
    try:
        translation = db.query(ChapterTranslation).filter(
            ChapterTranslation.id == translation_id,
            ChapterTranslation.chapter_id == chapter_id
        ).first()
        
        if not translation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation not found"
            )
        
        translation.is_published = publish
        db.commit()
        
        # Invalidate cache
        CacheInvalidation.invalidate_chapter_cache(chapter_id)
        
        return BaseResponse.success_response(
            {
                "translation_id": translation_id,
                "is_published": publish
            },
            f"Translation {'published' if publish else 'unpublished'} successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating translation publish status: {str(e)}"
        )

