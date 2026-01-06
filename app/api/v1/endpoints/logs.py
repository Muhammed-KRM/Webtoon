"""
Log Endpoints - View application logs
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.models.log import Log

router = APIRouter()


@router.get("/logs", response_model=BaseResponse[list])
def get_logs(
    level: Optional[str] = Query(None, regex="^(INFO|WARNING|ERROR|DEBUG)$"),
    module: Optional[str] = None,
    request_id: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get application logs (Admin only)"""
    try:
        query = db.query(Log)
        
        # Filters
        if level:
            query = query.filter(Log.level == level)
        if module:
            query = query.filter(Log.module.ilike(f"%{module}%"))
        if request_id:
            query = query.filter(Log.request_id == request_id)
        if user_id:
            query = query.filter(Log.user_id == user_id)
        if start_date:
            query = query.filter(Log.created_at >= start_date)
        if end_date:
            query = query.filter(Log.created_at <= end_date)
        
        # Get total count
        total = query.count()
        
        # Get logs
        logs = query.order_by(desc(Log.created_at)).offset(skip).limit(limit).all()
        
        log_list = []
        for log in logs:
            log_list.append({
                "id": log.id,
                "level": log.level,
                "message": log.message,
                "module": log.module,
                "request_id": log.request_id,
                "user_id": log.user_id,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "extra_data": log.extra_data,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        
        return BaseResponse.success_response(
            {
                "logs": log_list,
                "total": total,
                "skip": skip,
                "limit": limit
            },
            f"Found {total} log entries"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting logs: {str(e)}"
        )


@router.get("/logs/stats", response_model=BaseResponse[dict])
def get_log_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get log statistics (Admin only)"""
    try:
        from sqlalchemy import func
        
        query = db.query(Log)
        
        if start_date:
            query = query.filter(Log.created_at >= start_date)
        if end_date:
            query = query.filter(Log.created_at <= end_date)
        
        # Count by level
        level_counts = db.query(
            Log.level,
            func.count(Log.id).label("count")
        ).group_by(Log.level).all()
        
        # Count by module
        module_counts = db.query(
            Log.module,
            func.count(Log.id).label("count")
        ).filter(Log.module.isnot(None)).group_by(Log.module).order_by(desc("count")).limit(10).all()
        
        # Error rate
        total = query.count()
        errors = query.filter(Log.level == "ERROR").count()
        error_rate = (errors / total * 100) if total > 0 else 0
        
        return BaseResponse.success_response(
            {
                "total": total,
                "by_level": {level: count for level, count in level_counts},
                "top_modules": {module: count for module, count in module_counts},
                "error_rate": round(error_rate, 2),
                "errors": errors
            },
            "Log statistics retrieved"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting log stats: {str(e)}"
        )

