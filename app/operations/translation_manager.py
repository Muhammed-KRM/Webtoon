"""
Translation Manager - Orchestrates the translation pipeline
"""
from celery import Celery
from celery.result import AsyncResult
import base64
import asyncio
from typing import Dict, Any
from loguru import logger
from app.core.config import settings
from app.services.scraper_service import ScraperService
from app.services.ocr_service import OCRService
from app.services.ai_translator import AITranslator
from app.services.image_processor import ImageProcessor
from app.services.cache_service import CacheService
from app.core.metrics import metrics
import time

# Initialize Celery
celery_app = Celery(
    "webtoon_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery_app.task(bind=True, name="process_chapter_task")
def process_chapter_task(
    self,
    chapter_url: str,
    target_lang: str = "tr",
    source_lang: str = "en",
    mode: str = "clean",
    use_cache: bool = True,
    series_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main translation pipeline task
    
    This task orchestrates the entire translation process:
    1. Fetch images from URL
    2. OCR to extract text
    3. AI translation (context-aware)
    4. Image processing (in-painting + text rendering)
    
    Args:
        chapter_url: URL of the webtoon chapter
        target_lang: Target language (default: "tr")
        mode: Processing mode ("clean" or "overlay")
        use_cache: Whether to use Cached Input
        
    Returns:
        Dictionary with processed pages (base64 encoded)
    """
    scraper = None
    try:
        # Initialize services
        cache_service = CacheService()
        scraper = ScraperService()
        ocr = OCRService()
        translator = AITranslator()
        processor = ImageProcessor()
        
        # Check cache first
        cached_result = cache_service.get_cached_result(chapter_url, target_lang, mode)
        if cached_result:
            logger.info(f"Returning cached result for: {chapter_url}")
            return cached_result
        
        # Step 1: Fetch images
        self.update_state(
            state='PROCESSING',
            meta={'progress': 10, 'message': 'Resimler indiriliyor...'}
        )
        logger.info(f"Fetching images from: {chapter_url}")
        
        # Run async scraper in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            images_bytes = loop.run_until_complete(scraper.fetch_chapter_images(chapter_url))
        finally:
            loop.close()
        
        if not images_bytes:
            raise ValueError("No images found")
        
        logger.info(f"Fetched {len(images_bytes)} images")
        
        # Step 2: OCR - Extract text from all pages
        self.update_state(
            state='PROCESSING',
            meta={'progress': 30, 'message': 'OCR yapılıyor...'}
        )
        
        all_pages_blocks = []
        flat_text_list = []
        
        for idx, img_bytes in enumerate(images_bytes):
            logger.debug(f"Processing OCR for page {idx + 1}/{len(images_bytes)}")
            blocks = ocr.detect_text(img_bytes)
            all_pages_blocks.append(blocks)
            
            for block in blocks:
                flat_text_list.append(block['text'])
        
        logger.info(f"Extracted {len(flat_text_list)} text blocks from {len(images_bytes)} pages")
        
        if not flat_text_list:
            logger.warning("No text found in images")
            # Return original images if no text found
            processed_images_base64 = [
                base64.b64encode(img).decode('utf-8')
                for img in images_bytes
            ]
            return {
                "pages": processed_images_base64,
                "total": len(processed_images_base64),
                "message": "No text found in images"
            }
        
        # Step 3: AI Translation (Context-aware)
        # Detect source language from URL if not provided
        if 'source_lang' not in locals():
            from app.services.language_detector import LanguageDetector
            detected_lang = LanguageDetector.detect_from_url(chapter_url)
            source_lang = detected_lang or "en"
        
        self.update_state(
            state='PROCESSING',
            meta={'progress': 50, 'message': f'Translating from {source_lang} to {target_lang}...'}
        )
        
        logger.info(f"Translating {len(flat_text_list)} texts from {source_lang} to {target_lang}")
        translated_flat = translator.translate_batch_context_aware(
            all_texts=flat_text_list,
            source_lang=source_lang,
            target_lang=target_lang,
            use_cache=use_cache
        )
        
        if len(translated_flat) != len(flat_text_list):
            logger.warning(
                f"Translation count mismatch: {len(flat_text_list)} -> {len(translated_flat)}"
            )
        
        # Step 4: Image Processing
        self.update_state(
            state='PROCESSING',
            meta={'progress': 70, 'message': 'Görüntüler işleniyor...'}
        )
        
        processed_images_base64 = []
        text_cursor = 0
        
        for page_idx, img_bytes in enumerate(images_bytes):
            logger.debug(f"Processing image {page_idx + 1}/{len(images_bytes)}")
            
            blocks = all_pages_blocks[page_idx]
            block_count = len(blocks)
            
            # Get translations for this page
            page_translations = translated_flat[text_cursor:text_cursor + block_count]
            text_cursor += block_count
            
            # Process image (in-paint + render text)
            if mode == "clean" and page_translations:
                final_img_bytes = processor.process_image(
                    img_bytes,
                    blocks,
                    page_translations
                )
            else:
                # Overlay mode or no translations - return original
                final_img_bytes = img_bytes
            
            # Encode to base64
            b64_str = base64.b64encode(final_img_bytes).decode('utf-8')
            processed_images_base64.append(b64_str)
            
            # Update progress
            progress = 70 + int((page_idx + 1) / len(images_bytes) * 20)
            self.update_state(
                state='PROCESSING',
                meta={'progress': progress, 'message': f'Sayfa {page_idx + 1}/{len(images_bytes)} işlendi...'}
            )
        
        logger.info(f"Successfully processed {len(processed_images_base64)} pages")
        
        # Metrics
        duration = time.time() - start_time
        metrics.increment_counter("translation.completed")
        metrics.record_timing("translation.duration", duration)
        
        # Final result
        result = {
            "pages": processed_images_base64,
            "total": len(processed_images_base64),
            "original_texts": flat_text_list,
            "translated_texts": translated_flat,
            "blocks": [
                {
                    "page": idx,
                    "blocks": [
                        {
                            "text": b['text'],
                            "coords": b['coords'],
                            "confidence": b['confidence']
                        }
                        for b in blocks
                    ]
                }
                for idx, blocks in enumerate(all_pages_blocks)
            ]
        }
        
        # Cache the result
        cache_service.set_cached_result(chapter_url, result, target_lang, mode)
        
        # Auto-publish translation if series_name provided
        if 'series_name' in locals() and series_name:
            try:
                from app.operations.translation_publisher import publish_translation_on_completion
                publish_translation_on_completion(
                    task_id=self.request.id,
                    result=result,
                    chapter_url=chapter_url,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    series_name=series_name
                )
            except Exception as e:
                logger.warning(f"Error auto-publishing translation: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in translation task: {e}", exc_info=True)
        metrics.increment_counter("translation.failed")
        self.update_state(
            state='FAILED',
            meta={'progress': 0, 'error': str(e)}
        )
        raise
    finally:
        if scraper:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(scraper.close())
                loop.close()
            except:
                pass


def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get status of a Celery task"""
    task_result = AsyncResult(task_id, app=celery_app)
    
    response_data = {
        "task_id": task_id,
        "status": task_result.state,
        "progress": 0,
        "message": None,
        "result": None,
        "error": None
    }
    
    if task_result.state == 'PROCESSING':
        info = task_result.info or {}
        response_data["progress"] = info.get('progress', 0)
        response_data["message"] = info.get('message', 'Processing...')
    elif task_result.state == 'SUCCESS':
        response_data["progress"] = 100
        response_data["result"] = task_result.result
        response_data["message"] = "Completed"
    elif task_result.state == 'FAILURE':
        response_data["error"] = str(task_result.info)
        response_data["message"] = "Failed"
    elif task_result.state == 'PENDING':
        response_data["message"] = "Pending"
    
    return response_data

