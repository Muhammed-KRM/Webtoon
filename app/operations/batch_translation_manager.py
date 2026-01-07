"""
Batch Translation Manager - Handles multiple chapter translations
"""
from typing import List, Dict, Optional
import time
from loguru import logger
from app.core.celery_app import celery_app
from app.operations.translation_manager import process_chapter_task
from app.services.url_generator import URLGenerator
from app.services.language_detector import LanguageDetector
from app.services.file_manager import FileManager
from app.core.enums import TranslateType


@celery_app.task(bind=True, name="batch_translation_task")
def batch_translation_task(
    self,
    base_url: str,
    chapter_numbers: List[int],
    source_lang: str = "en",
    target_lang: str = "tr",
    mode: str = "clean",
    series_name: Optional[str] = None,
    translate_type: int = TranslateType.AI  # 1 = AI, 2 = Free
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
        logger.info(f"[DEBUG] Batch translation task started: base_url={base_url}, chapters={chapter_numbers}, series_name={series_name}")
        
        # Validate language pair
        is_valid, error_msg = LanguageDetector.validate_language_pair(source_lang, target_lang)
        if not is_valid:
            logger.error(f"[DEBUG] Language pair validation failed: {error_msg}")
            raise ValueError(error_msg)
        logger.info(f"[DEBUG] Language pair validated: {source_lang} -> {target_lang}")
        
        # Generate URLs for all chapters
        logger.info(f"[DEBUG] Generating URLs for {len(chapter_numbers)} chapters from base_url: {base_url}")
        chapter_urls = URLGenerator.generate_chapter_urls(base_url, chapter_numbers)
        logger.info(f"[DEBUG] Generated {len(chapter_urls)} URLs: {chapter_urls[:3]}..." if len(chapter_urls) > 3 else f"[DEBUG] Generated URLs: {chapter_urls}")
        
        total_chapters = len(chapter_urls)
        results = {}
        completed = 0
        failed = 0
        
        logger.info(f"[DEBUG] Starting batch translation: {total_chapters} chapters")
        
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
                
                logger.info(f"[DEBUG] Processing chapter {chapter_num}: {chapter_url}")
                
                # Start translation task for this chapter
                logger.info(f"[DEBUG] Starting process_chapter_task for chapter {chapter_num}")
                task = process_chapter_task.delay(
                    chapter_url=chapter_url,
                    target_lang=target_lang,
                    source_lang=source_lang,
                    mode=mode,
                    use_cache=(translate_type == TranslateType.AI),  # Use Cached Input only for AI
                    series_name=series_name,
                    translate_type=translate_type
                )
                logger.info(f"[DEBUG] Chapter {chapter_num} task started with task_id: {task.id}")
                
                # Wait for completion using AsyncResult (Celery best practice)
                # Cannot use .get() within a task - use AsyncResult polling instead
                logger.info(f"[DEBUG] Waiting for chapter {chapter_num} to complete (timeout: 600s)")
                try:
                    import time
                    from celery.result import AsyncResult
                    async_result = AsyncResult(task.id, app=celery_app)
                    
                    # Poll for result (don't use .get() directly in task)
                    # Increased timeout: 20 minutes per chapter (Cloudflare + translation can take time)
                    task_result = None
                    max_wait = 1200  # 20 minutes = 1200 seconds
                    for wait_count in range(max_wait):
                        if async_result.ready():
                            if async_result.successful():
                                task_result = async_result.result
                                break
                            else:
                                error_info = async_result.info
                                raise Exception(f"Task failed: {error_info}")
                        time.sleep(1)  # Wait 1 second between checks
                        
                        # Log progress every 60 seconds
                        if wait_count > 0 and wait_count % 60 == 0:
                            logger.info(f"[DEBUG] Chapter {chapter_num} still processing... ({wait_count}/{max_wait} seconds)")
                    
                    if task_result is None:
                        raise TimeoutError(f"Chapter {chapter_num} task timed out after {max_wait} seconds")
                    
                    logger.info(f"[DEBUG] Chapter {chapter_num} completed. Result type: {type(task_result)}, Keys: {list(task_result.keys()) if isinstance(task_result, dict) else 'Not a dict'}")
                except Exception as e:
                    logger.error(f"[DEBUG] Error getting task result for chapter {chapter_num}: {e}", exc_info=True)
                    raise
                
                # Save to file system if series_name provided
                if series_name and task_result and isinstance(task_result, dict):
                    try:
                        logger.info(f"[DEBUG] Saving chapter {chapter_num} to file system")
                        file_manager = FileManager()
                        pages_data = task_result.get("pages", [])
                        logger.info(f"[DEBUG] Chapter {chapter_num} has {len(pages_data)} pages")
                        
                        if not pages_data or len(pages_data) == 0:
                            logger.warning(f"[DEBUG] Chapter {chapter_num} has no pages data, skipping file save")
                            results[chapter_num] = {
                                "status": "completed",
                                "task_id": task.id,
                                "url": chapter_url,
                                "warning": "No pages data in result"
                            }
                            completed += 1
                            continue
                        
                        # Convert base64 to bytes
                        import base64
                        pages_bytes = []
                        for idx, page in enumerate(pages_data):
                            try:
                                if isinstance(page, str):
                                    pages_bytes.append(base64.b64decode(page))
                                elif isinstance(page, bytes):
                                    pages_bytes.append(page)
                                else:
                                    logger.warning(f"[DEBUG] Page {idx} of chapter {chapter_num} is not string or bytes, type: {type(page)}")
                                    continue
                            except Exception as e:
                                logger.error(f"[DEBUG] Error decoding page {idx} of chapter {chapter_num}: {e}")
                                raise
                        
                        if not pages_bytes:
                            logger.warning(f"[DEBUG] No valid pages bytes for chapter {chapter_num}, skipping file save")
                            results[chapter_num] = {
                                "status": "completed",
                                "task_id": task.id,
                                "url": chapter_url,
                                "warning": "No valid pages bytes"
                            }
                            completed += 1
                            continue
                        
                        metadata = {
                            "original_texts": task_result.get("original_texts", []),
                            "translated_texts": task_result.get("translated_texts", []),
                            "blocks": task_result.get("blocks", []),
                            "source_lang": source_lang,
                            "target_lang": target_lang
                        }
                        
                        logger.info(f"[DEBUG] Saving chapter {chapter_num} with metadata keys: {list(metadata.keys())}")
                        file_manager.save_chapter(
                            series_name=series_name,
                            chapter_number=chapter_num,
                            pages=pages_bytes,
                            metadata=metadata,
                            source_lang=source_lang,
                            target_lang=target_lang
                        )
                        logger.info(f"[DEBUG] Chapter {chapter_num} saved successfully to file system")
                    except Exception as e:
                        logger.error(f"[DEBUG] Failed to save chapter {chapter_num} to file: {e}", exc_info=True)
                
                results[chapter_num] = {
                    "status": "completed",
                    "task_id": task.id,
                    "url": chapter_url
                }
                completed += 1
                
            except Exception as e:
                logger.error(f"[DEBUG] Error processing chapter {chapter_num}: {e}", exc_info=True)
                error_msg = str(e)
                # Get more details if available
                if hasattr(e, '__cause__') and e.__cause__:
                    error_msg += f" (Cause: {str(e.__cause__)})"
                results[chapter_num] = {
                    "status": "failed",
                    "error": error_msg,
                    "url": chapter_url,
                    "error_type": type(e).__name__
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

