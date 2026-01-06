"""
Notification Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.models.reading import Notification
from app.core.cache_invalidation import CacheInvalidation

router = APIRouter()


@router.get("/notifications", response_model=BaseResponse[list])
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user notifications"""
    try:
        query = db.query(Notification).filter(
            Notification.user_id == current_user.id
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
        
        notification_list = []
        for n in notifications:
            notification_list.append({
                "id": n.id,
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "link": n.link,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None
            })
        
        return BaseResponse.success_response(
            notification_list,
            f"Found {len(notification_list)} notifications"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting notifications: {str(e)}"
        )


@router.put("/notifications/{notification_id}/read", response_model=BaseResponse[dict])
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark notification as read"""
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        notification.is_read = True
        db.commit()
        
        return BaseResponse.success_response(
            {"notification_id": notification_id},
            "Notification marked as read"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking notification as read: {str(e)}"
        )


@router.put("/notifications/read-all", response_model=BaseResponse[dict])
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark all notifications as read"""
    try:
        db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).update({"is_read": True})
        db.commit()
        
        return BaseResponse.success_response(
            {"message": "All notifications marked as read"},
            "All notifications marked as read"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking all notifications as read: {str(e)}"
        )


@router.get("/notifications/unread-count", response_model=BaseResponse[dict])
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get unread notification count"""
    try:
        count = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).count()
        
        return BaseResponse.success_response(
            {"unread_count": count},
            "Unread count retrieved"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting unread count: {str(e)}"
        )

