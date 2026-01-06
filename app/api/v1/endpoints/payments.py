"""
Payment Endpoints - Stripe Integration
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.subscription import PaymentRequest, PaymentResponse
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.models.subscription import Subscription, Payment
from app.services.payment_service import PaymentService
from loguru import logger
from datetime import datetime

router = APIRouter()


@router.post("/payments/create-intent", response_model=BaseResponse[dict])
def create_payment_intent(
    payment_data: PaymentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create Stripe payment intent for extra chapters"""
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
        
        # Create payment intent
        payment_intent = PaymentService.create_payment_intent(
            amount=amount,
            currency="usd",
            metadata={
                "user_id": str(current_user.id),
                "subscription_id": str(subscription.id),
                "chapter_count": str(payment_data.chapter_count)
            }
        )
        
        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            subscription_id=subscription.id,
            amount=amount,
            chapter_count=payment_data.chapter_count,
            payment_method=payment_data.payment_method,
            status="pending",
            transaction_id=payment_intent.get("payment_intent_id")
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        return BaseResponse.success_response(
            {
                "payment_id": payment.id,
                "client_secret": payment_intent.get("client_secret"),
                "payment_intent_id": payment_intent.get("payment_intent_id"),
                "amount": amount,
                "chapter_count": payment_data.chapter_count
            },
            "Payment intent created"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating payment intent: {str(e)}"
        )


@router.post("/payments/confirm", response_model=BaseResponse[PaymentResponse])
def confirm_payment(
    payment_intent_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Confirm payment and update subscription"""
    try:
        # Confirm payment with Stripe
        payment_result = PaymentService.confirm_payment(payment_intent_id)
        
        if payment_result.get("status") != "succeeded":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment not succeeded: {payment_result.get('status')}"
            )
        
        # Find payment record
        payment = db.query(Payment).filter(
            Payment.transaction_id == payment_intent_id,
            Payment.user_id == current_user.id
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment record not found"
            )
        
        # Update payment status
        payment.status = "completed"
        db.commit()
        
        # Update subscription (add chapters)
        subscription = db.query(Subscription).filter(
            Subscription.id == payment.subscription_id
        ).first()
        
        if subscription:
            # Reduce used chapters (add to available)
            subscription.used_chapters_this_month = max(
                0,
                subscription.used_chapters_this_month - payment.chapter_count
            )
            db.commit()
        
        return BaseResponse.success_response(
            PaymentResponse.model_validate(payment),
            "Payment confirmed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error confirming payment: {str(e)}"
        )


@router.post("/payments/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """Handle Stripe webhook events"""
    try:
        body = await request.body()
        
        # Handle webhook
        event = PaymentService.handle_webhook(body, stripe_signature)
        
        if event.get("event_type") == "payment_intent.succeeded":
            # Update payment status in database
            from app.core.database import SessionLocal
            db = SessionLocal()
            try:
                payment = db.query(Payment).filter(
                    Payment.transaction_id == event.get("payment_intent_id")
                ).first()
                
                if payment:
                    payment.status = "completed"
                    db.commit()
                    
                    # Update subscription
                    subscription = db.query(Subscription).filter(
                        Subscription.id == payment.subscription_id
                    ).first()
                    if subscription:
                        subscription.used_chapters_this_month = max(
                            0,
                            subscription.used_chapters_this_month - payment.chapter_count
                        )
                        db.commit()
            finally:
                db.close()
        
        return {"received": True, "event": event.get("event_type")}
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook error: {str(e)}"
        )

