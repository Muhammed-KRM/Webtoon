"""
Translation Publisher - Auto-publish completed translations with improved error handling
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from loguru import logger
from app.models.series import Series, Chapter, ChapterTranslation
from app.models.job import TranslationJob
from app.services.file_manager import FileManager
from app.services.notification_service import NotificationService
from app.services.series_manager import SeriesManager
from app.core.database import SessionLocal
from app.core.enums import TranslationStatus
from pathlib import Path
import base64
import re


def extract_chapter_number_from_url(chapter_url: str) -> Optional[int]:
    """Extract chapter number from URL"""
    if not chapter_url:
        return None
    
    # Try to find chapter number in URL
    # Common patterns: episode-123, chapter-123, ch123, ep123, /123/
    patterns = [
        r'episode[_-]?(\d+)',
        r'chapter[_-]?(\d+)',
        r'ch[_-]?(\d+)',
        r'ep[_-]?(\d+)',
        r'/(\d+)/',
        r'#(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, chapter_url, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue
    
    return None


def publish_translation_on_completion(
    task_id: str,
    result: Dict[str, Any],
    chapter_url: str,
    source_lang: str,
    target_lang: str,
    series_name: Optional[str] = None,
    series_description: Optional[str] = None,
    category_id: Optional[int] = None,
    tags: Optional[List[str]] = None,
    replace_existing_chapters: bool = True
):
    """
    Automatically publish translation when job completes
    
    This function handles:
    - Series creation/matching (exact name matching)
    - Chapter creation/updating (handles conflicts)
    - Translation creation/updating (replaces existing if replace_existing_chapters=True)
    - Full transaction rollback on any error
    - File cleanup on failure
    
    Args:
        task_id: Celery task ID
        result: Translation result dictionary
        chapter_url: Chapter source URL
        source_lang: Source language
        target_lang: Target language
        series_name: Series name (required for auto-publish)
        series_description: Series description (required if creating new series)
        category_id: Category ID (optional)
        tags: List of tag names (optional)
        replace_existing_chapters: If True, replace existing chapters/translations
    """
    db = SessionLocal()
    file_manager = FileManager()
    storage_path = None
    saved_files = False
    
    try:
        # Validate required fields
        if not series_name or not series_name.strip():
            logger.warning(f"Series name not provided. Cannot auto-publish translation for task {task_id}")
            return
        
        # Find the translation job
        job = db.query(TranslationJob).filter(
            TranslationJob.task_id == task_id
        ).first()
        
        if not job:
            logger.warning(f"Translation job not found: {task_id}")
            return
        
        # Extract chapter number from URL if possible
        chapter_number = extract_chapter_number_from_url(chapter_url)
        if not chapter_number:
            # Try to get from result metadata
            chapter_number = result.get("chapter_number")
        if not chapter_number:
            logger.warning(f"Could not extract chapter number from URL: {chapter_url}")
            # Fallback: use 1 or get from existing chapters
            chapter_number = 1
        
        # Step 1: Find or create series
        series, is_new_series = SeriesManager.create_or_get_series(
            db=db,
            title=series_name.strip(),
            description=series_description or f"Translated series: {series_name}",
            source_url=None,  # Can be set later
            source_site=None,  # Can be set later
            category_id=category_id,
            tags=tags
        )
        
        if not series:
            raise ValueError(f"Failed to create or find series: {series_name}")
        
        logger.info(f"Using series: {series.id} - {series.title} (new: {is_new_series})")
        
        # Step 2: Save translation files
        pages_data = result.get("pages", [])
        cleaned_pages_data = result.get("cleaned_pages", [])  # Get cleaned pages
        
        if not pages_data:
            raise ValueError("No pages data in translation result")
        
        try:
            pages_bytes = [base64.b64decode(page) for page in pages_data]
            
            # Decode cleaned pages if available
            cleaned_pages_bytes = []
            if cleaned_pages_data:
                cleaned_pages_bytes = [
                    base64.b64decode(page) if page else None 
                    for page in cleaned_pages_data
                ]
            
            metadata = {
                "original_texts": result.get("original_texts", []),
                "translated_texts": result.get("translated_texts", []),
                "blocks": result.get("blocks", []),
                "chapter_url": chapter_url,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "task_id": task_id
            }
            
            storage_path = file_manager.save_chapter(
                series_name=series.title,
                chapter_number=chapter_number,
                pages=pages_bytes,
                metadata=metadata,
                source_lang=source_lang,
                target_lang=target_lang,
                cleaned_pages=cleaned_pages_bytes  # Pass cleaned pages
            )
            
            if not storage_path:
                raise ValueError("Failed to save chapter files")
            
            saved_files = True
            logger.info(f"Saved translation files to: {storage_path}")
            
        except Exception as e:
            logger.error(f"Error saving translation files: {e}", exc_info=True)
            raise
        
        # Step 3: Create or update chapter
        chapter, is_new_chapter = SeriesManager.create_or_update_chapter(
            db=db,
            series_id=series.id,
            chapter_number=chapter_number,
            source_url=chapter_url,
            title=result.get("chapter_title") or f"Chapter {chapter_number}",
            page_count=result.get("total", len(pages_bytes)),
            replace_existing=replace_existing_chapters
        )
        
        if not chapter:
            raise ValueError(f"Failed to create or update chapter {chapter_number}")
        
        logger.info(f"Using chapter: {chapter.id} - Chapter {chapter_number} (new: {is_new_chapter})")
        
        # Step 4: Create or update translation
        translation_data = {
            "storage_path": str(storage_path),
            "page_count": result.get("total", len(pages_bytes))
        }
        
        translation = SeriesManager.handle_chapter_conflict(
            db=db,
            chapter=chapter,
            new_translation_data=translation_data,
            source_lang=source_lang,
            target_lang=target_lang,
            replace_existing=replace_existing_chapters
        )
        
        # Update translation job ID
        translation.translation_job_id = task_id
        
        # Commit all changes
        db.commit()
        logger.info(f"Successfully published translation for chapter {chapter.id} ({source_lang}->{target_lang})")
        
        # Step 5: Invalidate cache
        try:
            from app.core.cache_invalidation import CacheInvalidation
            CacheInvalidation.invalidate_chapter_cache(chapter_id=chapter.id)
            CacheInvalidation.invalidate_series_cache(series_id=series.id)
        except Exception as e:
            logger.warning(f"Error invalidating cache: {e}")
        
        # Step 6: Send notification
        if job.user_id:
            try:
                NotificationService.notify_translation_completed(
                    db=db,
                    user_id=job.user_id,
                    chapter_id=chapter.id,
                    series_title=series.title,
                    target_lang=target_lang
                )
            except Exception as e:
                logger.warning(f"Error sending notification: {e}")
        
    except Exception as e:
        logger.error(f"Error publishing translation: {e}", exc_info=True)
        
        # Rollback database transaction
        try:
            db.rollback()
            logger.info("Database transaction rolled back")
        except Exception as rollback_error:
            logger.error(f"Error during rollback: {rollback_error}", exc_info=True)
        
        # Clean up saved files if any
        if saved_files and storage_path:
            try:
                storage_path_obj = Path(storage_path)
                if storage_path_obj.exists() and storage_path_obj.is_dir():
                    import shutil
                    shutil.rmtree(storage_path_obj)
                    logger.info(f"Cleaned up translation files: {storage_path}")
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up files: {cleanup_error}", exc_info=True)
        
        # Re-raise to ensure task is marked as failed
        raise
    
    finally:
        try:
            db.close()
        except Exception as e:
            logger.warning(f"Error closing database session: {e}")
