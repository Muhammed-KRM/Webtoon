"""
Language Detection Service
"""
from typing import Dict, Optional
import re
from loguru import logger


class LanguageDetector:
    """Service for detecting and validating language codes"""
    
    # ISO 639-1 language codes
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "tr": "Turkish",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese",
        "ar": "Arabic",
        "hi": "Hindi",
        "pl": "Polish",
        "nl": "Dutch",
        "sv": "Swedish",
        "no": "Norwegian",
        "da": "Danish",
        "fi": "Finnish",
        "cs": "Czech",
        "hu": "Hungarian",
        "ro": "Romanian",
        "bg": "Bulgarian",
        "el": "Greek",
        "he": "Hebrew",
        "th": "Thai",
        "vi": "Vietnamese",
        "id": "Indonesian",
        "ms": "Malay",
        "uk": "Ukrainian",
    }
    
    @classmethod
    def is_supported(cls, lang_code: str) -> bool:
        """Check if language code is supported"""
        return lang_code.lower() in cls.SUPPORTED_LANGUAGES
    
    @classmethod
    def get_language_name(cls, lang_code: str) -> Optional[str]:
        """Get language name from code"""
        return cls.SUPPORTED_LANGUAGES.get(lang_code.lower())
    
    @classmethod
    def validate_language_pair(cls, source_lang: str, target_lang: str) -> tuple[bool, Optional[str]]:
        """
        Validate language pair for translation
        
        Returns:
            (is_valid, error_message)
        """
        if not cls.is_supported(source_lang):
            return False, f"Unsupported source language: {source_lang}"
        
        if not cls.is_supported(target_lang):
            return False, f"Unsupported target language: {target_lang}"
        
        if source_lang == target_lang:
            return False, "Source and target languages cannot be the same"
        
        return True, None
    
    @classmethod
    def detect_from_url(cls, url: str) -> Optional[str]:
        """
        Try to detect language from URL
        
        Examples:
        - https://www.webtoons.com/en/... -> "en"
        - https://www.webtoons.com/tr/... -> "tr"
        - https://asurascans.com.tr/... -> "tr"
        """
        url_lower = url.lower()
        
        # Check for language code in path
        lang_patterns = {
            '/en/': 'en',
            '/tr/': 'tr',
            '/es/': 'es',
            '/fr/': 'fr',
            '/de/': 'de',
            '/it/': 'it',
            '/pt/': 'pt',
            '/ru/': 'ru',
            '/ja/': 'ja',
            '/ko/': 'ko',
            '/zh/': 'zh',
        }
        
        for pattern, lang_code in lang_patterns.items():
            if pattern in url_lower:
                return lang_code
        
        # Check domain
        if '.com.tr' in url_lower or 'turkish' in url_lower:
            return 'tr'
        elif '.com' in url_lower and 'webtoons' in url_lower:
            # Default webtoons.com to English if no language specified
            return 'en'
        
        return None
    
    @classmethod
    def normalize_language_code(cls, lang_code: str) -> str:
        """
        Normalize language code to ISO 639-1 format
        
        Args:
            lang_code: Language code (may be in various formats)
            
        Returns:
            Normalized language code (lowercase, 2-letter)
        """
        if not lang_code:
            return "en"
        
        lang_code = lang_code.lower().strip()
        
        # If already in SUPPORTED_LANGUAGES, return as is
        if lang_code in cls.SUPPORTED_LANGUAGES:
            return lang_code
        
        # Try to map common variations
        lang_map = {
            "english": "en",
            "turkish": "tr",
            "spanish": "es",
            "french": "fr",
            "german": "de",
            "italian": "it",
            "portuguese": "pt",
            "russian": "ru",
            "japanese": "ja",
            "korean": "ko",
            "chinese": "zh",
        }
        
        if lang_code in lang_map:
            return lang_map[lang_code]
        
        # If 3-letter code, try to convert (simplified)
        if len(lang_code) == 3:
            # Common 3-letter to 2-letter mappings
            iso3_to_2 = {
                "eng": "en",
                "tur": "tr",
                "spa": "es",
                "fra": "fr",
                "deu": "de",
                "ita": "it",
                "por": "pt",
                "rus": "ru",
                "jpn": "ja",
                "kor": "ko",
                "zho": "zh",
            }
            if lang_code in iso3_to_2:
                return iso3_to_2[lang_code]
        
        # Default to English if unknown
        return "en"

