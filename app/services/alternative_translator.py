"""
Alternative Translation Services - Free/cheaper AI translation options
Supports: Argos Translate (offline), Hugging Face models
"""
from typing import List, Optional
from loguru import logger

# Try to import Argos Translate
try:
    import argostranslate.package
    import argostranslate.translate
    ARGOS_AVAILABLE = True
except (ImportError, Exception) as e:
    ARGOS_AVAILABLE = False
    logger.warning(f"Argos Translate not available: {e}")

# Try to import transformers (Hugging Face)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Install with: pip install transformers torch")


class AlternativeTranslator:
    """Alternative translation services (free/cheaper than OpenAI)"""
    
    def __init__(self, provider: str = "argos"):
        """
        Initialize alternative translator
        
        Args:
            provider: "argos" (offline), "huggingface" (free models), "ezai" (API)
        """
        self.provider = provider
        self.argos_models = {}
        self.hf_pipeline = None
        self._init_provider()
    
    def _init_provider(self):
        """Initialize the selected provider"""
        if self.provider == "argos" and ARGOS_AVAILABLE:
            try:
                # Download and install packages if needed
                argostranslate.package.update_package_index()
                available_packages = argostranslate.package.get_available_packages()
                logger.info(f"Argos Translate: {len(available_packages)} packages available")
            except Exception as e:
                logger.warning(f"Argos Translate initialization failed: {e}")
        
        elif self.provider == "huggingface" and TRANSFORMERS_AVAILABLE:
            try:
                # Use a lightweight translation model
                # Helsinki-NLP models are good for many language pairs
                model_name = "Helsinki-NLP/opus-mt-en-tr"  # English to Turkish
                self.hf_pipeline = pipeline(
                    "translation",
                    model=model_name,
                    device=0 if torch.cuda.is_available() else -1  # Use GPU if available
                )
                logger.info(f"Hugging Face model loaded: {model_name}")
            except Exception as e:
                logger.warning(f"Hugging Face initialization failed: {e}")
    
    def translate_batch(
        self,
        texts: List[str],
        source_lang: str = "en",
        target_lang: str = "tr",
        provider: Optional[str] = None
    ) -> List[str]:
        """
        Translate batch of texts using alternative provider
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            provider: Override default provider
            
        Returns:
            List of translated texts
        """
        if not texts:
            return []
        
        provider = provider or self.provider
        
        if provider == "argos" and ARGOS_AVAILABLE:
            return self._translate_with_argos(texts, source_lang, target_lang)
        elif provider == "huggingface" and TRANSFORMERS_AVAILABLE:
            return self._translate_with_huggingface(texts, source_lang, target_lang)
        else:
            logger.warning(f"Provider {provider} not available, returning original texts")
            return texts
    
    def _translate_with_argos(self, texts: List[str], source_lang: str, target_lang: str) -> List[str]:
        """Translate using Argos Translate (offline, free)"""
        try:
            # Argos uses language codes like "en", "tr"
            translated = []
            for text in texts:
                if not text or not text.strip():
                    translated.append("")
                    continue
                
                try:
                    result = argostranslate.translate.translate(text, source_lang, target_lang)
                    translated.append(result)
                except Exception as e:
                    logger.warning(f"Argos translation error: {e}")
                    translated.append(text)  # Fallback
            
            return translated
        except Exception as e:
            logger.error(f"Argos Translate batch error: {e}")
            return texts
    
    def _translate_with_huggingface(self, texts: List[str], source_lang: str, target_lang: str) -> List[str]:
        """Translate using Hugging Face models (free, requires model download)"""
        if not self.hf_pipeline:
            logger.warning("Hugging Face pipeline not initialized")
            return texts
        
        try:
            translated = []
            for text in texts:
                if not text or not text.strip():
                    translated.append("")
                    continue
                
                try:
                    result = self.hf_pipeline(text, max_length=512)
                    # Result format: [{"translation_text": "..."}]
                    if isinstance(result, list) and len(result) > 0:
                        translated.append(result[0].get("translation_text", text))
                    else:
                        translated.append(text)
                except Exception as e:
                    logger.warning(f"Hugging Face translation error: {e}")
                    translated.append(text)
            
            return translated
        except Exception as e:
            logger.error(f"Hugging Face batch error: {e}")
            return texts
    
    def translate_single(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "tr",
        provider: Optional[str] = None
    ) -> str:
        """Translate a single text"""
        results = self.translate_batch([text], source_lang, target_lang, provider)
        return results[0] if results else text

