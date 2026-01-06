"""
Discovery Endpoints - Trending, Featured, Recommendations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import Optional, List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_user_optional
from app.schemas.series import SeriesResponse
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.models.series import Series, Chapter
from app.models.reading import ReadingHistory, Bookmark
from app.models.comment import Comment
from app.models.reaction import Reaction
from app.services.api_cache import api_cache
from app.core.cache_invalidation import CacheInvalidation
from app.core.enums import SeriesStatus

router = APIRouter()


@router.get("/series/trending", response_model=BaseResponse[List[SeriesResponse]])
def get_trending_series(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    period: str = Query("week", regex="^(day|week|month)$"),
    db: Session = Depends(get_db)
):
    """
    Get trending series based on views, ratings, and recent activity
    Period: day, week, month
    """
    try:
        # Check cache
        cache_params = {"skip": skip, "limit": limit, "period": period}
        cached = api_cache.get_cached_response("/api/v1/series/trending", cache_params, ttl=3600)
        if cached:
            return BaseResponse.success_response(
                [SeriesResponse.model_validate(s) for s in cached.get("data", [])],
                cached.get("message", "Trending series")
            )
        
        # Calculate time threshold
        now = datetime.utcnow()
        if period == "day":
            threshold = now - timedelta(days=1)
        elif period == "week":
            threshold = now - timedelta(days=7)
        else:  # month
            threshold = now - timedelta(days=30)
        
        # Get trending series based on:
        # 1. Recent views (weighted by recency)
        # 2. Rating
        # 3. Number of chapters
        # 4. Recent comments/reactions
        
        query = db.query(Series).filter(
            Series.is_active == True,
            Series.is_published == True,
            Series.created_at >= threshold
        )
        
        # Order by trending score (view_count * rating)
        # Get series with chapter counts
        series_list = query.order_by(
            desc(Series.view_count),
            desc(Series.rating)
        ).offset(skip).limit(limit).all()
        
        response_data = [SeriesResponse.model_validate(s) for s in series_list]
        
        # Cache result
        api_cache.set_cached_response(
            "/api/v1/series/trending",
            cache_params,
            {"data": [s.model_dump() for s in response_data], "message": f"Found {len(series_list)} trending series"},
            ttl=3600
        )
        
        return BaseResponse.success_response(
            response_data,
            f"Found {len(series_list)} trending series"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting trending series: {str(e)}"
        )


@router.get("/series/featured", response_model=BaseResponse[List[SeriesResponse]])
def get_featured_series(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get featured series (admin-selected)"""
    try:
        # Check cache
        cache_params = {"skip": skip, "limit": limit}
        cached = api_cache.get_cached_response("/api/v1/series/featured", cache_params, ttl=1800)
        if cached:
            return BaseResponse.success_response(
                [SeriesResponse.model_validate(s) for s in cached.get("data", [])],
                cached.get("message", "Featured series")
            )
        
        query = db.query(Series).filter(
            Series.is_active == True,
            Series.is_published == True,
            Series.is_featured == True
        ).order_by(desc(Series.created_at))
        
        series_list = query.offset(skip).limit(limit).all()
        
        response_data = [SeriesResponse.model_validate(s) for s in series_list]
        
        # Cache result
        api_cache.set_cached_response(
            "/api/v1/series/featured",
            cache_params,
            {"data": [s.model_dump() for s in response_data], "message": f"Found {len(series_list)} featured series"},
            ttl=1800
        )
        
        return BaseResponse.success_response(
            response_data,
            f"Found {len(series_list)} featured series"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting featured series: {str(e)}"
        )


@router.get("/series/recommendations", response_model=BaseResponse[List[SeriesResponse]])
def get_recommendations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get personalized recommendations based on:
    - User's reading history
    - User's bookmarks
    - Similar genres
    - Popular series in user's preferred genres
    """
    try:
        # Check cache (if user is logged in, cache per user)
        cache_params = {
            "skip": skip,
            "limit": limit,
            "user_id": current_user.id if current_user else None
        }
        cache_key = f"/api/v1/series/recommendations/{current_user.id if current_user else 'guest'}"
        cached = api_cache.get_cached_response(cache_key, cache_params, ttl=1800)
        if cached:
            return BaseResponse.success_response(
                [SeriesResponse.model_validate(s) for s in cached.get("data", [])],
                cached.get("message", "Recommendations")
            )
        
        if current_user:
            # Get user's reading history genres
            history = db.query(ReadingHistory).filter(
                ReadingHistory.user_id == current_user.id
            ).all()
            
            # Get user's bookmarked series
            bookmarks = db.query(Bookmark).filter(
                Bookmark.user_id == current_user.id
            ).all()
            
            # Collect genres from history and bookmarks
            preferred_genres = set()
            for h in history:
                if h.series and h.series.genre:
                    preferred_genres.add(h.series.genre)
            for b in bookmarks:
                if b.series and b.series.genre:
                    preferred_genres.add(b.series.genre)
            
            # Get series in preferred genres that user hasn't read
            read_series_ids = {h.series_id for h in history}
            bookmarked_series_ids = {b.series_id for b in bookmarks}
            excluded_ids = read_series_ids | bookmarked_series_ids
            
            if preferred_genres:
                query = db.query(Series).filter(
                    Series.is_active == True,
                    Series.is_published == True,
                    Series.genre.in_(list(preferred_genres)),
                    ~Series.id.in_(list(excluded_ids)) if excluded_ids else True
                ).order_by(
                    desc(Series.rating),
                    desc(Series.view_count)
                )
            else:
                # No preferences yet, show popular series
                query = db.query(Series).filter(
                    Series.is_active == True,
                    Series.is_published == True
                ).order_by(desc(Series.view_count))
        else:
            # Guest user - show popular series
            query = db.query(Series).filter(
                Series.is_active == True,
                Series.is_published == True
            ).order_by(desc(Series.view_count), desc(Series.rating))
        
        series_list = query.offset(skip).limit(limit).all()
        
        response_data = [SeriesResponse.model_validate(s) for s in series_list]
        
        # Cache result
        api_cache.set_cached_response(
            cache_key,
            cache_params,
            {"data": [s.model_dump() for s in response_data], "message": f"Found {len(series_list)} recommendations"},
            ttl=1800
        )
        
        return BaseResponse.success_response(
            response_data,
            f"Found {len(series_list)} recommendations"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recommendations: {str(e)}"
        )


@router.get("/series/popular", response_model=BaseResponse[List[SeriesResponse]])
def get_popular_series(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    period: str = Query("all", regex="^(day|week|month|all)$"),
    db: Session = Depends(get_db)
):
    """
    Get popular series based on views
    Period: day, week, month, all
    """
    try:
        # Check cache
        cache_params = {"skip": skip, "limit": limit, "period": period}
        cached = api_cache.get_cached_response("/api/v1/series/popular", cache_params, ttl=3600)
        if cached:
            return BaseResponse.success_response(
                [SeriesResponse.model_validate(s) for s in cached.get("data", [])],
                cached.get("message", "Popular series")
            )
        
        query = db.query(Series).filter(
            Series.is_active == True,
            Series.is_published == True
        )
        
        if period != "all":
            now = datetime.utcnow()
            if period == "day":
                threshold = now - timedelta(days=1)
            elif period == "week":
                threshold = now - timedelta(days=7)
            else:  # month
                threshold = now - timedelta(days=30)
            query = query.filter(Series.created_at >= threshold)
        
        series_list = query.order_by(desc(Series.view_count)).offset(skip).limit(limit).all()
        
        response_data = [SeriesResponse.model_validate(s) for s in series_list]
        
        # Cache result
        api_cache.set_cached_response(
            "/api/v1/series/popular",
            cache_params,
            {"data": [s.model_dump() for s in response_data], "message": f"Found {len(series_list)} popular series"},
            ttl=3600
        )
        
        return BaseResponse.success_response(
            response_data,
            f"Found {len(series_list)} popular series"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting popular series: {str(e)}"
        )


@router.get("/series/newest", response_model=BaseResponse[List[SeriesResponse]])
def get_newest_series(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get newest series"""
    try:
        # Check cache
        cache_params = {"skip": skip, "limit": limit}
        cached = api_cache.get_cached_response("/api/v1/series/newest", cache_params, ttl=600)
        if cached:
            return BaseResponse.success_response(
                [SeriesResponse.model_validate(s) for s in cached.get("data", [])],
                cached.get("message", "Newest series")
            )
        
        query = db.query(Series).filter(
            Series.is_active == True,
            Series.is_published == True
        ).order_by(desc(Series.created_at))
        
        series_list = query.offset(skip).limit(limit).all()
        
        response_data = [SeriesResponse.model_validate(s) for s in series_list]
        
        # Cache result
        api_cache.set_cached_response(
            "/api/v1/series/newest",
            cache_params,
            {"data": [s.model_dump() for s in response_data], "message": f"Found {len(series_list)} newest series"},
            ttl=600
        )
        
        return BaseResponse.success_response(
            response_data,
            f"Found {len(series_list)} newest series"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting newest series: {str(e)}"
        )


@router.get("/series/genres", response_model=BaseResponse[List[dict]])
def get_available_genres(db: Session = Depends(get_db)):
    """Get list of available genres with counts"""
    try:
        # Check cache
        cached = api_cache.get_cached_response("/api/v1/series/genres", {}, ttl=3600)
        if cached:
            return BaseResponse.success_response(
                cached.get("data", []),
                cached.get("message", "Genres")
            )
        
        # Get distinct genres with counts
        genres = db.query(
            Series.genre,
            func.count(Series.id).label('count')
        ).filter(
            Series.is_active == True,
            Series.is_published == True,
            Series.genre.isnot(None)
        ).group_by(Series.genre).order_by(desc('count')).all()
        
        genre_list = [{"name": genre, "count": count} for genre, count in genres]
        
        # Cache result
        api_cache.set_cached_response(
            "/api/v1/series/genres",
            {},
            {"data": genre_list, "message": f"Found {len(genre_list)} genres"},
            ttl=3600
        )
        
        return BaseResponse.success_response(
            genre_list,
            f"Found {len(genre_list)} genres"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting genres: {str(e)}"
        )


@router.get("/tags", response_model=BaseResponse[dict])
def get_available_tags():
    """Get all available tags from enum (cached)"""
    try:
        from app.core.tag_enum import WebtoonTag
        
        # Check cache
        cached = api_cache.get_cached_response("/api/v1/tags", {}, ttl=86400)  # 24 hours
        if cached:
            return BaseResponse.success_response(
                cached.get("data", {}),
                cached.get("message", "Tags")
            )
        
        # Get all tags from enum
        all_tags = WebtoonTag.get_all_tags()
        genre_tags = WebtoonTag.get_genre_tags()
        webtoon_specific_tags = WebtoonTag.get_webtoon_specific_tags()
        
        # Organize by category
        tags_data = {
            "all_tags": all_tags,
            "genre_tags": genre_tags,
            "webtoon_specific_tags": webtoon_specific_tags,
            "total_count": len(all_tags)
        }
        
        # Cache result
        api_cache.set_cached_response(
            "/api/v1/tags",
            {},
            {"data": tags_data, "message": f"Found {len(all_tags)} tags"},
            ttl=86400
        )
        
        return BaseResponse.success_response(
            tags_data,
            f"Found {len(all_tags)} available tags"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting tags: {str(e)}"
        )


@router.get("/tags/validate", response_model=BaseResponse[dict])
def validate_tags(tag_names: List[str] = Query(..., description="List of tag names to validate")):
    """Validate tag names against enum"""
    try:
        from app.core.tag_enum import WebtoonTag
        
        validated_tags = []
        invalid_tags = []
        
        for tag_name in tag_names:
            normalized = WebtoonTag.normalize_tag(tag_name)
            if normalized:
                validated_tags.append({
                    "original": tag_name,
                    "normalized": normalized,
                    "valid": True
                })
            else:
                invalid_tags.append({
                    "original": tag_name,
                    "valid": False
                })
        
        return BaseResponse.success_response(
            {
                "valid_tags": validated_tags,
                "invalid_tags": invalid_tags,
                "total_valid": len(validated_tags),
                "total_invalid": len(invalid_tags)
            },
            f"Validated {len(tag_names)} tags"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating tags: {str(e)}"
        )

