"""
Advanced NER Service - Uses spaCy for professional named entity recognition
Falls back to regex-based NER if spaCy is not available
"""
import re
from typing import List, Dict, Optional
from loguru import logger

# Try to import spaCy
try:
    import spacy
    SPACY_AVAILABLE = True
except (ImportError, Exception) as e:
    SPACY_AVAILABLE = False
    logger.warning(f"spaCy not available: {e}. Using regex-based NER fallback.")


class AdvancedNERService:
    """Advanced NER service using spaCy with regex fallback"""
    
    def __init__(self, language: str = "en"):
        """
        Initialize NER service
        
        Args:
            language: Language code (en, tr, etc.)
        """
        self.language = language
        self.nlp = None
        self.use_spacy = False
        
        if SPACY_AVAILABLE:
            try:
                # Try to load spaCy model
                model_name = self._get_spacy_model(language)
                if model_name:
                    self.nlp = spacy.load(model_name)
                    self.use_spacy = True
                    logger.info(f"Loaded spaCy model: {model_name}")
                else:
                    logger.warning(f"No spaCy model found for {language}, using regex fallback")
            except Exception as e:
                logger.warning(f"Failed to load spaCy model: {e}. Using regex fallback")
        
        # Fallback regex patterns
        self._init_regex_patterns()
    
    def _get_spacy_model(self, lang: str) -> Optional[str]:
        """Get spaCy model name for language"""
        models = {
            "en": "en_core_web_sm",
            "tr": "tr_core_news_sm",  # May not be available
            "es": "es_core_news_sm",
            "fr": "fr_core_news_sm",
            "de": "de_core_news_sm",
        }
        return models.get(lang)
    
    def _init_regex_patterns(self):
        """Initialize regex patterns for fallback"""
        self.PROPER_NOUN_PATTERNS = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Capitalized words
            r'\b[A-Z]{2,}\b',  # All caps
        ]
        self.COMMON_WORDS = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        }
        self._compiled_patterns = [re.compile(p) for p in self.PROPER_NOUN_PATTERNS]
    
    def detect_proper_nouns(self, text: str) -> List[Dict[str, any]]:
        """
        Detect proper nouns using spaCy or regex fallback
        
        Args:
            text: Input text
            
        Returns:
            List of detected entities: [{"name": "John", "start": 0, "end": 4, "confidence": 0.9, "type": "PERSON"}, ...]
        """
        if not text or not text.strip():
            return []
        
        if self.use_spacy and self.nlp:
            return self._detect_with_spacy(text)
        else:
            return self._detect_with_regex(text)
    
    def _detect_with_spacy(self, text: str) -> List[Dict[str, any]]:
        """Detect entities using spaCy"""
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                # Filter for person, organization, location, and other proper nouns
                if ent.label_ in ["PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT"]:
                    entities.append({
                        "name": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": 0.9,  # spaCy doesn't provide confidence, use high default
                        "type": ent.label_,
                        "label": ent.label_
                    })
            
            return entities
        except Exception as e:
            logger.warning(f"spaCy detection failed: {e}, falling back to regex")
            return self._detect_with_regex(text)
    
    def _detect_with_regex(self, text: str) -> List[Dict[str, any]]:
        """Detect entities using regex (fallback)"""
        detected = []
        seen = set()
        
        for pattern in self._compiled_patterns:
            for match in pattern.finditer(text):
                name = match.group()
                start = match.start()
                end = match.end()
                
                if len(name) < 2 or len(name) > 50:
                    continue
                
                if (name, start) in seen:
                    continue
                seen.add((name, start))
                
                name_lower = name.lower()
                if name_lower in self.COMMON_WORDS:
                    continue
                
                confidence = self._calculate_confidence(name, text, start, end)
                
                if confidence > 0.3:
                    detected.append({
                        "name": name,
                        "start": start,
                        "end": end,
                        "confidence": confidence,
                        "type": "UNKNOWN",  # Regex can't determine type
                        "label": "UNKNOWN"
                    })
        
        return self._remove_overlaps(detected)
    
    def _calculate_confidence(self, name: str, text: str, start: int, end: int) -> float:
        """Calculate confidence for regex-detected entity"""
        confidence = 0.5
        
        words = name.split()
        if len(words) > 1:
            confidence += 0.2
        elif name[0].isupper() and name[1:].islower():
            confidence += 0.1
        
        if start == 0 or (start > 0 and text[start - 1] in '.!?\n'):
            confidence += 0.1
        
        if end < len(text) and text[end] in ".,!?;:":
            confidence += 0.1
        
        if 3 <= len(name) <= 20:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _remove_overlaps(self, detected: List[Dict]) -> List[Dict]:
        """Remove overlapping detections"""
        if not detected:
            return []
        
        sorted_detected = sorted(detected, key=lambda x: x.get('confidence', 0), reverse=True)
        result = []
        used_positions = set()
        
        for item in sorted_detected:
            start = item['start']
            end = item['end']
            
            overlaps = False
            for pos_start, pos_end in used_positions:
                if not (end <= pos_start or start >= pos_end):
                    overlaps = True
                    break
            
            if not overlaps:
                result.append(item)
                used_positions.add((start, end))
        
        result.sort(key=lambda x: x['start'])
        return result
    
    def extract_all_names(self, texts: List[str]) -> List[str]:
        """Extract all unique proper nouns from texts"""
        all_names = set()
        
        for text in texts:
            detected = self.detect_proper_nouns(text)
            for item in detected:
                name = item['name'].strip()
                if name:
                    all_names.add(name)
        
        return sorted(list(all_names))

