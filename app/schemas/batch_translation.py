"""
Batch Translation Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from app.core.enums import TranslateType


class BatchTranslationRequest(BaseModel):
    """Batch translation request for multiple chapters"""
    base_url: str = Field(..., description="Base URL pattern (e.g., https://webtoons.com/en/series/episode-{}/viewer)")
    start_chapter: int = Field(..., ge=1, description="Starting chapter number")
    end_chapter: int = Field(..., ge=1, description="Ending chapter number")
    source_lang: str = Field(default="en", description="Source language code (ISO 639-1)")
    target_lang: str = Field(default="tr", description="Target language code (ISO 639-1)")
    mode: str = Field(default="clean", description="Processing mode: clean or overlay")
    series_name: Optional[str] = Field(None, description="Series name for folder organization")
    translate_type: int = Field(default=TranslateType.AI, description="1 = AI (OpenAI GPT-4o-mini), 2 = Free (Google Translate/DeepL)")


class BatchTranslationResponse(BaseModel):
    """Batch translation response"""
    task_id: str
    total_chapters: int
    chapters: List[Dict] = Field(default_factory=list, description="List of chapter task IDs")
    message: str


class ChapterRangeRequest(BaseModel):
    """Request for chapter range translation"""
    series_url: str = Field(..., description="Base series URL")
    chapter_range: str = Field(..., description="Chapter range (e.g., '1-10', '5,7,9', '1-5,10-15')")
    source_lang: str = Field(default="en", description="Source language code")
    target_lang: str = Field(default="tr", description="Target language code")
    mode: str = Field(default="clean", description="Processing mode")
    series_name: Optional[str] = None
    translate_type: int = Field(default=TranslateType.AI, description="1 = AI (OpenAI GPT-4o-mini), 2 = Free (Google Translate/DeepL)")

