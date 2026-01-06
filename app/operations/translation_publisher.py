"""
Translation Publisher - Auto-publish completed translations
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from loguru import logger
from app.models.series import Series, Chapter, ChapterTranslation
from app.models.job import TranslationJob
from app.services.file_manager import FileManager
from app.services.notification_service import NotificationService
from app.core.database import SessionLocal


def publish_translation_on_completion(
    task_id: str,
    result: Dict[str, Any],
    chapter_url: str,
    source_lang: str,
    target_lang: str,
    series_name: Optional[str] = None
):
    """
    Automatically publish translation when job completes
    
    This function should be called when translation job completes
    """
    db = SessionLocal()
    try:
        # Find the translation job
        job = db.query(TranslationJob).filter(
            TranslationJob.task_id == task_id
        ).first()
        
        if not job:
            logger.warning(f"Translation job not found: {task_id}")
            return
        
        # Try to find or create chapter
        chapter = None
        if series_name:
            # Find series by name
            series = db.query(Series).filter(
                Series.title.ilike(f"%{series_name}%")
            ).first()
            
            if series:
                # Try to find chapter by URL
                chapter = db.query(Chapter).filter(
                    Chapter.series_id == series.id,
                    Chapter.source_url == chapter_url
                ).first()
        
        # If chapter not found, we can't publish
        if not chapter:
            logger.warning(f"Chapter not found for URL: {chapter_url}. Cannot auto-publish.")
            return
        
        # Check if translation already exists
        existing = db.query(ChapterTranslation).filter(
            ChapterTranslation.chapter_id == chapter.id,
            ChapterTranslation.source_lang == source_lang,
            ChapterTranslation.target_lang == target_lang
        ).first()
        
        if existing:
            logger.info(f"Translation already exists for chapter {chapter.id}")
            # Update existing
            existing.status = "completed"
            existing.is_published = True
            existing.page_count = result.get("total", 0)
        else:
            # Create new translation
            # Get storage path from file manager
            file_manager = FileManager()
            storage_path = file_manager.get_chapter_path(
                series_name=series_name or chapter.series.title,
                chapter_number=chapter.chapter_number,
                source_lang=source_lang,
                target_lang=target_lang
            )
            
            if not storage_path:
                # Save files if not already saved
                pages_data = result.get("pages", [])
                if pages_data:
                    import base64
                    pages_bytes = [base64.b64decode(page) for page in pages_data]
                    metadata = {
                        "original_texts": result.get("original_texts", []),
                        "translated_texts": result.get("translated_texts", []),
                        "blocks": result.get("blocks", [])
                    }
                    
                    storage_path = file_manager.save_chapter(
                        series_name=series_name or chapter.series.title,
                        chapter_number=chapter.chapter_number,
                        pages=pages_bytes,
                        metadata=metadata,
                        source_lang=source_lang,
                        target_lang=target_lang
                    )
            
            new_translation = ChapterTranslation(
                chapter_id=chapter.id,
                source_lang=source_lang,
                target_lang=target_lang,
                storage_path=str(storage_path) if storage_path else "",
                page_count=result.get("total", 0),
                translation_job_id=task_id,
                status="completed",
                is_published=True
            )
            db.add(new_translation)
            existing = new_translation
        
        db.commit()
        
        # Invalidate cache (new translation completed)
        from app.core.cache_invalidation import CacheInvalidation
        CacheInvalidation.invalidate_chapter_cache(
            chapter_id=chapter.id,
            series_id=chapter.series_id if chapter.series else None
        )
        
        # Send notification to user
        if job.user_id:
            try:
                NotificationService.notify_translation_completed(
                    db=db,
                    user_id=job.user_id,
                    chapter_id=chapter.id,
                    series_title=chapter.series.title if chapter.series else series_name or "Unknown",
                    target_lang=target_lang
                )
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
        
        logger.info(f"Translation published for chapter {chapter.id}: {source_lang} -> {target_lang}")
        
    except Exception as e:
        logger.error(f"Error publishing translation: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

