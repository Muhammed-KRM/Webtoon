"""
Admin Content Management Endpoints
- Manual chapter upload (without translation)
- Chapter/Page editing
- Content management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List
from pathlib import Path
import shutil
import json
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.models.series import Series, Chapter, ChapterTranslation
from app.services.file_manager import FileManager
from app.core.cache_invalidation import CacheInvalidation
from app.core.enums import TranslationStatus
from loguru import logger
from sqlalchemy import and_

router = APIRouter()
file_manager = FileManager()


class BulkPublishRequest(BaseModel):
    chapter_ids: List[int]
    publish: bool = True


@router.post("/admin/chapters/upload", response_model=BaseResponse[dict])
async def upload_chapter_manually(
    series_id: int = Form(...),
    chapter_number: int = Form(...),
    source_lang: str = Form("en"),
    target_lang: str = Form("tr"),
    title: Optional[str] = Form(None),
    pages: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Admin manuel bölüm yükleme (çeviri yaptırmadan direkt dosya yükleme)
    
    Admin kendi çevirdiği veya başka yerden bulduğu bölümleri direkt yükleyebilir.
    """
    try:
        # Get series
        series = db.query(Series).filter(Series.id == series_id).first()
        if not series:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Series not found"
            )
        
        # Check if chapter exists
        existing_chapter = db.query(Chapter).filter(
            Chapter.series_id == series_id,
            Chapter.chapter_number == chapter_number
        ).first()
        
        if not existing_chapter:
            # Create new chapter
            chapter = Chapter(
                series_id=series_id,
                chapter_number=chapter_number,
                title=title or f"Chapter {chapter_number}",
                page_count=len(pages),
                is_published=True,
                published_at=datetime.utcnow()
            )
            db.add(chapter)
            db.commit()
            db.refresh(chapter)
        else:
            chapter = existing_chapter
            chapter.page_count = len(pages)
            chapter.title = title or chapter.title
            db.commit()
            db.refresh(chapter)
        
        # Save pages to disk
        pages_bytes = []
        for page_file in pages:
            content = await page_file.read()
            pages_bytes.append(content)
        
        # Save using FileManager
        metadata = {
            "uploaded_by": current_user.id,
            "uploaded_at": datetime.utcnow().isoformat(),
            "upload_type": "manual",
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        
        storage_path = file_manager.save_chapter(
            series_name=series.title,
            chapter_number=chapter_number,
            pages=pages_bytes,
            metadata=metadata,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        # Create or update ChapterTranslation
        translation = db.query(ChapterTranslation).filter(
            ChapterTranslation.chapter_id == chapter.id,
            ChapterTranslation.source_lang == source_lang,
            ChapterTranslation.target_lang == target_lang
        ).first()
        
        if not translation:
            translation = ChapterTranslation(
                chapter_id=chapter.id,
                source_lang=source_lang,
                target_lang=target_lang,
                storage_path=storage_path,
                page_count=len(pages),
                status=TranslationStatus.COMPLETED,
                is_published=True
            )
            db.add(translation)
        else:
            translation.storage_path = storage_path
            translation.page_count = len(pages)
            translation.status = TranslationStatus.COMPLETED
            translation.is_published = True
        
        db.commit()
        db.refresh(translation)
        
        # Invalidate cache
        CacheInvalidation.invalidate_chapter_cache(chapter.id)
        CacheInvalidation.invalidate_series_cache(series.id)
        
        return BaseResponse.success_response(
            {
                "chapter_id": chapter.id,
                "translation_id": translation.id,
                "chapter_number": chapter_number,
                "page_count": len(pages),
                "storage_path": storage_path
            },
            "Chapter uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading chapter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading chapter: {str(e)}"
        )


@router.put("/admin/chapters/{chapter_id}/pages/{page_number}", response_model=BaseResponse[dict])
async def update_page(
    chapter_id: int,
    page_number: int,
    page_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Spesifik bir sayfayı düzenleme/yeniden yükleme
    """
    try:
        # Get chapter
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        # Get translation (use first available or create)
        translation = db.query(ChapterTranslation).filter(
            ChapterTranslation.chapter_id == chapter_id
        ).first()
        
        if not translation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation not found. Upload chapter first."
            )
        
        # Get storage path
        storage_path = Path(translation.storage_path)
        if not storage_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Storage path not found"
            )
        
        # Update page
        page_path = storage_path / f"page_{page_number:03d}.jpg"
        content = await page_file.read()
        
        with open(page_path, 'wb') as f:
            f.write(content)
        
        # Update metadata
        metadata_path = storage_path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        if "page_updates" not in metadata:
            metadata["page_updates"] = []
        
        metadata["page_updates"].append({
            "page_number": page_number,
            "updated_by": current_user.id,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # Invalidate cache
        CacheInvalidation.invalidate_chapter_cache(chapter_id)
        CacheInvalidation.invalidate_series_cache(chapter.series_id)
        
        return BaseResponse.success_response(
            {
                "chapter_id": chapter_id,
                "page_number": page_number,
                "updated": True
            },
            "Page updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating page: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating page: {str(e)}"
        )


@router.delete("/admin/chapters/{chapter_id}/pages/{page_number}", response_model=BaseResponse[dict])
async def delete_page(
    chapter_id: int,
    page_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Spesifik bir sayfayı silme
    """
    try:
        # Get chapter
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        # Get translation
        translation = db.query(ChapterTranslation).filter(
            ChapterTranslation.chapter_id == chapter_id
        ).first()
        
        if not translation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation not found"
            )
        
        # Delete page file
        storage_path = Path(translation.storage_path)
        page_path = storage_path / f"page_{page_number:03d}.jpg"
        
        if page_path.exists():
            page_path.unlink()
        
        # Update page count
        remaining_pages = len(list(storage_path.glob("page_*.jpg")))
        translation.page_count = remaining_pages
        chapter.page_count = remaining_pages
        db.commit()
        
        # Invalidate cache
        CacheInvalidation.invalidate_chapter_cache(chapter_id)
        CacheInvalidation.invalidate_series_cache(chapter.series_id)
        
        return BaseResponse.success_response(
            {
                "chapter_id": chapter_id,
                "page_number": page_number,
                "deleted": True,
                "remaining_pages": remaining_pages
            },
            "Page deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting page: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting page: {str(e)}"
        )


@router.post("/admin/chapters/{chapter_id}/pages/reorder", response_model=BaseResponse[dict])
async def reorder_pages(
    chapter_id: int,
    page_order: List[int] = Body(..., description="New page order (list of page numbers)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Sayfa sıralamasını yeniden düzenleme
    """
    try:
        # Get chapter
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        # Get translation
        translation = db.query(ChapterTranslation).filter(
            ChapterTranslation.chapter_id == chapter_id
        ).first()
        
        if not translation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation not found"
            )
        
        storage_path = Path(translation.storage_path)
        if not storage_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Storage path not found"
            )
        
        # Get all pages
        all_pages = sorted([int(p.stem.split('_')[1]) for p in storage_path.glob("page_*.jpg")])
        
        if len(page_order) != len(all_pages):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Page order must contain {len(all_pages)} pages"
            )
        
        # Create temp directory
        temp_dir = storage_path / "temp_reorder"
        temp_dir.mkdir(exist_ok=True)
        
        # Move pages to temp with new names
        for new_index, old_page_num in enumerate(page_order, start=1):
            old_path = storage_path / f"page_{old_page_num:03d}.jpg"
            if old_path.exists():
                temp_path = temp_dir / f"page_{new_index:03d}.jpg"
                shutil.copy2(old_path, temp_path)
        
        # Remove old pages
        for page_num in all_pages:
            old_path = storage_path / f"page_{page_num:03d}.jpg"
            if old_path.exists():
                old_path.unlink()
        
        # Move from temp to final
        for temp_file in sorted(temp_dir.glob("page_*.jpg")):
            final_path = storage_path / temp_file.name
            shutil.move(str(temp_file), str(final_path))
        
        # Remove temp directory
        temp_dir.rmdir()
        
        # Update metadata
        metadata_path = storage_path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        metadata["reordered"] = {
            "new_order": page_order,
            "reordered_by": current_user.id,
            "reordered_at": datetime.utcnow().isoformat()
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # Invalidate cache
        CacheInvalidation.invalidate_chapter_cache(chapter_id)
        CacheInvalidation.invalidate_series_cache(chapter.series_id)
        
        return BaseResponse.success_response(
            {
                "chapter_id": chapter_id,
                "new_order": page_order,
                "reordered": True
            },
            "Pages reordered successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering pages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reordering pages: {str(e)}"
        )


@router.post("/admin/series/{series_id}/chapters/bulk-publish", response_model=BaseResponse[dict])
def bulk_publish_chapters(
    series_id: int,
    request: BulkPublishRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Toplu bölüm yayınlama/yayından kaldırma
    """
    try:
        # Get series
        series = db.query(Series).filter(Series.id == series_id).first()
        if not series:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Series not found"
            )
        
        # Update chapters
        chapters = db.query(Chapter).filter(
            Chapter.id.in_(request.chapter_ids),
            Chapter.series_id == series_id
        ).all()
        
        updated_count = 0
        for chapter in chapters:
            chapter.is_published = request.publish
            if request.publish:
                chapter.published_at = datetime.utcnow()
            updated_count += 1
        
        db.commit()
        
        # Invalidate cache
        CacheInvalidation.invalidate_series_cache(series_id)
        for chapter in chapters:
            CacheInvalidation.invalidate_chapter_cache(chapter.id)
        
        return BaseResponse.success_response(
            {
                "series_id": series_id,
                "updated_count": updated_count,
                "publish": request.publish
            },
            f"{updated_count} chapters {'published' if request.publish else 'unpublished'} successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error bulk publishing chapters: {str(e)}"
        )
