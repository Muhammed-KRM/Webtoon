"""
AI Translator Service - Context-aware translation with Cached Input
"""
import json
from typing import List, Optional, Dict
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
    
    def _build_system_prompt_with_glossary(
        self,
        glossary_dict: Optional[Dict[str, str]],
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Build system prompt with glossary integration
        
        Args:
            glossary_dict: Dictionary of {original: translated} terms
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Enhanced system prompt with glossary instructions
        """
        base_prompt = self.system_prompt
        
        if glossary_dict and len(glossary_dict) > 0:
            # Build glossary section
            glossary_items = []
            for original, translated in glossary_dict.items():
                glossary_items.append(f'  - "{original}" → "{translated}"')
            
            glossary_section = f"""

CRITICAL GLOSSARY RULES (MANDATORY):
The following terms MUST be translated EXACTLY as specified. If you see these terms, use ONLY the provided translation:
{chr(10).join(glossary_items)}

When you encounter any of these terms in the source text, you MUST translate them to the exact value shown above.
Do NOT use alternative translations, synonyms, or variations. Consistency is critical.
"""
            return base_prompt + glossary_section
        
        return base_prompt
    
    def translate_batch_context_aware(
        self,
        all_texts: List[str],
        source_lang: str = "en",
        target_lang: str = "tr",
        use_cache: bool = True,
        glossary_dict: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """
        Translate all texts in a batch with context awareness and glossary support
        
        This method sends all texts at once to maintain consistency
        across the entire chapter. Uses smart chunking for large texts.
        
        Args:
            all_texts: List of all texts from the chapter
            source_lang: Source language code
            target_lang: Target language (default: "tr")
            use_cache: Whether to use Cached Input for system prompt
            glossary_dict: Dictionary of {original: translated} terms for consistency
            
        Returns:
            List of translated texts in the same order
        """
        if not all_texts:
            return []
        
        try:
            logger.info(f"Translating {len(all_texts)} texts to {target_lang}")
            
            # Check if we need smart chunking (estimate tokens: ~4 chars = 1 token)
            estimated_tokens = sum(len(text) for text in all_texts) // 4
            max_safe_tokens = 100000  # Safe limit for GPT-4o-mini (128k max, but use 100k for safety)
            
            if estimated_tokens > max_safe_tokens:
                logger.info(f"Large text detected ({estimated_tokens} estimated tokens), using smart chunking")
                return self._translate_with_chunking(all_texts, source_lang, target_lang, use_cache, glossary_dict)
            
            # Get language names
            source_name = LanguageDetector.get_language_name(source_lang) or source_lang
            target_name = LanguageDetector.get_language_name(target_lang) or target_lang
            
            # Build system prompt with glossary
            system_prompt = self._build_system_prompt_with_glossary(glossary_dict, source_lang, target_lang)
            
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
                {"role": "system", "content": system_prompt},
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
    
    def _translate_with_chunking(
        self,
        all_texts: List[str],
        source_lang: str,
        target_lang: str,
        use_cache: bool,
        glossary_dict: Optional[Dict[str, str]]
    ) -> List[str]:
        """
        Translate large texts using smart chunking to avoid token limits
        
        Args:
            all_texts: List of all texts
            source_lang: Source language code
            target_lang: Target language code
            use_cache: Whether to use Cached Input
            glossary_dict: Glossary dictionary
            
        Returns:
            List of translated texts
        """
        # Chunk size: ~20k tokens per chunk (safe limit)
        chunk_size = 80000  # ~80k characters = ~20k tokens
        chunks = []
        current_chunk = []
        current_size = 0
        
        # Split texts into chunks
        for text in all_texts:
            text_size = len(text)
            if current_size + text_size > chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = [text]
                current_size = text_size
            else:
                current_chunk.append(text)
                current_size += text_size
        
        if current_chunk:
            chunks.append(current_chunk)
        
        logger.info(f"Split {len(all_texts)} texts into {len(chunks)} chunks")
        
        # Translate each chunk with context from previous chunk
        all_translations = []
        previous_context = None
        
        for idx, chunk in enumerate(chunks):
            logger.info(f"Translating chunk {idx + 1}/{len(chunks)} ({len(chunk)} texts)")
            
            # Build context summary from previous chunk
            context_prompt = ""
            if previous_context:
                context_prompt = f"""
PREVIOUS CONTEXT (for consistency):
The previous part of this chapter contained these key terms and character names:
{json.dumps(previous_context[:10], ensure_ascii=False)}  # First 10 translations for context

Maintain consistency with the previous translations, especially for character names and special terms.
"""
            
            # Get language names
            source_name = LanguageDetector.get_language_name(source_lang) or source_lang
            target_name = LanguageDetector.get_language_name(target_lang) or target_lang
            
            # Build system prompt with glossary
            system_prompt = self._build_system_prompt_with_glossary(glossary_dict, source_lang, target_lang)
            
            # Prepare user prompt
            user_prompt = f"""Translate the following text list from {source_name} ({source_lang}) to {target_name} ({target_lang}).
This is part {idx + 1} of {len(chunks)} of a webtoon chapter.{context_prompt}

IMPORTANT RULES:
1. Keep character names consistent with previous parts
2. Maintain consistent honorifics and addressing styles
3. Preserve the tone of speech (formal, casual, rude, etc.)
4. Translate webtoon slang and special terms correctly
5. Output ONLY a JSON list, no other explanations

Input List:
{json.dumps(chunk, ensure_ascii=False, indent=2)}
"""
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Prepare cache control
            extra_body = {}
            if use_cache:
                extra_body["cache_control"] = self.cache_control
            
            # Call OpenAI API
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    extra_body=extra_body if use_cache else None
                )
                
                content = response.choices[0].message.content
                
                # Parse response
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict):
                        translations = parsed.get("translations") or parsed.get("texts") or list(parsed.values())[0]
                    else:
                        translations = parsed
                    
                    if isinstance(translations, list):
                        chunk_translations = translations
                    else:
                        chunk_translations = self._fallback_parse(content)
                    
                    # Validate length
                    if len(chunk_translations) != len(chunk):
                        logger.warning(
                            f"Chunk {idx + 1} translation count mismatch: "
                            f"expected {len(chunk)}, got {len(chunk_translations)}"
                        )
                        # Pad or truncate
                        if len(chunk_translations) < len(chunk):
                            chunk_translations.extend([""] * (len(chunk) - len(chunk_translations)))
                        else:
                            chunk_translations = chunk_translations[:len(chunk)]
                    
                    all_translations.extend(chunk_translations)
                    previous_context = chunk_translations  # Store for next chunk context
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in chunk {idx + 1}: {e}")
                    # Fallback: use original texts
                    all_translations.extend(chunk)
                    previous_context = chunk
                    
            except Exception as e:
                logger.error(f"Error translating chunk {idx + 1}: {e}")
                # Fallback: use original texts
                all_translations.extend(chunk)
                previous_context = chunk
        
        # Final validation
        if len(all_translations) != len(all_texts):
            logger.warning(
                f"Final translation count mismatch: expected {len(all_texts)}, got {len(all_translations)}"
            )
            if len(all_translations) < len(all_texts):
                all_translations.extend([""] * (len(all_texts) - len(all_translations)))
            else:
                all_translations = all_translations[:len(all_texts)]
        
        logger.info(f"Successfully translated {len(all_translations)} texts using chunking")
        return all_translations

