"""
Notification background tasks
"""
from app.core.celery_app import celery_app

@celery_app.task(name="send_notification")
def send_notification_task(user_id: int, message: str):
    """Background task for sending notifications"""
    return {"status": "sent", "user_id": user_id}
