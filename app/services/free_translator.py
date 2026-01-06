"""
Free Translation Service - Uses free translation APIs (Google Translate, DeepL free tier)
"""
from typing import List, Optional
from loguru import logger
from deep_translator import GoogleTranslator, DeepL
from app.services.language_detector import LanguageDetector


class FreeTranslator:
    """Service for free translation using Google Translate or DeepL free tier"""
    
    def __init__(self, provider: str = "google"):
        """
        Initialize free translator
        
        Args:
            provider: "google" or "deepl" (default: "google")
        """
        self.provider = provider
        self._google_translator = None
        self._deepl_translator = None
    
    def _get_google_translator(self, source: str, target: str):
        """Get or create Google Translator instance"""
        if self._google_translator is None:
            try:
                self._google_translator = GoogleTranslator(source=source, target=target)
            except Exception as e:
                logger.warning(f"Failed to initialize Google Translator: {e}")
                return None
        else:
            # Update source/target if changed
            if self._google_translator.source != source or self._google_translator.target != target:
                try:
                    self._google_translator = GoogleTranslator(source=source, target=target)
                except Exception as e:
                    logger.warning(f"Failed to update Google Translator: {e}")
                    return None
        return self._google_translator
    
    def _get_deepl_translator(self, source: str, target: str):
        """Get or create DeepL Translator instance (free tier)"""
        if self._deepl_translator is None:
            try:
                # DeepL free tier requires API key, but we can try without
                # If no API key, fallback to Google
                self._deepl_translator = DeepL(source=source, target=target, use_free_api=True)
            except Exception as e:
                logger.warning(f"Failed to initialize DeepL Translator: {e}")
                return None
        return self._deepl_translator
    
    def translate_batch(
        self,
        texts: List[str],
        source_lang: str = "en",
        target_lang: str = "tr",
        provider: Optional[str] = None
    ) -> List[str]:
        """
        Translate a batch of texts using free translation service
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            provider: Override default provider ("google" or "deepl")
            
        Returns:
            List of translated texts
        """
        if not texts:
            return []
        
        provider = provider or self.provider
        
        # Normalize language codes
        source_lang = LanguageDetector.normalize_language_code(source_lang)
        target_lang = LanguageDetector.normalize_language_code(target_lang)
        
        try:
            if provider == "google":
                translator = self._get_google_translator(source_lang, target_lang)
                if translator is None:
                    raise ValueError("Failed to initialize Google Translator")
                
                # Google Translate can handle batch translation
                translated = []
                for text in texts:
                    try:
                        if not text or not text.strip():
                            translated.append("")
                            continue
                        
                        result = translator.translate(text)
                        translated.append(result)
                    except Exception as e:
                        logger.warning(f"Translation error for text '{text[:50]}...': {e}")
                        translated.append(text)  # Fallback to original
                
                return translated
                
            elif provider == "deepl":
                translator = self._get_deepl_translator(source_lang, target_lang)
                if translator is None:
                    # Fallback to Google
                    logger.warning("DeepL unavailable, falling back to Google")
                    return self.translate_batch(texts, source_lang, target_lang, provider="google")
                
                # DeepL batch translation
                translated = []
                for text in texts:
                    try:
                        if not text or not text.strip():
                            translated.append("")
                            continue
                        
                        result = translator.translate(text)
                        translated.append(result)
                    except Exception as e:
                        logger.warning(f"DeepL translation error: {e}")
                        translated.append(text)  # Fallback to original
                
                return translated
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except Exception as e:
            logger.error(f"Free translation error: {e}")
            # Return original texts on error
            return texts
    
    def translate_single(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "tr",
        provider: Optional[str] = None
    ) -> str:
        """
        Translate a single text
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            provider: Override default provider
            
        Returns:
            Translated text
        """
        results = self.translate_batch([text], source_lang, target_lang, provider)
        return results[0] if results else text

