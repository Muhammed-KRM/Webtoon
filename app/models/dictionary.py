"""
Series Dictionary Model - Special names glossary for translation consistency
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.core.enums import ProperNounType


class SeriesDictionary(Base):
    """Dictionary for a series - stores special names and their translations"""
    __tablename__ = "series_dictionaries"
    
    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=False, index=True)
    source_lang = Column(String, nullable=False)  # en, ko, ja
    target_lang = Column(String, nullable=False)  # tr, en, es
    max_entries = Column(Integer, default=1000)  # Maximum entries before cleanup
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    entries = relationship("DictionaryEntry", back_populates="dictionary", cascade="all, delete-orphan")
    
    # Unique constraint: one dictionary per series per language pair
    __table_args__ = (
        Index('ix_series_dict_lang_pair', 'series_id', 'source_lang', 'target_lang', unique=True),
    )


class DictionaryEntry(Base):
    """Individual dictionary entry - special name and its translation"""
    __tablename__ = "dictionary_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    dictionary_id = Column(Integer, ForeignKey("series_dictionaries.id"), nullable=False, index=True)
    original_name = Column(String, nullable=False)  # Original name in source language
    translated_name = Column(String, nullable=False)  # Translated name in target language
    usage_count = Column(Integer, default=1)  # How many times this name was used
    is_proper_noun = Column(String, default=ProperNounType.AUTO)  # auto, yes, no - detected or manual
    last_used_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dictionary = relationship("SeriesDictionary", back_populates="entries")
    
    # Indexes for fast lookup
    __table_args__ = (
        Index('ix_dict_entry_original', 'dictionary_id', 'original_name'),
        Index('ix_dict_entry_usage', 'dictionary_id', 'usage_count'),
        Index('ix_dict_entry_last_used', 'dictionary_id', 'last_used_at'),
    )

