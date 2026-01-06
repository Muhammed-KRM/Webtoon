"""
Translation Job Model
"""
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.core.enums import JobStatus, TranslationMode


class TranslationJob(Base):
    __tablename__ = "translation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)  # Celery Task ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default=JobStatus.PENDING)  # PENDING, PROCESSING, COMPLETED, FAILED
    chapter_url = Column(Text, nullable=False)
    target_lang = Column(String, default="tr")
    mode = Column(String, default=TranslationMode.CLEAN)  # clean, overlay
    result_data = Column(JSON, nullable=True)  # İşlenmiş resim URL'leri veya base64
    error_message = Column(Text, nullable=True)
    progress = Column(Integer, default=0)  # 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

