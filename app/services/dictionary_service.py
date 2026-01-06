"""
Dictionary Management Service - Manages special names glossary for translation consistency
"""
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from loguru import logger
from datetime import datetime
from app.models.dictionary import SeriesDictionary, DictionaryEntry
from app.models.series import Series


class DictionaryService:
    """Service for managing series translation dictionaries"""
    
    MAX_ENTRIES = 1000  # Maximum entries per dictionary before cleanup
    MIN_USAGE_COUNT = 2  # Minimum usage count to keep during cleanup
    
    @staticmethod
    def get_or_create_dictionary(
        db: Session,
        series_id: int,
        source_lang: str,
        target_lang: str
    ) -> SeriesDictionary:
        """
        Get or create a dictionary for a series and language pair
        
        Args:
            db: Database session
            series_id: Series ID
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            SeriesDictionary instance
        """
        dictionary = db.query(SeriesDictionary).filter(
            and_(
                SeriesDictionary.series_id == series_id,
                SeriesDictionary.source_lang == source_lang,
                SeriesDictionary.target_lang == target_lang
            )
        ).first()
        
        if not dictionary:
            dictionary = SeriesDictionary(
                series_id=series_id,
                source_lang=source_lang,
                target_lang=target_lang,
                max_entries=DictionaryService.MAX_ENTRIES
            )
            db.add(dictionary)
            db.commit()
            db.refresh(dictionary)
            logger.info(f"Created dictionary for series {series_id} ({source_lang}->{target_lang})")
        
        return dictionary
    
    @staticmethod
    def lookup_name(
        db: Session,
        dictionary_id: int,
        original_name: str
    ) -> Optional[DictionaryEntry]:
        """
        Look up a name in the dictionary
        
        Args:
            db: Database session
            dictionary_id: Dictionary ID
            original_name: Original name to look up
            
        Returns:
            DictionaryEntry if found, None otherwise
        """
        entry = db.query(DictionaryEntry).filter(
            and_(
                DictionaryEntry.dictionary_id == dictionary_id,
                DictionaryEntry.original_name.ilike(original_name)  # Case-insensitive
            )
        ).first()
        
        return entry
    
    @staticmethod
    def add_or_update_entry(
        db: Session,
        dictionary_id: int,
        original_name: str,
        translated_name: str,
        is_proper_noun: str = "auto"
    ) -> DictionaryEntry:
        """
        Add or update a dictionary entry
        
        Args:
            db: Database session
            dictionary_id: Dictionary ID
            original_name: Original name
            translated_name: Translated name
            is_proper_noun: "auto", "yes", or "no"
            
        Returns:
            DictionaryEntry instance
        """
        # Try to find existing entry (case-insensitive)
        entry = db.query(DictionaryEntry).filter(
            and_(
                DictionaryEntry.dictionary_id == dictionary_id,
                DictionaryEntry.original_name.ilike(original_name)
            )
        ).first()
        
        if entry:
            # Update existing entry
            entry.translated_name = translated_name
            entry.usage_count += 1
            entry.last_used_at = datetime.utcnow()
            if is_proper_noun != "auto":
                entry.is_proper_noun = is_proper_noun
        else:
            # Create new entry
            entry = DictionaryEntry(
                dictionary_id=dictionary_id,
                original_name=original_name,
                translated_name=translated_name,
                usage_count=1,
                is_proper_noun=is_proper_noun,
                last_used_at=datetime.utcnow()
            )
            db.add(entry)
        
        db.commit()
        db.refresh(entry)
        
        return entry
    
    @staticmethod
    def apply_dictionary(
        db: Session,
        dictionary_id: int,
        texts: List[str]
    ) -> Tuple[List[str], Dict[str, str]]:
        """
        Apply dictionary to texts - replace known names with translations
        
        Args:
            db: Database session
            dictionary_id: Dictionary ID
            texts: List of texts to process
            
        Returns:
            Tuple of (processed_texts, replacements_dict)
            replacements_dict: {original_name: translated_name, ...}
        """
        # Get all dictionary entries
        entries = db.query(DictionaryEntry).filter(
            DictionaryEntry.dictionary_id == dictionary_id
        ).all()
        
        if not entries:
            return texts, {}
        
        # Sort by length (longest first) to handle compound names
        entries_sorted = sorted(entries, key=lambda e: len(e.original_name), reverse=True)
        
        processed_texts = []
        replacements = {}
        
        for text in texts:
            processed_text = text
            text_replacements = {}
            
            # Apply each dictionary entry
            for entry in entries_sorted:
                original = entry.original_name
                translated = entry.translated_name
                
                # Case-insensitive replacement
                import re
                pattern = re.compile(re.escape(original), re.IGNORECASE)
                
                if pattern.search(processed_text):
                    processed_text = pattern.sub(translated, processed_text)
                    text_replacements[original] = translated
                    replacements[original] = translated
            
            processed_texts.append(processed_text)
        
        return processed_texts, replacements
    
    @staticmethod
    def cleanup_dictionary(db: Session, dictionary_id: int) -> int:
        """
        Clean up dictionary by removing least-used entries
        
        Args:
            db: Database session
            dictionary_id: Dictionary ID
            
        Returns:
            Number of entries removed
        """
        dictionary = db.query(SeriesDictionary).filter(
            SeriesDictionary.id == dictionary_id
        ).first()
        
        if not dictionary:
            return 0
        
        # Count current entries
        entry_count = db.query(func.count(DictionaryEntry.id)).filter(
            DictionaryEntry.dictionary_id == dictionary_id
        ).scalar()
        
        if entry_count <= dictionary.max_entries:
            return 0
        
        # Get entries sorted by usage count and last used date
        entries_to_remove = db.query(DictionaryEntry).filter(
            DictionaryEntry.dictionary_id == dictionary_id
        ).order_by(
            DictionaryEntry.usage_count.asc(),
            DictionaryEntry.last_used_at.asc()
        ).limit(entry_count - dictionary.max_entries).all()
        
        removed_count = len(entries_to_remove)
        
        for entry in entries_to_remove:
            # Only remove if usage count is below threshold
            if entry.usage_count < DictionaryService.MIN_USAGE_COUNT:
                db.delete(entry)
        
        db.commit()
        
        logger.info(f"Cleaned up {removed_count} entries from dictionary {dictionary_id}")
        
        return removed_count
    
    @staticmethod
    def get_series_id_from_name(db: Session, series_name: str) -> Optional[int]:
        """
        Get series ID from series name
        
        Args:
            db: Database session
            series_name: Series name
            
        Returns:
            Series ID if found, None otherwise
        """
        series = db.query(Series).filter(
            Series.title.ilike(f"%{series_name}%")
        ).first()
        
        return series.id if series else None

