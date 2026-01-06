"""
Log Model - Database logging
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class Log(Base):
    """Application log model"""
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False, index=True)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    module = Column(String, nullable=True)  # Module/function name
    request_id = Column(String, nullable=True, index=True)  # Request ID from middleware
    user_id = Column(Integer, nullable=True, index=True)  # User ID if authenticated
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Additional context data
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Index for common queries
    __table_args__ = (
        {"sqlite_autoincrement": True} if hasattr(Base, 'metadata') else {}
    )

