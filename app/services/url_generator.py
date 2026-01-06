"""
URL Generator Service - Generates chapter URLs from patterns
"""
import re
from typing import List, Optional
from loguru import logger


class URLGenerator:
    """Service for generating chapter URLs from base URL patterns"""
    
    @staticmethod
    def parse_chapter_range(chapter_range: str) -> List[int]:
        """
        Parse chapter range string into list of chapter numbers
        
        Examples:
        - "1-10" -> [1, 2, 3, ..., 10]
        - "5,7,9" -> [5, 7, 9]
        - "1-5,10-15" -> [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15]
        """
        chapters = []
        parts = chapter_range.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                # Range
                start, end = part.split('-', 1)
                try:
                    start_num = int(start.strip())
                    end_num = int(end.strip())
                    chapters.extend(range(start_num, end_num + 1))
                except ValueError:
                    logger.warning(f"Invalid range format: {part}")
            else:
                # Single number
                try:
                    chapters.append(int(part))
                except ValueError:
                    logger.warning(f"Invalid chapter number: {part}")
        
        # Remove duplicates and sort
        return sorted(list(set(chapters)))
    
    @staticmethod
    def generate_chapter_urls(
        base_url: str,
        chapter_numbers: List[int],
        url_pattern: Optional[str] = None
    ) -> List[str]:
        """
        Generate chapter URLs from base URL and chapter numbers
        
        Args:
            base_url: Base URL or pattern (e.g., "https://webtoons.com/en/series/episode-{}/viewer")
            chapter_numbers: List of chapter numbers
            url_pattern: Optional pattern string (e.g., "episode-{}" or "chapter-{}")
            
        Returns:
            List of chapter URLs
        """
        urls = []
        
        # Try to detect pattern from base_url
        if url_pattern is None:
            url_pattern = URLGenerator._detect_pattern(base_url)
        
        for chapter_num in chapter_numbers:
            if url_pattern:
                # Replace pattern with chapter number
                url = base_url.replace(url_pattern, str(chapter_num))
            else:
                # Try common patterns
                url = URLGenerator._try_common_patterns(base_url, chapter_num)
            
            urls.append(url)
        
        return urls
    
    @staticmethod
    def _detect_pattern(url: str) -> Optional[str]:
        """Detect URL pattern from example URL"""
        # Look for common patterns
        patterns = [
            r'episode-(\d+)',
            r'chapter-(\d+)',
            r'bolum-(\d+)',
            r'episode_no=(\d+)',
            r'chapter_no=(\d+)',
            r'/ep(\d+)',
            r'/ch(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.I)
            if match:
                return match.group(0)  # Return the full matched pattern
        
        return None
    
    @staticmethod
    def _try_common_patterns(base_url: str, chapter_num: int) -> str:
        """Try common URL patterns"""
        # Webtoons.com pattern
        if 'webtoons.com' in base_url.lower() and 'episode_no=' in base_url:
            return re.sub(r'episode_no=\d+', f'episode_no={chapter_num}', base_url)
        
        # AsuraScans pattern
        if 'asurascans' in base_url.lower() and 'bolum-' in base_url:
            return re.sub(r'bolum-\d+', f'bolum-{chapter_num}', base_url)
        
        # Generic episode pattern
        if 'episode-' in base_url.lower():
            return re.sub(r'episode-\d+', f'episode-{chapter_num}', base_url, flags=re.I)
        
        # Generic chapter pattern
        if 'chapter-' in base_url.lower():
            return re.sub(r'chapter-\d+', f'chapter-{chapter_num}', base_url, flags=re.I)
        
        # If no pattern found, append chapter number
        if base_url.endswith('/'):
            return f"{base_url}chapter-{chapter_num}"
        else:
            return f"{base_url}/chapter-{chapter_num}"

