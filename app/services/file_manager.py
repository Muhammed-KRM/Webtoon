"""
File Manager Service - Organizes translated chapters into folders
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
from app.core.config import settings


class FileManager:
    """Service for managing translated chapter files"""
    
    def __init__(self):
        self.storage_path = Path(settings.STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save_chapter(
        self,
        series_name: str,
        chapter_number: int,
        pages: List[bytes],
        metadata: Optional[Dict] = None,
        source_lang: str = "en",
        target_lang: str = "tr"
    ) -> str:
        """
        Save translated chapter to organized folder structure
        
        Structure:
        storage/
          {series_name}/
            {source_lang}_to_{target_lang}/
              chapter_{chapter_number}/
                page_001.jpg
                page_002.jpg
                ...
                metadata.json
        
        Args:
            series_name: Name of the webtoon series
            chapter_number: Chapter number
            pages: List of processed image bytes
            metadata: Additional metadata (original texts, translated texts, etc.)
            source_lang: Source language code (e.g., "en", "ko")
            target_lang: Target language code (e.g., "tr", "es")
            
        Returns:
            Path to saved chapter folder
        """
        try:
            # Sanitize series name for filesystem
            safe_series_name = self._sanitize_filename(series_name)
            
            # Create folder structure
            chapter_folder = (
                self.storage_path / 
                safe_series_name / 
                f"{source_lang}_to_{target_lang}" / 
                f"chapter_{chapter_number:04d}"
            )
            chapter_folder.mkdir(parents=True, exist_ok=True)
            
            # Save pages
            for idx, page_bytes in enumerate(pages, start=1):
                page_path = chapter_folder / f"page_{idx:03d}.jpg"
                with open(page_path, 'wb') as f:
                    f.write(page_bytes)
            
            # Save metadata
            if metadata:
                metadata_path = chapter_folder / "metadata.json"
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved chapter {chapter_number} to: {chapter_folder}")
            return str(chapter_folder)
            
        except Exception as e:
            logger.error(f"Error saving chapter: {e}")
            raise
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename
    
    def get_chapter_path(
        self,
        series_name: str,
        chapter_number: int,
        source_lang: str = "en",
        target_lang: str = "tr"
    ) -> Optional[Path]:
        """Get path to saved chapter if it exists"""
        safe_series_name = self._sanitize_filename(series_name)
        chapter_folder = (
            self.storage_path / 
            safe_series_name / 
            f"{source_lang}_to_{target_lang}" / 
            f"chapter_{chapter_number:04d}"
        )
        
        if chapter_folder.exists():
            return chapter_folder
        return None
    
    def list_chapters(
        self,
        series_name: str,
        source_lang: str = "en",
        target_lang: str = "tr"
    ) -> List[int]:
        """List all available chapter numbers for a series"""
        safe_series_name = self._sanitize_filename(series_name)
        translation_folder = (
            self.storage_path / 
            safe_series_name / 
            f"{source_lang}_to_{target_lang}"
        )
        
        if not translation_folder.exists():
            return []
        
        chapters = []
        for item in translation_folder.iterdir():
            if item.is_dir() and item.name.startswith('chapter_'):
                try:
                    chapter_num = int(item.name.split('_')[1])
                    chapters.append(chapter_num)
                except:
                    continue
        
        return sorted(chapters)

