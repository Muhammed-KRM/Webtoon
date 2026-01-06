"""
Free Translation Service - Uses free translation APIs with automatic fallback
Priority: Hugging Face > Argos Translate > Google Translate > DeepL
"""
from typing import List, Optional
from loguru import logger
from deep_translator import GoogleTranslator, DeepL
from app.services.language_detector import LanguageDetector

# Try to import alternative translators
try:
    from app.services.alternative_translator import AlternativeTranslator
    ALTERNATIVE_AVAILABLE = True
except ImportError:
    ALTERNATIVE_AVAILABLE = False
    logger.debug("Alternative translators not available")


class FreeTranslator:
    """Service for free translation with automatic fallback to best available service"""
    
    def __init__(self, provider: str = "auto"):
        """
        Initialize free translator
        
        Args:
            provider: "auto" (try all), "huggingface", "argos", "google", "deepl"
        """
        self.provider = provider
        self._google_translator = None
        self._deepl_translator = None
        self._alternative_translator = None
        
        # Initialize alternative translator if available
        if ALTERNATIVE_AVAILABLE and provider in ["auto", "huggingface", "argos"]:
            try:
                # Try Hugging Face first (faster, better quality)
                if provider in ["auto", "huggingface"]:
                    self._alternative_translator = AlternativeTranslator(provider="huggingface")
                    if self._alternative_translator.hf_pipeline:
                        logger.info("Using Hugging Face models for translation")
                        return
                # Fallback to Argos if Hugging Face not available
                if provider in ["auto", "argos"]:
                    self._alternative_translator = AlternativeTranslator(provider="argos")
                    logger.info("Using Argos Translate for translation")
            except Exception as e:
                logger.warning(f"Alternative translator initialization failed: {e}")
                self._alternative_translator = None
    
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
        
        # Try alternative translators first (if auto mode or explicitly requested)
        if (provider == "auto" or provider in ["huggingface", "argos"]) and self._alternative_translator:
            try:
                # Determine which alternative provider to use
                alt_provider = None
                if provider == "huggingface":
                    alt_provider = "huggingface"
                elif provider == "argos":
                    alt_provider = "argos"
                elif provider == "auto":
                    # Try Hugging Face first, then Argos
                    alt_provider = "huggingface" if self._alternative_translator.hf_pipeline else "argos"
                
                result = self._alternative_translator.translate_batch(
                    texts, source_lang, target_lang, provider=alt_provider
                )
                if result and len(result) == len(texts) and any(r for r in result if r):
                    logger.info(f"Successfully translated using alternative translator ({alt_provider})")
                    return result
            except Exception as e:
                logger.warning(f"Alternative translator failed: {e}, falling back to Google Translate")
        
        # Fallback to Google Translate or DeepL
        try:
            if provider == "auto" or provider == "google":
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

