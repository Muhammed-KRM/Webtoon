"""
File Serving Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path
from app.core.config import settings
from app.core.security import get_current_active_user, get_current_user_optional
from typing import Optional
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.services.file_manager import FileManager
from loguru import logger

router = APIRouter()
file_manager = FileManager()


@router.get("/{series_name}/{source_lang}_to_{target_lang}/chapter_{chapter_number:04d}/page_{page_number:03d}.jpg")
def get_page_image(
    series_name: str,
    source_lang: str,
    target_lang: str,
    chapter_number: int,
    page_number: int,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get a specific page image from translated chapter (public, auth optional)"""
    try:
        # Get chapter path
        chapter_path = file_manager.get_chapter_path(
            series_name=series_name,
            chapter_number=chapter_number,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        if not chapter_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        # Build page path
        page_path = chapter_path / f"page_{page_number:03d}.jpg"
        
        if not page_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found"
            )
        
        return FileResponse(
            path=str(page_path),
            media_type="image/jpeg",
            filename=f"page_{page_number:03d}.jpg"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error serving file: {str(e)}"
        )


@router.get("/{series_name}/chapters")
def list_chapters(
    series_name: str,
    source_lang: str,
    target_lang: str,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """List available chapters for a series (public, auth optional)"""
    try:
        chapters = file_manager.list_chapters(
            series_name=series_name,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        return BaseResponse.success_response(
            {
                "series_name": series_name,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "chapters": chapters,
                "total": len(chapters)
            },
            "Chapters listed"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing chapters: {str(e)}"
        )

