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
        
        # 1. Load metadata to get file paths
        from app.models.series import Chapter, ChapterTranslation
        from app.services.file_manager import FileManager
        from app.services.image_processor import ImageProcessor
        import json
        from pathlib import Path
        import base64
        
        # We need to find where the files are stored via the chapter relation
        # or assuming we can find it via job result if available, 
        # but for safety let's assume we can reconstruct path or find the translation entry
        
        translation = db.query(ChapterTranslation).filter(
            ChapterTranslation.translation_job_id == request.task_id
        ).first()
        
        if not translation or not translation.storage_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation files not found"
            )
        
        storage_path = Path(translation.storage_path)
        metadata_path = storage_path / "metadata.json"
        
        if not metadata_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Metadata file not found"
            )
            
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        # 2. Update the specific text
        # metadata structure: 
        # "translated_texts": [...],
        # "blocks": [{"page": 0, "blocks": [...]}, ...]
        
        # Calculate global text index
        # We need to find which "translated_texts" index corresponds to page_index + block_index
        # This depends on how many blocks were in previous pages
        
        global_index = 0
        found = False
        
        blocks_structure = metadata.get("blocks", [])
        
        for p_idx, page_data in enumerate(blocks_structure):
            if p_idx == request.page_index:
                # We are in the correct page
                if request.block_index < len(page_data["blocks"]):
                    global_index += request.block_index
                    found = True
                    break
                else:
                     raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Block index {request.block_index} out of range for page {request.page_index}"
                    )
            else:
                # Add all blocks from this page
                global_index += len(page_data["blocks"])
        
        if not found:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page {request.page_index} not found in metadata"
            )
            
        # Validate global index
        translated_texts = metadata.get("translated_texts", [])
        if global_index >= len(translated_texts):
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Global index {global_index} out of range (total {len(translated_texts)})"
            )
            
        # Update text
        old_text = translated_texts[global_index]
        translated_texts[global_index] = request.translated_text
        metadata["translated_texts"] = translated_texts
        
        # 3. Re-process the image
        # Load cleaned image
        # Assuming format: page_001.jpg/webp
        # We need to detect extension. Let's look at the existing files in cleaning folder
        cleaned_folder = storage_path / "cleaned"
        if not cleaned_folder.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cleaned images not found. Cannot edit translation."
            )
            
        # Find the file for this page (page index is 0-based, files are 1-based)
        page_num = request.page_index + 1
        page_files = list(cleaned_folder.glob(f"page_{page_num:03d}.*"))
        
        if not page_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cleaned image for page {page_num} not found"
            )
            
        cleaned_image_path = page_files[0]
        with open(cleaned_image_path, 'rb') as f:
            cleaned_bytes = f.read()
            
        # Prepare data for rendering
        # Get blocks for this page
        page_blocks_data = blocks_structure[request.page_index]["blocks"]
        
        # Get translations for this page
        # Start index for this page in global list
        start_idx = global_index - request.block_index
        end_idx = start_idx + len(page_blocks_data)
        page_translations = translated_texts[start_idx:end_idx]
        
        # Render
        processor = ImageProcessor()
        final_bytes = processor.render_text(
            cleaned_bytes,
            page_blocks_data, # Pass dict directly, render_text expects list of dicts
            page_translations
        )
        
        # 4. Save new image
        # Overwrite the existing final image
        # We need to match the extension of the final image in parent folder
        # or just use the extension we generated
        final_image_path = storage_path / cleaned_image_path.name # Use same name/ext as cleaned for simplicity? 
        # Wait, if we use WebP we might change ext. 
        # Let's check what's in the main folder
        main_page_files = list(storage_path.glob(f"page_{page_num:03d}.*"))
        target_path = main_page_files[0] if main_page_files else final_image_path
        
        with open(target_path, 'wb') as f:
            f.write(final_bytes)
            
        # Update metadata file
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
        # 5. Update Cache/CDN if enabled (Logic omitted for brevity, but should invalidate cache)
        if metadata.get("cdn_enabled"):
             # In a real scenario, we would re-upload to CDN here
             pass
             
        logger.info(
            f"User {current_user.id} edited translation {request.task_id}: "
            f"page {request.page_index}, block {request.block_index}, "
            f"text: '{old_text}' -> '{request.translated_text}'"
        )
        
        return BaseResponse.success_response(
            {
                "task_id": request.task_id,
                "page_index": request.page_index,
                "block_index": request.block_index,
                "original_text": request.original_text,
                "translated_text": request.translated_text,
                "status": "edited",
                "updated_image_url": f"/files/{translation.storage_path}/{target_path.name}?t={int(import_time.time())}" if 'import_time' in locals() else ""
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

