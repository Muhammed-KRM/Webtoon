"""
Translation Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.translation import (
    TranslationRequest,
    JobStatusResponse,
    ChapterResponse
)
from app.schemas.batch_translation import (
    BatchTranslationRequest,
    BatchTranslationResponse,
    ChapterRangeRequest
)
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.models.job import TranslationJob
from app.operations.translation_manager import (
    process_chapter_task,
    get_task_status
)
from app.operations.batch_translation_manager import batch_translation_task
from app.services.url_generator import URLGenerator
from app.services.language_detector import LanguageDetector
from app.core.rate_limit import rate_limit
from app.core.metrics import metrics
from app.core.enums import TranslateType
from datetime import datetime
import uuid
import time

router = APIRouter()


@router.post("/start", response_model=BaseResponse[dict])
@rate_limit(max_requests=10, window_seconds=60, key_prefix="translation.start")
def start_translation(
    request: TranslationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start a translation job"""
    start_time = time.time()
    try:
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Detect source language
        from app.services.language_detector import LanguageDetector
        source_lang = LanguageDetector.detect_from_url(request.chapter_url) or "en"
        
        # Validate translate_type
        if request.translate_type not in [TranslateType.AI, TranslateType.FREE]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"translate_type must be {TranslateType.AI} (AI) or {TranslateType.FREE} (Free)"
            )
        
        # Start Celery task
        task = process_chapter_task.delay(
            chapter_url=request.chapter_url,
            target_lang=request.target_lang,
            source_lang=source_lang,
            mode=request.mode,
            use_cache=(request.translate_type == TranslateType.AI),  # Use Cached Input only for AI
            series_name=request.series_name,
            translate_type=request.translate_type
        )
        
        # Update task_id with Celery's task ID
        task_id = task.id
        
        # Save job to database
        job = TranslationJob(
            task_id=task_id,
            user_id=current_user.id,
            chapter_url=request.chapter_url,
            target_lang=request.target_lang,
            mode=request.mode,
            status="PENDING"
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Metrics
        metrics.increment_counter("translation.started")
        duration = time.time() - start_time
        metrics.record_timing("translation.start.duration", duration)
        
        return BaseResponse.success_response(
            {"task_id": task_id},
            "Translation started. You can track it using the task ID."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting translation: {str(e)}"
        )


@router.get("/status/{task_id}", response_model=BaseResponse[JobStatusResponse])
def get_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get translation job status"""
    # Check if job belongs to user
    job = db.query(TranslationJob).filter(
        TranslationJob.task_id == task_id,
        TranslationJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get task status from Celery
    task_status = get_task_status(task_id)
    
    # Update job in database
    job.status = task_status["status"]
    job.progress = task_status["progress"]
    
    if task_status["status"] == "SUCCESS":
        job.status = "COMPLETED"
        job.result_data = task_status["result"]
        job.completed_at = datetime.utcnow()
    elif task_status["status"] == "FAILURE":
        job.status = "FAILED"
        job.error_message = task_status.get("error", "Unknown error")
    
    db.commit()
    
    return BaseResponse.success_response(
        JobStatusResponse(
            task_id=task_id,
            status=task_status["status"],
            progress=task_status["progress"],
            message=task_status.get("message"),
            result=task_status.get("result"),
            error=task_status.get("error")
        ),
        "Status retrieved"
    )


@router.get("/result/{task_id}", response_model=BaseResponse[ChapterResponse])
def get_result(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get translation result"""
    # Check if job belongs to user and is completed
    job = db.query(TranslationJob).filter(
        TranslationJob.task_id == task_id,
        TranslationJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not completed. Status: {job.status}"
        )
    
    if not job.result_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result data not found"
        )
    
    # Build response
    result = job.result_data
    pages_data = result.get("pages", [])
    blocks_data = result.get("blocks", [])
    original_texts = result.get("original_texts", [])
    translated_texts = result.get("translated_texts", [])
    
    # Build pages
    pages = []
    text_index = 0
    
    for page_idx, page_data in enumerate(pages_data):
        page_blocks = blocks_data[page_idx]["blocks"] if page_idx < len(blocks_data) else []
        
        # Get texts for this page
        page_original = []
        page_translated = []
        
        for block in page_blocks:
            if text_index < len(original_texts):
                page_original.append(original_texts[text_index])
            if text_index < len(translated_texts):
                page_translated.append(translated_texts[text_index])
            text_index += 1
        
        pages.append({
            "index": page_idx,
            "processed_url": f"data:image/jpeg;base64,{page_data}",
            "original_text": page_original,
            "translated_text": page_translated,
            "bubbles": [{"x": b["coords"][0], "y": b["coords"][1], 
                        "w": b["coords"][2], "h": b["coords"][3]} 
                       for b in page_blocks]
        })
    
        return BaseResponse.success_response(
        ChapterResponse(
            chapter_title=f"Chapter {task_id[:8]}",
            pages=pages,
            total_pages=len(pages)
        ),
        "Result retrieved"
    )


@router.post("/batch/start", response_model=BaseResponse[BatchTranslationResponse])
def start_batch_translation(
    request: BatchTranslationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start batch translation for multiple chapters"""
    try:
        # Validate language pair
        is_valid, error_msg = LanguageDetector.validate_language_pair(
            request.source_lang, 
            request.target_lang
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Generate chapter numbers
        chapter_numbers = list(range(request.start_chapter, request.end_chapter + 1))
        
        # Validate translate_type
        if request.translate_type not in [TranslateType.AI, TranslateType.FREE]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"translate_type must be {TranslateType.AI} (AI) or {TranslateType.FREE} (Free)"
            )
        
        # Start batch task
        task = batch_translation_task.delay(
            base_url=request.base_url,
            chapter_numbers=chapter_numbers,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            mode=request.mode,
            series_name=request.series_name,
            translate_type=request.translate_type
        )
        
        # Save to database
        job = TranslationJob(
            task_id=task.id,
            user_id=current_user.id,
            chapter_url=request.base_url,
            target_lang=request.target_lang,
            mode=request.mode,
            status="PENDING"
        )
        db.add(job)
        db.commit()
        
        return BaseResponse.success_response(
            BatchTranslationResponse(
                task_id=task.id,
                total_chapters=len(chapter_numbers),
                chapters=[{"chapter": num, "status": "pending"} for num in chapter_numbers],
                message=f"Batch translation started for {len(chapter_numbers)} chapters"
            ),
            "Batch translation started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting batch translation: {str(e)}"
        )


@router.post("/batch/range", response_model=BaseResponse[BatchTranslationResponse])
def start_range_translation(
    request: ChapterRangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start translation for a chapter range (e.g., '1-10', '5,7,9', '1-5,10-15')"""
    try:
        # Validate language pair
        is_valid, error_msg = LanguageDetector.validate_language_pair(
            request.source_lang,
            request.target_lang
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Parse chapter range
        chapter_numbers = URLGenerator.parse_chapter_range(request.chapter_range)
        
        if not chapter_numbers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid chapter range format"
            )
        
        # Validate translate_type
        if request.translate_type not in [TranslateType.AI, TranslateType.FREE]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"translate_type must be {TranslateType.AI} (AI) or {TranslateType.FREE} (Free)"
            )
        
        # Start batch task
        task = batch_translation_task.delay(
            base_url=request.series_url,
            chapter_numbers=chapter_numbers,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            mode=request.mode,
            series_name=request.series_name,
            translate_type=request.translate_type
        )
        
        # Save to database
        job = TranslationJob(
            task_id=task.id,
            user_id=current_user.id,
            chapter_url=request.series_url,
            target_lang=request.target_lang,
            mode=request.mode,
            status="PENDING"
        )
        db.add(job)
        db.commit()
        
        return BaseResponse.success_response(
            BatchTranslationResponse(
                task_id=task.id,
                total_chapters=len(chapter_numbers),
                chapters=[{"chapter": num, "status": "pending"} for num in chapter_numbers],
                message=f"Range translation started for chapters: {request.chapter_range}"
            ),
            "Range translation started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting range translation: {str(e)}"
        )

