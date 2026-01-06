"""
Subscription Model - Premium user subscriptions
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Subscription(Base):
    """User subscription model"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    plan_type = Column(String, nullable=False)  # premium, basic, free
    monthly_chapter_limit = Column(Integer, default=0)  # 0 = unlimited
    used_chapters_this_month = Column(Integer, default=0)
    price_per_extra_chapter = Column(Numeric(10, 2), default=0.50)  # Price in USD
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="subscription")


class Payment(Base):
    """Payment model for extra chapters"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="USD")
    chapter_count = Column(Integer, nullable=False)  # Number of chapters purchased
    status = Column(String, default="pending")  # pending, completed, failed
    payment_method = Column(String, nullable=True)  # stripe, paypal, etc.
    transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="payments")
    subscription = relationship("Subscription", backref="payments")

