"""
Application Enums
"""
from enum import IntEnum


class TranslateType(IntEnum):
    """Translation type enumeration"""
    AI = 1  # OpenAI GPT-4o-mini (paid, high quality)
    FREE = 2  # Free translation (Google Translate/DeepL free tier)


class TranslationMode(IntEnum):
    """Translation processing mode"""
    CLEAN = 1  # Clean mode: remove original text and replace
    OVERLAY = 2  # Overlay mode: add translation on top


class JobStatus(IntEnum):
    """Translation job status"""
    PENDING = 1
    PROCESSING = 2
    COMPLETED = 3
    FAILED = 4

