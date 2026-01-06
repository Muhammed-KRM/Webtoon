"""
Series Manager - Handles series creation, matching, and chapter conflict resolution
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Tuple, Dict, Any
from loguru import logger
from app.models.series import Series, Chapter, ChapterTranslation
from app.models.tag import Tag, Category
from app.core.enums import SeriesStatus, TranslationStatus
from app.services.file_manager import FileManager
from pathlib import Path
import re


class SeriesManager:
    """Manages series creation, matching, and conflict resolution"""
    
    @staticmethod
    def normalize_series_name(name: str) -> str:
        """Normalize series name for comparison (lowercase, remove special chars)"""
        if not name:
            return ""
        # Remove special characters, lowercase, strip
        normalized = re.sub(r'[^\w\s]', '', name.lower().strip())
        # Remove extra spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized
    
    @staticmethod
    def find_series_by_name(
        db: Session,
        series_name: str,
        exact_match: bool = True
    ) -> Optional[Series]:
        """
        Find series by name with intelligent matching
        
        Args:
            db: Database session
            series_name: Series name to search for
            exact_match: If True, use exact match. If False, use fuzzy match.
        
        Returns:
            Series if found, None otherwise
        """
        if not series_name:
            return None
        
        normalized_name = SeriesManager.normalize_series_name(series_name)
        
        if exact_match:
            # Try exact match first (case-insensitive)
            series = db.query(Series).filter(
                Series.title.ilike(series_name.strip())
            ).first()
            
            if series:
                return series
            
            # Try normalized match
            all_series = db.query(Series).filter(Series.is_active == True).all()
            for s in all_series:
                if SeriesManager.normalize_series_name(s.title) == normalized_name:
                    return s
        else:
            # Fuzzy match - find closest match
            all_series = db.query(Series).filter(Series.is_active == True).all()
            best_match = None
            best_score = 0
            
            for s in all_series:
                s_normalized = SeriesManager.normalize_series_name(s.title)
                # Simple similarity check
                if normalized_name in s_normalized or s_normalized in normalized_name:
                    score = min(len(normalized_name), len(s_normalized)) / max(len(normalized_name), len(s_normalized))
                    if score > best_score:
                        best_score = score
                        best_match = s
            
            if best_score > 0.8:  # 80% similarity threshold
                return best_match
        
        return None
    
    @staticmethod
    def create_or_get_series(
        db: Session,
        title: str,
        description: str,
        source_url: Optional[str] = None,
        source_site: Optional[str] = None,
        author: Optional[str] = None,
        cover_image_url: Optional[str] = None,
        category_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        genre: Optional[str] = None  # Legacy support
    ) -> Tuple[Series, bool]:
        """
        Create a new series or get existing one if name matches
        
        Returns:
            Tuple of (Series, is_new) where is_new is True if series was created
        """
        # Validate required fields
        if not title or not title.strip():
            raise ValueError("Series title is required")
        if not description or not description.strip():
            raise ValueError("Series description is required")
        
        # Try to find existing series
        existing_series = SeriesManager.find_series_by_name(db, title, exact_match=True)
        
        if existing_series:
            logger.info(f"Found existing series: {existing_series.id} - {existing_series.title}")
            # Update metadata if provided
            updated = False
            if source_url and not existing_series.source_url:
                existing_series.source_url = source_url
                updated = True
            if source_site and not existing_series.source_site:
                existing_series.source_site = source_site
                updated = True
            if author and not existing_series.author:
                existing_series.author = author
                updated = True
            if cover_image_url and not existing_series.cover_image_url:
                existing_series.cover_image_url = cover_image_url
                updated = True
            if category_id and not existing_series.category_id:
                existing_series.category_id = category_id
                updated = True
            
            # Update tags
            if tags:
                SeriesManager.add_tags_to_series(db, existing_series, tags)
            
            if updated:
                db.commit()
                db.refresh(existing_series)
            
            return existing_series, False
        
        # Create new series
        new_series = Series(
            title=title.strip(),
            description=description.strip(),
            source_url=source_url,
            source_site=source_site,
            author=author,
            cover_image_url=cover_image_url,
            category_id=category_id,
            genre=genre,  # Legacy support
            status=SeriesStatus.ONGOING,
            is_active=True,
            is_published=True
        )
        
        db.add(new_series)
        db.flush()  # Get ID without committing
        
        # Add tags
        if tags:
            SeriesManager.add_tags_to_series(db, new_series, tags)
        
        db.commit()
        db.refresh(new_series)
        
        logger.info(f"Created new series: {new_series.id} - {new_series.title}")
        return new_series, True
    
    @staticmethod
    def add_tags_to_series(db: Session, series: Series, tag_names: List[str]):
        """Add tags to a series (create tags if they don't exist, validate against enum)"""
        if not tag_names:
            return
        
        from app.core.tag_enum import WebtoonTag
        
        for tag_name in tag_names:
            if not tag_name or not tag_name.strip():
                continue
            
            # Normalize and validate tag using enum
            normalized_tag = WebtoonTag.normalize_tag(tag_name.strip())
            
            if not normalized_tag:
                logger.warning(f"Invalid tag name: {tag_name}, skipping")
                continue
            
            # Find or create tag using normalized name
            tag = db.query(Tag).filter(
                or_(
                    Tag.name.ilike(normalized_tag),
                    Tag.slug == normalized_tag
                )
            ).first()
            
            if not tag:
                # Create new tag with normalized name
                tag = Tag(
                    name=normalized_tag.replace('-', ' ').title(),  # "action", "system" -> "Action", "System"
                    slug=normalized_tag,  # "action", "system"
                    usage_count=0
                )
                db.add(tag)
                db.flush()
            
            # Add tag to series if not already added
            if tag not in series.tags:
                series.tags.append(tag)
                tag.usage_count += 1
    
    @staticmethod
    def create_or_update_chapter(
        db: Session,
        series_id: int,
        chapter_number: int,
        source_url: Optional[str] = None,
        title: Optional[str] = None,
        page_count: int = 0,
        replace_existing: bool = True
    ) -> Tuple[Chapter, bool]:
        """
        Create a new chapter or update existing one if chapter_number matches
        
        Args:
            db: Database session
            series_id: Series ID
            chapter_number: Chapter number
            source_url: Chapter source URL
            title: Chapter title
            page_count: Number of pages
            replace_existing: If True, replace existing chapter. If False, skip if exists.
        
        Returns:
            Tuple of (Chapter, is_new) where is_new is True if chapter was created
        """
        # Check if chapter already exists
        existing_chapter = db.query(Chapter).filter(
            and_(
                Chapter.series_id == series_id,
                Chapter.chapter_number == chapter_number
            )
        ).first()
        
        if existing_chapter:
            if replace_existing:
                logger.info(f"Updating existing chapter {chapter_number} in series {series_id}")
                # Update existing chapter
                if source_url:
                    existing_chapter.source_url = source_url
                if title:
                    existing_chapter.title = title
                if page_count > 0:
                    existing_chapter.page_count = page_count
                
                db.commit()
                db.refresh(existing_chapter)
                return existing_chapter, False
            else:
                logger.info(f"Chapter {chapter_number} already exists, skipping")
                return existing_chapter, False
        
        # Create new chapter
        new_chapter = Chapter(
            series_id=series_id,
            chapter_number=chapter_number,
            source_url=source_url,
            title=title or f"Chapter {chapter_number}",
            page_count=page_count,
            is_published=True
        )
        
        db.add(new_chapter)
        db.commit()
        db.refresh(new_chapter)
        
        logger.info(f"Created new chapter {chapter_number} in series {series_id}")
        return new_chapter, True
    
    @staticmethod
    def handle_chapter_conflict(
        db: Session,
        chapter: Chapter,
        new_translation_data: Dict[str, Any],
        source_lang: str,
        target_lang: str,
        replace_existing: bool = True
    ) -> ChapterTranslation:
        """
        Handle chapter translation conflict (same chapter, same language pair)
        
        Args:
            db: Database session
            chapter: Chapter object
            new_translation_data: New translation data (pages, storage_path, etc.)
            source_lang: Source language
            target_lang: Target language
            replace_existing: If True, replace existing translation. If False, keep existing.
        
        Returns:
            ChapterTranslation object
        """
        # Check if translation already exists
        existing_translation = db.query(ChapterTranslation).filter(
            and_(
                ChapterTranslation.chapter_id == chapter.id,
                ChapterTranslation.source_lang == source_lang,
                ChapterTranslation.target_lang == target_lang
            )
        ).first()
        
        if existing_translation:
            if replace_existing:
                logger.info(f"Replacing existing translation for chapter {chapter.id} ({source_lang}->{target_lang})")
                
                # Delete old files if storage path exists
                if existing_translation.storage_path:
                    try:
                        old_path = Path(existing_translation.storage_path)
                        if old_path.exists() and old_path.is_dir():
                            import shutil
                            shutil.rmtree(old_path)
                            logger.info(f"Deleted old translation files: {old_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete old translation files: {e}")
                
                # Update existing translation
                existing_translation.storage_path = new_translation_data.get("storage_path", "")
                existing_translation.page_count = new_translation_data.get("page_count", 0)
                existing_translation.status = TranslationStatus.COMPLETED
                existing_translation.is_published = True
                
                db.commit()
                db.refresh(existing_translation)
                
                return existing_translation
            else:
                logger.info(f"Translation already exists, keeping existing")
                return existing_translation
        
        # Create new translation
        new_translation = ChapterTranslation(
            chapter_id=chapter.id,
            source_lang=source_lang,
            target_lang=target_lang,
            storage_path=new_translation_data.get("storage_path", ""),
            page_count=new_translation_data.get("page_count", 0),
            status=TranslationStatus.COMPLETED,
            is_published=True
        )
        
        db.add(new_translation)
        db.commit()
        db.refresh(new_translation)
        
        logger.info(f"Created new translation for chapter {chapter.id} ({source_lang}->{target_lang})")
        return new_translation

