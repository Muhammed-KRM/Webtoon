"""
Batch Translation Manager - Handles multiple chapter translations
"""
from celery import Celery
from typing import List, Dict, Optional
from loguru import logger
from app.core.config import settings
from app.operations.translation_manager import celery_app, process_chapter_task
from app.services.url_generator import URLGenerator
from app.services.language_detector import LanguageDetector
from app.services.file_manager import FileManager


@celery_app.task(bind=True, name="batch_translation_task")
def batch_translation_task(
    self,
    base_url: str,
    chapter_numbers: List[int],
    source_lang: str = "en",
    target_lang: str = "tr",
    mode: str = "clean",
    series_name: Optional[str] = None
) -> Dict:
    """
    Process multiple chapters in batch
    
    Args:
        base_url: Base URL pattern
        chapter_numbers: List of chapter numbers to translate
        source_lang: Source language code
        target_lang: Target language code
        mode: Processing mode
        series_name: Series name for organization
        
    Returns:
        Dictionary with results for each chapter
    """
    try:
        # Validate language pair
        is_valid, error_msg = LanguageDetector.validate_language_pair(source_lang, target_lang)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Generate URLs for all chapters
        chapter_urls = URLGenerator.generate_chapter_urls(base_url, chapter_numbers)
        
        total_chapters = len(chapter_urls)
        results = {}
        completed = 0
        failed = 0
        
        logger.info(f"Starting batch translation: {total_chapters} chapters")
        
        # Process each chapter
        for idx, (chapter_num, chapter_url) in enumerate(zip(chapter_numbers, chapter_urls)):
            try:
                self.update_state(
                    state='PROCESSING',
                    meta={
                        'progress': int((idx / total_chapters) * 100),
                        'message': f'Processing chapter {chapter_num}/{chapter_numbers[-1]}...',
                        'current_chapter': chapter_num,
                        'total_chapters': total_chapters
                    }
                )
                
                logger.info(f"Processing chapter {chapter_num}: {chapter_url}")
                
                # Start translation task for this chapter
                task = process_chapter_task.delay(
                    chapter_url=chapter_url,
                    target_lang=target_lang,
                    mode=mode,
                    use_cache=True
                )
                
                # Wait for completion
                task_result = task.get(timeout=600)  # 10 minute timeout per chapter
                
                # Save to file system if series_name provided
                if series_name and task_result:
                    try:
                        file_manager = FileManager()
                        pages_data = task_result.get("pages", [])
                        # Convert base64 to bytes
                        import base64
                        pages_bytes = [base64.b64decode(page) for page in pages_data]
                        
                        metadata = {
                            "original_texts": task_result.get("original_texts", []),
                            "translated_texts": task_result.get("translated_texts", []),
                            "blocks": task_result.get("blocks", []),
                            "source_lang": source_lang,
                            "target_lang": target_lang
                        }
                        
                        file_manager.save_chapter(
                            series_name=series_name,
                            chapter_number=chapter_num,
                            pages=pages_bytes,
                            metadata=metadata,
                            source_lang=source_lang,
                            target_lang=target_lang
                        )
                    except Exception as e:
                        logger.warning(f"Failed to save chapter {chapter_num} to file: {e}")
                
                results[chapter_num] = {
                    "status": "completed",
                    "task_id": task.id,
                    "url": chapter_url
                }
                completed += 1
                
            except Exception as e:
                logger.error(f"Error processing chapter {chapter_num}: {e}")
                results[chapter_num] = {
                    "status": "failed",
                    "error": str(e),
                    "url": chapter_url
                }
                failed += 1
        
        return {
            "total_chapters": total_chapters,
            "completed": completed,
            "failed": failed,
            "results": results,
            "series_name": series_name
        }
        
    except Exception as e:
        logger.error(f"Error in batch translation: {e}")
        self.update_state(
            state='FAILED',
            meta={'error': str(e)}
        )
        raise

