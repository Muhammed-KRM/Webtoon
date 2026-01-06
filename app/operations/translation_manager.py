"""
Translation Manager - Orchestrates the translation pipeline
"""
from celery import Celery
from celery.result import AsyncResult
import base64
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from app.core.config import settings
from app.services.scraper_service import ScraperService
from app.services.ocr_service import OCRService
from app.services.ai_translator import AITranslator
from app.services.free_translator import FreeTranslator
from app.services.ner_service import NERService
from app.services.advanced_ner_service import AdvancedNERService
from app.services.alternative_translator import AlternativeTranslator
from app.services.dictionary_service import DictionaryService
from app.core.enums import TranslateType, TranslationMode
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
    series_name: Optional[str] = None,
    translate_type: int = TranslateType.AI  # 1 = AI, 2 = Free
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
    start_time = time.time()
    try:
        # Initialize services
        cache_service = CacheService()
        scraper = ScraperService()
        ocr = OCRService()
        ai_translator = AITranslator() if translate_type == TranslateType.AI else None
        free_translator = FreeTranslator() if translate_type == TranslateType.FREE else None
        # Use advanced NER if available, fallback to basic NER
        try:
            ner_service = AdvancedNERService(language=source_lang) if translate_type == TranslateType.FREE else None
        except:
            ner_service = NERService() if translate_type == TranslateType.FREE else None
        processor = ImageProcessor()
        
        # Get database session for dictionary (for both AI and Free translation)
        db = None
        dictionary = None
        if series_name:
            try:
                from app.db.session import SessionLocal
                from app.models.dictionary import DictionaryEntry
                db = SessionLocal()
                series_id = DictionaryService.get_series_id_from_name(db, series_name)
                if series_id:
                    dictionary = DictionaryService.get_or_create_dictionary(
                        db, series_id, source_lang, target_lang
                    )
                    logger.info(f"Using dictionary for series {series_id} ({source_lang}->{target_lang})")
            except Exception as e:
                logger.warning(f"Failed to initialize dictionary: {e}")
        
        # Check cache first (include translate_type in cache key)
        cache_key_suffix = f"_{translate_type}"
        cached_result = cache_service.get_cached_result(
            chapter_url, target_lang, f"{mode}{cache_key_suffix}"
        )
        if cached_result:
            logger.info(f"Returning cached result for: {chapter_url}")
            # Release lock if we got cached result
            cache_service.release_translation_lock(chapter_url, target_lang, translate_type)
            if db:
                db.close()
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
        
        # Step 3: Translation (AI or Free)
        # Detect source language from URL if not provided
        from app.services.language_detector import LanguageDetector
        detected_lang = LanguageDetector.detect_from_url(chapter_url)
        if not source_lang:
            source_lang = detected_lang or "en"
        
        self.update_state(
            state='PROCESSING',
            meta={'progress': 50, 'message': f'Translating from {source_lang} to {target_lang}...'}
        )
        
        logger.info(f"Translating {len(flat_text_list)} texts from {source_lang} to {target_lang} (type: {translate_type})")
        
        # Get glossary dictionary for AI translation
        glossary_dict = None
        if translate_type == TranslateType.AI and dictionary:
            try:
                # Get all dictionary entries
                entries = db.query(DictionaryEntry).filter(
                    DictionaryEntry.dictionary_id == dictionary.id
                ).all()
                
                if entries:
                    # Convert to {original: translated} format
                    glossary_dict = {
                        entry.original_name: entry.translated_name
                        for entry in entries
                    }
                    logger.info(f"Using glossary with {len(glossary_dict)} entries for AI translation")
            except Exception as e:
                logger.warning(f"Failed to load glossary for AI translation: {e}")
        
        if translate_type == TranslateType.AI:
            # AI Translation (OpenAI GPT-4o-mini) with Glossary Support
            translated_flat = ai_translator.translate_batch_context_aware(
                all_texts=flat_text_list,
                source_lang=source_lang,
                target_lang=target_lang,
                use_cache=use_cache,
                glossary_dict=glossary_dict
            )
            
            # Update dictionary with detected proper nouns (for future use)
            if dictionary and db:
                try:
                    from app.models.dictionary import DictionaryEntry
                    # Use basic NER for AI translation too (lightweight)
                    try:
                        ner_service = NERService()
                        # Extract all proper nouns from original texts
                        all_proper_nouns = ner_service.extract_all_names(flat_text_list)
                        
                        # For each detected proper noun, check if it's in dictionary
                        for proper_noun in all_proper_nouns:
                            existing_entry = DictionaryService.lookup_name(db, dictionary.id, proper_noun)
                            if existing_entry:
                                # Update usage count
                                existing_entry.usage_count += 1
                                existing_entry.last_used_at = datetime.utcnow()
                                db.commit()
                            else:
                                # New proper noun - add to dictionary (AI will translate it consistently)
                                # We'll add the original as-is for now (AI handles translation)
                                occurrences = sum(1 for text in flat_text_list if proper_noun.lower() in text.lower())
                                if occurrences >= 2:  # Appears at least twice
                                    DictionaryService.add_or_update_entry(
                                        db, dictionary.id, proper_noun, proper_noun, "auto"
                                    )
                                    logger.info(f"Added new proper noun to dictionary: {proper_noun}")
                        
                        # Cleanup dictionary if needed
                        DictionaryService.cleanup_dictionary(db, dictionary.id)
                    except Exception as ner_error:
                        logger.warning(f"NER service failed for AI translation: {ner_error}")
                except Exception as e:
                    logger.warning(f"Dictionary update after AI translation failed: {e}")
        elif translate_type == TranslateType.FREE:
            # Free Translation with Dictionary Support
            # Step 3a: Apply dictionary (replace known names)
            texts_with_dict = flat_text_list
            if dictionary:
                try:
                    texts_with_dict, replacements = DictionaryService.apply_dictionary(
                        db, dictionary.id, flat_text_list
                    )
                    if replacements:
                        logger.info(f"Applied {len(replacements)} dictionary entries")
                except Exception as e:
                    logger.warning(f"Dictionary application failed: {e}")
                    texts_with_dict = flat_text_list
            
            # Step 3b: Free translation
            translated_flat = free_translator.translate_batch(
                texts=texts_with_dict,
                source_lang=source_lang,
                target_lang=target_lang
            )
            
            # Step 3c: Detect new proper nouns and add to dictionary
            if dictionary and ner_service:
                try:
                    # Extract all proper nouns from original texts
                    all_proper_nouns = ner_service.extract_all_names(flat_text_list)
                    
                    # For each detected proper noun, check if it's in dictionary
                    for proper_noun in all_proper_nouns:
                        # Skip if already in dictionary
                        existing_entry = DictionaryService.lookup_name(db, dictionary.id, proper_noun)
                        if existing_entry:
                            # Update usage count
                            existing_entry.usage_count += 1
                            existing_entry.last_used_at = datetime.utcnow()
                            db.commit()
                            continue
                        
                        # New proper noun - translate it and add to dictionary
                        try:
                            translated_name = free_translator.translate_single(
                                proper_noun, source_lang, target_lang
                            )
                            
                            # Add to dictionary
                            DictionaryService.add_or_update_entry(
                                db, dictionary.id, proper_noun, translated_name, "auto"
                            )
                            logger.info(f"Added new proper noun to dictionary: {proper_noun} -> {translated_name}")
                        except Exception as e:
                            logger.warning(f"Failed to add proper noun '{proper_noun}' to dictionary: {e}")
                    
                    # Cleanup dictionary if needed
                    DictionaryService.cleanup_dictionary(db, dictionary.id)
                except Exception as e:
                    logger.warning(f"Dictionary update failed: {e}")
        else:
            raise ValueError(f"Invalid translate_type: {translate_type}. Must be {TranslateType.AI} (AI) or {TranslateType.FREE} (Free)")
        
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
        cleaned_images_base64 = []  # Store cleaned images
        text_cursor = 0
        
        # We need to collect raw cleaned bytes to save them via FileManager later
        # (Though current flow returns result dict, the auto-publisher uses it)
        # We'll encode them to base64 for the result dict
        
        for page_idx, img_bytes in enumerate(images_bytes):
            logger.debug(f"Processing image {page_idx + 1}/{len(images_bytes)}")
            
            blocks = all_pages_blocks[page_idx]
            block_count = len(blocks)
            
            # Get translations for this page
            page_translations = translated_flat[text_cursor:text_cursor + block_count]
            text_cursor += block_count
            
            # 1. Clean image (always clean if mode is clean, or if we want to support editing)
            # We always generate cleaned image for "clean" mode to enable Editor support
            if mode == TranslationMode.CLEAN or mode == "clean":
                cleaned_bytes = processor.clean_image(img_bytes, blocks)
                # Store cleaned image
                cleaned_b64 = base64.b64encode(cleaned_bytes).decode('utf-8')
                cleaned_images_base64.append(cleaned_b64)
                
                if page_translations:
                    # Render text on cleaned image
                    final_img_bytes = processor.render_text(cleaned_bytes, blocks, page_translations)
                else:
                    final_img_bytes = cleaned_bytes
            else:
                # Overlay mode - no cleaning
                final_img_bytes = img_bytes
                cleaned_images_base64.append("")  # No cleaned image for overlay mode
            
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
            "cleaned_pages": cleaned_images_base64,  # New field
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
        
        # Release translation lock (task completed successfully)
        cache_service.release_translation_lock(chapter_url, target_lang, translate_type)
        
        # Auto-publish translation if series_name provided
        if series_name:
            try:
                from app.operations.translation_publisher import publish_translation_on_completion
                publish_translation_on_completion(
                    task_id=self.request.id,
                    result=result,
                    chapter_url=chapter_url,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    series_name=series_name,
                    series_description=f"Translated series: {series_name}",  # Default description
                    replace_existing_chapters=True  # Replace existing chapters/translations
                )
            except Exception as e:
                logger.error(f"Error auto-publishing translation: {e}", exc_info=True)
                # Don't fail the entire task if publishing fails
                # The translation files are already saved, can be published manually later
        
        return result
        
    except Exception as e:
        logger.error(f"Error in translation task: {e}", exc_info=True)
        metrics.increment_counter("translation.failed")
        self.update_state(
            state='FAILED',
            meta={'progress': 0, 'error': str(e)}
        )
        # Release lock on error
        try:
            cache_service.release_translation_lock(chapter_url, target_lang, translate_type)
        except:
            pass
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
        # Close database session if opened
        if 'db' in locals() and db:
            try:
                db.close()
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

