"""
Job History Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.base_response import BaseResponse
from app.models.user import User
from app.models.job import TranslationJob
from datetime import datetime

router = APIRouter()


@router.get("/jobs", response_model=BaseResponse[dict])
def get_job_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's translation job history"""
    try:
        # Build query
        query = db.query(TranslationJob).filter(
            TranslationJob.user_id == current_user.id
        )
        
        # Apply status filter
        if status_filter:
            query = query.filter(TranslationJob.status == status_filter.upper())
        
        # Get total count
        total = query.count()
        
        # Get jobs with pagination
        jobs = query.order_by(desc(TranslationJob.created_at)).offset(skip).limit(limit).all()
        
        # Format response
        job_list = []
        for job in jobs:
            job_list.append({
                "task_id": job.task_id,
                "chapter_url": job.chapter_url,
                "target_lang": job.target_lang,
                "mode": job.mode,
                "status": job.status,
                "progress": job.progress or 0,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error_message": job.error_message
            })
        
        return BaseResponse.success_response(
            {
                "jobs": job_list,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total
            },
            "Job history retrieved"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving job history: {str(e)}"
        )


@router.delete("/jobs/{task_id}", response_model=BaseResponse[dict])
def delete_job(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a translation job"""
    try:
        # Find job
        job = db.query(TranslationJob).filter(
            TranslationJob.task_id == task_id,
            TranslationJob.user_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Delete job
        db.delete(job)
        db.commit()
        
        return BaseResponse.success_response(
            {"task_id": task_id},
            "Job deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting job: {str(e)}"
        )

