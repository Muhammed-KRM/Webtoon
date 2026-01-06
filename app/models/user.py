"""
User Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.db.base import Base
from app.core.enums import UserRole, Theme


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default=UserRole.USER)  # admin, user, guest, premium
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    preferred_language = Column(String, default="tr")
    preferred_theme = Column(String, default=Theme.AUTO)  # light, dark, auto
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

