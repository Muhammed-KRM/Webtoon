"""
File Manager Service - Organizes translated chapters into folders
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
from app.core.config import settings
from app.services.cdn_service import CDNService


class FileManager:
    """Service for managing translated chapter files"""
    
    def __init__(self):
        self.storage_path = Path(settings.STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.cdn_service = CDNService()  # Initialize CDN service
    
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
            
            # Save pages (detect format from bytes)
            cdn_urls = []  # Store CDN URLs if CDN enabled
            
            for idx, page_bytes in enumerate(pages, start=1):
                # Detect image format from magic bytes
                # WebP: RIFF...WEBP
                if page_bytes.startswith(b'RIFF') and b'WEBP' in page_bytes[:12]:
                    extension = "webp"
                    content_type = "image/webp"
                # JPEG: FF D8 FF
                elif page_bytes.startswith(b'\xff\xd8\xff'):
                    extension = "jpg"
                    content_type = "image/jpeg"
                # PNG: 89 50 4E 47
                elif page_bytes.startswith(b'\x89PNG'):
                    extension = "png"
                    content_type = "image/png"
                else:
                    extension = "jpg"  # Default fallback
                    content_type = "image/jpeg"
                
                # Generate object key for CDN
                object_key = f"{safe_series_name}/{source_lang}_to_{target_lang}/chapter_{chapter_number:04d}/page_{idx:03d}.{extension}"
                
                # Upload to CDN if enabled
                cdn_url = None
                if self.cdn_service.cdn_enabled:
                    cdn_url = self.cdn_service.upload_image(
                        image_bytes=page_bytes,
                        object_key=object_key,
                        content_type=content_type
                    )
                    if cdn_url:
                        cdn_urls.append(cdn_url)
                        logger.info(f"Uploaded page {idx} to CDN: {cdn_url}")
                
                # Also save locally (fallback if CDN fails or disabled)
                page_path = chapter_folder / f"page_{idx:03d}.{extension}"
                with open(page_path, 'wb') as f:
                    f.write(page_bytes)
            
            # Save metadata (include CDN URLs if available)
            if metadata:
                if cdn_urls:
                    metadata['cdn_urls'] = cdn_urls
                    metadata['cdn_enabled'] = True
                else:
                    metadata['cdn_enabled'] = False
                
                metadata_path = chapter_folder / "metadata.json"
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved chapter {chapter_number} to: {chapter_folder}")
            if cdn_urls:
                logger.info(f"Chapter {chapter_number} uploaded to CDN with {len(cdn_urls)} images")
            
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

