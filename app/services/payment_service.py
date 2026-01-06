"""
Payment Service - Stripe Integration
"""
import stripe
from typing import Optional, Dict
from loguru import logger
from app.core.config import settings

# Initialize Stripe (will be set from settings)
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)


class PaymentService:
    """Service for handling payments via Stripe"""
    
    @staticmethod
    def create_payment_intent(
        amount: float,
        currency: str = "usd",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create a Stripe payment intent
        
        Args:
            amount: Amount in dollars (will be converted to cents)
            currency: Currency code
            metadata: Additional metadata
            
        Returns:
            Payment intent object
        """
        try:
            if not stripe.api_key:
                logger.warning("Stripe API key not configured")
                return {
                    "error": "Payment service not configured",
                    "mock": True,
                    "payment_intent_id": f"mock_pi_{int(amount * 100)}"
                }
            
            # Convert dollars to cents
            amount_cents = int(amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    "enabled": True,
                }
            )
            
            logger.info(f"Payment intent created: {intent.id}")
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": amount,
                "currency": currency
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            raise Exception(f"Payment processing error: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            raise
    
    @staticmethod
    def confirm_payment(payment_intent_id: str) -> Dict:
        """Confirm a payment intent"""
        try:
            if not stripe.api_key:
                return {"status": "succeeded", "mock": True}
            
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == "succeeded":
                return {
                    "status": "succeeded",
                    "payment_intent_id": payment_intent_id,
                    "amount": intent.amount / 100,  # Convert cents to dollars
                    "currency": intent.currency
                }
            else:
                return {
                    "status": intent.status,
                    "payment_intent_id": payment_intent_id
                }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            raise Exception(f"Payment confirmation error: {str(e)}")
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
            raise
    
    @staticmethod
    def handle_webhook(payload: bytes, signature: str) -> Dict:
        """Handle Stripe webhook"""
        try:
            if not stripe.api_key:
                logger.warning("Stripe webhook received but API key not configured")
                return {"error": "Payment service not configured"}
            
            webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
            if not webhook_secret:
                logger.warning("Stripe webhook secret not configured")
                return {"error": "Webhook secret not configured"}
            
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            # Handle different event types
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                logger.info(f"Payment succeeded: {payment_intent['id']}")
                return {
                    "event_type": "payment_intent.succeeded",
                    "payment_intent_id": payment_intent['id'],
                    "amount": payment_intent['amount'] / 100
                }
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                logger.warning(f"Payment failed: {payment_intent['id']}")
                return {
                    "event_type": "payment_intent.payment_failed",
                    "payment_intent_id": payment_intent['id']
                }
            
            return {"event_type": event['type'], "handled": False}
            
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise Exception("Invalid webhook payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise Exception("Invalid webhook signature")
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            raise

