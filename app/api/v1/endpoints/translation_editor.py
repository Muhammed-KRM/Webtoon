"""
Translation Editor Endpoint - Human-in-the-Loop manual editing
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger

from app.core.database import get_db
from app.core.security import get_current_active_user, require_admin
from app.models.user import User
from app.models.job import TranslationJob
from app.schemas.base_response import BaseResponse
from app.services.cache_service import CacheService

router = APIRouter()


class TranslationEditRequest(BaseModel):
    """Request to edit a translation"""
    task_id: str
    page_index: int
    block_index: int
    original_text: str
    translated_text: str


class TranslationReviewRequest(BaseModel):
    """Request to review and approve/reject translation"""
    task_id: str
    page_index: int
    block_index: int
    action: str  # "approve", "reject", "edit"
    edited_text: Optional[str] = None


class TranslationReviewResponse(BaseModel):
    """Response for translation review"""
    task_id: str
    page_index: int
    block_index: int
    original_text: str
    translated_text: str
    status: str  # "pending", "approved", "rejected", "edited"


@router.get("/translation/{task_id}/review", response_model=BaseResponse[dict])
def get_translation_for_review(
    task_id: str,
    page_index: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get translation result for manual review/editing
    
    Returns original texts and AI translations side-by-side for review
    """
    try:
        # Get translation job
        job = db.query(TranslationJob).filter(
            TranslationJob.task_id == task_id,
            TranslationJob.user_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation job not found"
            )
        
        # Get cached result
        cache_service = CacheService()
        # Note: We need to store the result with original texts for review
        # This should be stored when translation completes
        
        # For now, return job status
        # In production, you'd fetch the actual translation data from cache/DB
        return BaseResponse.success_response(
            {
                "task_id": task_id,
                "status": job.status,
                "message": "Translation review data will be available when job completes"
            },
            "Translation review data retrieved"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting translation for review: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving translation: {str(e)}"
        )


@router.post("/translation/review", response_model=BaseResponse[dict])
def review_translation(
    request: TranslationReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Review and approve/reject/edit a translation
    
    Allows manual correction of AI translations before finalizing
    """
    try:
        # Get translation job
        job = db.query(TranslationJob).filter(
            TranslationJob.task_id == request.task_id,
            TranslationJob.user_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation job not found"
            )
        
        # Validate action
        if request.action not in ["approve", "reject", "edit"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action must be 'approve', 'reject', or 'edit'"
            )
        
        if request.action == "edit" and not request.edited_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="edited_text is required when action is 'edit'"
            )
        
        # In production, you would:
        # 1. Get the translation result from cache/DB
        # 2. Update the specific block's translation
        # 3. Re-process the image with the edited text
        # 4. Update the cache/DB with the corrected version
        
        logger.info(
            f"User {current_user.id} reviewed translation {request.task_id}: "
            f"page {request.page_index}, block {request.block_index}, action: {request.action}"
        )
        
        return BaseResponse.success_response(
            {
                "task_id": request.task_id,
                "page_index": request.page_index,
                "block_index": request.block_index,
                "action": request.action,
                "status": "reviewed"
            },
            f"Translation {request.action}ed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reviewing translation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reviewing translation: {str(e)}"
        )


@router.post("/translation/edit", response_model=BaseResponse[dict])
def edit_translation(
    request: TranslationEditRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Edit a specific translation block
    
    Allows manual correction of individual translation blocks
    """
    try:
        # Get translation job
        job = db.query(TranslationJob).filter(
            TranslationJob.task_id == request.task_id,
            TranslationJob.user_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation job not found"
            )
        
        # In production, you would:
        # 1. Get the translation result from cache/DB
        # 2. Update the specific block's translation
        # 3. Re-process the image with the edited text
        # 4. Update the cache/DB with the corrected version
        
        logger.info(
            f"User {current_user.id} edited translation {request.task_id}: "
            f"page {request.page_index}, block {request.block_index}"
        )
        
        return BaseResponse.success_response(
            {
                "task_id": request.task_id,
                "page_index": request.page_index,
                "block_index": request.block_index,
                "original_text": request.original_text,
                "translated_text": request.translated_text,
                "status": "edited"
            },
            "Translation edited successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing translation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error editing translation: {str(e)}"
        )

