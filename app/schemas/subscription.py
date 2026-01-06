"""
Subscription Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class SubscriptionResponse(BaseModel):
    """Subscription response schema"""
    id: int
    user_id: int
    plan_type: str
    monthly_chapter_limit: int
    used_chapters_this_month: int
    price_per_extra_chapter: Decimal
    is_active: bool
    started_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PaymentRequest(BaseModel):
    """Payment request schema"""
    chapter_count: int
    payment_method: str = "stripe"


class PaymentResponse(BaseModel):
    """Payment response schema"""
    id: int
    user_id: int
    amount: Decimal
    currency: str
    chapter_count: int
    status: str
    transaction_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

