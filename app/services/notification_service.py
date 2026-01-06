"""
Notification Service
"""
from sqlalchemy.orm import Session
from typing import Optional
from loguru import logger
from app.models.notification import Notification
from app.models.user import User


class NotificationService:
    """Service for managing user notifications"""
    
    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        link: Optional[str] = None
    ) -> Notification:
        """Create a new notification"""
        try:
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                link=link
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            logger.info(f"Notification created for user {user_id}: {title}")
            return notification
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def notify_translation_completed(
        db: Session,
        user_id: int,
        chapter_id: int,
        series_title: str,
        target_lang: str
    ):
        """Notify user that translation is completed"""
        NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.TRANSLATION_COMPLETED,
            title="Translation Completed",
            message=f"Translation of {series_title} to {target_lang} is ready!",
            link=f"/chapters/{chapter_id}"
        )
    
    @staticmethod
    def notify_new_chapter(
        db: Session,
        user_id: int,
        series_id: int,
        series_title: str,
        chapter_number: int
    ):
        """Notify user about new chapter"""
        NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.NEW_CHAPTER,
            title="New Chapter Available",
            message=f"Chapter {chapter_number} of {series_title} is now available!",
            link=f"/series/{series_id}/chapters/{chapter_number}"
        )
    
    @staticmethod
    def notify_comment_reply(
        db: Session,
        user_id: int,
        comment_id: int,
        commenter_username: str
    ):
        """Notify user about comment reply"""
        NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.COMMENT_REPLY,
            title="New Reply",
            message=f"{commenter_username} replied to your comment",
            link=f"/comments/{comment_id}"
        )

