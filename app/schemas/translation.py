"""
Translation Schemas
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.core.enums import TranslateType, TranslationMode, Quality


class TranslationRequest(BaseModel):
    """Translation request"""
    chapter_url: str
    source_lang: str = "en"  # Source language code (ISO 639-1)
    target_lang: str = "tr"  # Target language code (ISO 639-1)
    mode: str = TranslationMode.CLEAN  # clean, overlay
    quality: str = Quality.HIGH  # high, fast
    series_name: Optional[str] = None  # Series name for file organization
    translate_type: int = TranslateType.AI  # 1 = AI (OpenAI GPT-4o-mini), 2 = Free (Google Translate/DeepL)


class JobStatusResponse(BaseModel):
    """Job status response"""
    task_id: str
    status: str  # PENDING, PROCESSING, COMPLETED, FAILED
    progress: int = 0  # 0-100
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ChapterPageResponse(BaseModel):
    """Chapter page response"""
    index: int
    processed_url: Optional[str] = None  # Base64 or URL
    original_text: List[str] = []
    translated_text: List[str] = []
    bubbles: List[Dict[str, int]] = []  # [{x, y, w, h}, ...]


class ChapterResponse(BaseModel):
    """Chapter response"""
    chapter_title: str
    pages: List[ChapterPageResponse]
    total_pages: int

