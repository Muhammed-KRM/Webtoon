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
        target_lang: str = "tr",
        cleaned_pages: Optional[List[bytes]] = None  # New: Save cleaned images
    ) -> str:
        """
        Save translated chapter to organized folder structure
        
        Structure:
        storage/
          {series_name}/
            {source_lang}_to_{target_lang}/
              chapter_{chapter_number}/
                page_001.jpg
                ...
                cleaned/  <-- New
                  page_001.jpg
                metadata.json
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
            
            # Create cleaned folder if needed
            cleaned_folder = chapter_folder / "cleaned"
            if cleaned_pages:
                cleaned_folder.mkdir(exist_ok=True)
            
            # Save pages (detect format from bytes)
            cdn_urls = []
            cleaned_cdn_urls = []
            
            for idx, page_bytes in enumerate(pages, start=1):
                # Detect extension
                extension = self._detect_extension(page_bytes)
                content_type = f"image/{'jpeg' if extension == 'jpg' else extension}"
                
                # 1. Save Final Translation
                # Generate object key for CDN
                object_key = f"{safe_series_name}/{source_lang}_to_{target_lang}/chapter_{chapter_number:04d}/page_{idx:03d}.{extension}"
                
                # Upload to CDN if enabled
                if self.cdn_service.cdn_enabled:
                    cdn_url = self.cdn_service.upload_image(
                        image_bytes=page_bytes,
                        object_key=object_key,
                        content_type=content_type
                    )
                    if cdn_url:
                        cdn_urls.append(cdn_url)
                
                # Save locally
                page_path = chapter_folder / f"page_{idx:03d}.{extension}"
                with open(page_path, 'wb') as f:
                    f.write(page_bytes)
                
                # 2. Save Cleaned Image (if provided)
                if cleaned_pages and idx <= len(cleaned_pages):
                    cleaned_bytes = cleaned_pages[idx-1]
                    if cleaned_bytes:
                        cleaned_extension = self._detect_extension(cleaned_bytes)
                        cleaned_key = f"{safe_series_name}/{source_lang}_to_{target_lang}/chapter_{chapter_number:04d}/cleaned/page_{idx:03d}.{cleaned_extension}"
                        
                        # Upload to CDN
                        if self.cdn_service.cdn_enabled:
                            cleaned_url = self.cdn_service.upload_image(
                                image_bytes=cleaned_bytes,
                                object_key=cleaned_key,
                                content_type=content_type
                            )
                            if cleaned_url:
                                cleaned_cdn_urls.append(cleaned_url)
                        
                        # Save locally
                        cleaned_path = cleaned_folder / f"page_{idx:03d}.{cleaned_extension}"
                        with open(cleaned_path, 'wb') as f:
                            f.write(cleaned_bytes)

            # Save metadata
            if metadata:
                if cdn_urls:
                    metadata['cdn_urls'] = cdn_urls
                if cleaned_cdn_urls:
                    metadata['cleaned_cdn_urls'] = cleaned_cdn_urls
                
                metadata['cdn_enabled'] = bool(self.cdn_service.cdn_enabled)
                
                metadata_path = chapter_folder / "metadata.json"
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved chapter {chapter_number} to: {chapter_folder}")
            return str(chapter_folder)
            
        except Exception as e:
            logger.error(f"Error saving chapter: {e}")
            raise
    
    def _detect_extension(self, data: bytes) -> str:
        """Helper to detect image extension"""
        if data.startswith(b'RIFF') and b'WEBP' in data[:12]:
            return "webp"
        elif data.startswith(b'\xff\xd8\xff'):
            return "jpg"
        elif data.startswith(b'\x89PNG'):
            return "png"
        return "jpg"
    
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

