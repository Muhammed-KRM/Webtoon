"""
Metrics Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_active_user
from app.core.metrics import metrics
from app.schemas.base_response import BaseResponse
from app.models.user import User

router = APIRouter()


@router.get("/metrics/summary", response_model=BaseResponse[dict])
def get_metrics_summary(
    current_user: User = Depends(get_current_active_user)
):
    """Get application metrics summary"""
    try:
        # API metrics
        api_requests = metrics.get_counter("api.requests")
        api_errors = metrics.get_counter("api.errors")
        
        # Translation metrics
        translations_started = metrics.get_counter("translation.started")
        translations_completed = metrics.get_counter("translation.completed")
        translations_failed = metrics.get_counter("translation.failed")
        
        # Timing metrics
        translation_timing = metrics.get_timing_stats("translation.duration")
        api_timing = metrics.get_timing_stats("api.duration")
        
        return BaseResponse.success_response(
            {
                "api": {
                    "requests": api_requests,
                    "errors": api_errors,
                    "timing": api_timing
                },
                "translation": {
                    "started": translations_started,
                    "completed": translations_completed,
                    "failed": translations_failed,
                    "timing": translation_timing
                }
            },
            "Metrics retrieved"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving metrics: {str(e)}"
        )

