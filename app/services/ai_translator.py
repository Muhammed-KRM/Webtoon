"""
AI Translator Service - Context-aware translation with Cached Input
"""
import json
from typing import List, Optional
from openai import OpenAI
from loguru import logger
from app.core.config import settings
from app.services.language_detector import LanguageDetector


class AITranslator:
    """Service for AI-powered translation with context awareness"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.system_prompt = self._get_system_prompt()
        self.cache_control = {"type": "ephemeral"}  # Enable Cached Input
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for translation (English for global compatibility)"""
        return """You are a professional webtoon and comic book translator.
Your tasks:
1. Translate texts naturally and fluently to the target language
2. Keep character names and honorifics consistent throughout the entire chapter
3. Understand and translate webtoon language (slang, special terms) correctly
4. Preserve the tone of speech and character personality
5. Output ONLY a JSON list: ["translation1", "translation2", ...]"""
    
    def translate_batch_context_aware(
        self,
        all_texts: List[str],
        source_lang: str = "en",
        target_lang: str = "tr",
        use_cache: bool = True
    ) -> List[str]:
        """
        Translate all texts in a batch with context awareness
        
        This method sends all texts at once to maintain consistency
        across the entire chapter.
        
        Args:
            all_texts: List of all texts from the chapter
            target_lang: Target language (default: "tr")
            use_cache: Whether to use Cached Input for system prompt
            
        Returns:
            List of translated texts in the same order
        """
        if not all_texts:
            return []
        
        try:
            logger.info(f"Translating {len(all_texts)} texts to {target_lang}")
            
            # Get language names
            source_name = LanguageDetector.get_language_name(source_lang) or source_lang
            target_name = LanguageDetector.get_language_name(target_lang) or target_lang
            
            # Prepare user prompt (English for global compatibility)
            user_prompt = f"""Translate the following text list from {source_name} ({source_lang}) to {target_name} ({target_lang}).
This is a webtoon chapter. Translate all texts consistently within context.

IMPORTANT RULES:
1. Keep character names consistent throughout the list (e.g., "Jin" should remain "Jin" everywhere)
2. Maintain consistent honorifics and addressing styles
3. Preserve the tone of speech (formal, casual, rude, etc.)
4. Translate webtoon slang and special terms correctly
5. Output ONLY a JSON list, no other explanations

Input List:
{json.dumps(all_texts, ensure_ascii=False, indent=2)}
"""
            
            # Prepare messages
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Prepare cache control (only for system message)
            extra_body = {}
            if use_cache:
                extra_body["cache_control"] = self.cache_control
                logger.debug("Using Cached Input for system prompt")
            
            # Call OpenAI API
            # Note: Cached Input is handled via extra_body for system message
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for consistency
                extra_body=extra_body if use_cache else None
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                # Response might be wrapped in JSON object
                parsed = json.loads(content)
                
                # If it's a JSON object, look for translations array
                if isinstance(parsed, dict):
                    # Look for common keys
                    translations = parsed.get("translations") or parsed.get("texts") or list(parsed.values())[0]
                else:
                    translations = parsed
                
                # Ensure it's a list
                if isinstance(translations, list):
                    result = translations
                else:
                    # Fallback: split by lines or commas
                    logger.warning("Response not in expected format, attempting fallback parsing")
                    result = self._fallback_parse(content)
                
                # Validate length
                if len(result) != len(all_texts):
                    logger.warning(
                        f"Translation count mismatch: expected {len(all_texts)}, got {len(result)}"
                    )
                    # Pad or truncate as needed
                    if len(result) < len(all_texts):
                        result.extend([""] * (len(all_texts) - len(result)))
                    else:
                        result = result[:len(all_texts)]
                
                logger.info(f"Successfully translated {len(result)} texts")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Response content: {content[:500]}")
                # Fallback parsing
                return self._fallback_parse(content)
                
        except Exception as e:
            logger.error(f"AI Translation Error: {e}")
            # Return original texts on error
            return all_texts
    
    def _fallback_parse(self, content: str) -> List[str]:
        """Fallback parsing if JSON parsing fails"""
        # Try to extract list from text
        content = content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
        
        # Try to parse as JSON array directly
        try:
            return json.loads(content)
        except:
            pass
        
        # Try to find array in text
        import re
        array_match = re.search(r'\[.*?\]', content, re.DOTALL)
        if array_match:
            try:
                return json.loads(array_match.group())
            except:
                pass
        
        # Last resort: split by newlines
        return [line.strip() for line in content.split("\n") if line.strip()]

