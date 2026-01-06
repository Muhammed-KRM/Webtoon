"""
Named Entity Recognition (NER) Service - Detects special names in text
Uses regex-based detection (lightweight, fast)
For better accuracy, use AdvancedNERService with spaCy
"""
import re
from typing import List, Dict, Tuple
from loguru import logger


class NERService:
    """Service for detecting proper nouns and special names in text"""
    
    # Common patterns for proper nouns
    PROPER_NOUN_PATTERNS = [
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Capitalized words (John, Mary Jane)
        r'\b[A-Z]{2,}\b',  # All caps (USA, NASA)
    ]
    
    # Common words that are NOT proper nouns (stop words)
    COMMON_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'what', 'which', 'who', 'where', 'when', 'why', 'how', 'all',
        'each', 'every', 'some', 'any', 'no', 'not', 'yes', 'ok', 'okay'
    }
    
    # Common titles and honorifics
    TITLES = {'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'sir', 'madam', 'lord', 'lady'}
    
    def __init__(self, min_length: int = 2, max_length: int = 50):
        """
        Initialize NER service
        
        Args:
            min_length: Minimum length of a proper noun
            max_length: Maximum length of a proper noun
        """
        self.min_length = min_length
        self.max_length = max_length
        self._compiled_patterns = [re.compile(pattern) for pattern in self.PROPER_NOUN_PATTERNS]
    
    def detect_proper_nouns(self, text: str) -> List[Dict[str, any]]:
        """
        Detect proper nouns in text
        
        Args:
            text: Input text
            
        Returns:
            List of detected proper nouns with positions
            Format: [{"name": "John", "start": 0, "end": 4, "confidence": 0.8}, ...]
        """
        if not text or not text.strip():
            return []
        
        detected = []
        seen = set()
        
        # Try each pattern
        for pattern in self._compiled_patterns:
            for match in pattern.finditer(text):
                name = match.group()
                start = match.start()
                end = match.end()
                
                # Skip if too short or too long
                if len(name) < self.min_length or len(name) > self.max_length:
                    continue
                
                # Skip if already detected
                if (name, start) in seen:
                    continue
                seen.add((name, start))
                
                # Check if it's a common word
                name_lower = name.lower()
                if name_lower in self.COMMON_WORDS:
                    continue
                
                # Check if it starts with a title
                words = name.split()
                if words and words[0].lower() in self.TITLES:
                    # Include title as part of name
                    pass
                
                # Calculate confidence based on capitalization pattern
                confidence = self._calculate_confidence(name, text, start, end)
                
                # Only include if confidence is reasonable
                if confidence > 0.3:
                    detected.append({
                        "name": name,
                        "start": start,
                        "end": end,
                        "confidence": confidence
                    })
        
        # Remove overlapping detections (keep higher confidence)
        detected = self._remove_overlaps(detected)
        
        return detected
    
    def _calculate_confidence(
        self,
        name: str,
        text: str,
        start: int,
        end: int
    ) -> float:
        """
        Calculate confidence score for a detected proper noun
        
        Args:
            name: Detected name
            text: Full text
            start: Start position
            end: End position
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.5  # Base confidence
        
        # Check capitalization pattern
        words = name.split()
        if len(words) > 1:
            # Multiple words - likely a proper noun
            confidence += 0.2
        elif name[0].isupper() and name[1:].islower():
            # Single capitalized word
            confidence += 0.1
        
        # Check if it's at the start of a sentence
        if start == 0 or text[start - 1] in '.!?\n':
            confidence += 0.1
        
        # Check if it's followed by common proper noun indicators
        if end < len(text):
            next_char = text[end]
            if next_char in ".,!?;:":
                confidence += 0.1
        
        # Check length (very short or very long are less likely)
        if 3 <= len(name) <= 20:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _remove_overlaps(self, detected: List[Dict]) -> List[Dict]:
        """Remove overlapping detections, keeping higher confidence ones"""
        if not detected:
            return []
        
        # Sort by confidence (descending)
        sorted_detected = sorted(detected, key=lambda x: x['confidence'], reverse=True)
        
        result = []
        used_positions = set()
        
        for item in sorted_detected:
            start = item['start']
            end = item['end']
            
            # Check if position overlaps with already added items
            overlaps = False
            for pos_start, pos_end in used_positions:
                if not (end <= pos_start or start >= pos_end):
                    overlaps = True
                    break
            
            if not overlaps:
                result.append(item)
                used_positions.add((start, end))
        
        # Sort by position
        result.sort(key=lambda x: x['start'])
        
        return result
    
    def extract_all_names(self, texts: List[str]) -> List[str]:
        """
        Extract all unique proper nouns from a list of texts
        
        Args:
            texts: List of texts
            
        Returns:
            List of unique proper noun names
        """
        all_names = set()
        
        for text in texts:
            detected = self.detect_proper_nouns(text)
            for item in detected:
                name = item['name'].strip()
                if name:
                    all_names.add(name)
        
        return sorted(list(all_names))

