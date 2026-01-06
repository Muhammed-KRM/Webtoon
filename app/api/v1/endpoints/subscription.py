"""
Subscription Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_admin
from app.schemas.subscription import SubscriptionResponse, PaymentRequest, PaymentResponse
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.models.subscription import Subscription, Payment
from app.core.cache_invalidation import CacheInvalidation
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/subscription", response_model=BaseResponse[SubscriptionResponse])
def get_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        # Create free subscription
        subscription = Subscription(
            user_id=current_user.id,
            plan_type="free",
            monthly_chapter_limit=0,
            used_chapters_this_month=0
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    
    return BaseResponse.success_response(
        SubscriptionResponse.model_validate(subscription),
        "Subscription retrieved"
    )


@router.post("/subscription/upgrade", response_model=BaseResponse[SubscriptionResponse])
def upgrade_subscription(
    plan_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upgrade subscription (Admin only for now)"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            subscription = Subscription(user_id=current_user.id)
            db.add(subscription)
        
        # Set plan limits
        if plan_type == "premium":
            subscription.plan_type = "premium"
            subscription.monthly_chapter_limit = 50  # 50 free chapters per month
            subscription.price_per_extra_chapter = 0.50
        elif plan_type == "basic":
            subscription.plan_type = "basic"
            subscription.monthly_chapter_limit = 10
            subscription.price_per_extra_chapter = 1.00
        else:
            subscription.plan_type = "free"
            subscription.monthly_chapter_limit = 0
        
        subscription.is_active = True
        subscription.started_at = datetime.utcnow()
        subscription.expires_at = datetime.utcnow() + timedelta(days=30)
        
        db.commit()
        db.refresh(subscription)
        
        # Update user role
        if plan_type == "premium":
            current_user.is_premium = True
            current_user.role = "premium"
        db.commit()
        
        # Invalidate user cache (subscription changed)
        CacheInvalidation.invalidate_user_cache(current_user.id)
        
        return BaseResponse.success_response(
            SubscriptionResponse.model_validate(subscription),
            "Subscription upgraded successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error upgrading subscription: {str(e)}"
        )


@router.post("/subscription/payment", response_model=BaseResponse[PaymentResponse])
def create_payment(
    payment_data: PaymentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create payment for extra chapters"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.is_active == True
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        # Calculate amount
        amount = float(subscription.price_per_extra_chapter) * payment_data.chapter_count
        
        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            subscription_id=subscription.id,
            amount=amount,
            chapter_count=payment_data.chapter_count,
            payment_method=payment_data.payment_method,
            status="pending"
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # TODO: Integrate with payment gateway (Stripe, PayPal, etc.)
        # For now, mark as completed
        payment.status = "completed"
        payment.transaction_id = f"TXN-{payment.id}-{datetime.utcnow().timestamp()}"
        
        # Add chapters to subscription
        subscription.used_chapters_this_month = max(0, subscription.used_chapters_this_month - payment_data.chapter_count)
        
        db.commit()
        
        # Invalidate user cache (subscription changed)
        CacheInvalidation.invalidate_user_cache(current_user.id)
        
        return BaseResponse.success_response(
            PaymentResponse.model_validate(payment),
            "Payment created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating payment: {str(e)}"
        )

