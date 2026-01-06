"""
API v1 Router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, translate, jobs, files, admin, metrics, users,
    series, comments, subscription, site_settings,
    reading, notifications, payments, public, reactions, logs, cache
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(translate.router, prefix="/translate", tags=["Translation"])
api_router.include_router(jobs.router, prefix="/translate", tags=["Jobs"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(metrics.router, prefix="", tags=["Metrics"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(series.router, prefix="", tags=["Series"])
api_router.include_router(comments.router, prefix="", tags=["Comments"])
api_router.include_router(subscription.router, prefix="", tags=["Subscription"])
api_router.include_router(site_settings.router, prefix="", tags=["Site Settings"])
api_router.include_router(reading.router, prefix="", tags=["Reading"])
api_router.include_router(notifications.router, prefix="", tags=["Notifications"])
api_router.include_router(payments.router, prefix="", tags=["Payments"])
api_router.include_router(public.router, prefix="", tags=["Public"])
api_router.include_router(reactions.router, prefix="", tags=["Reactions"])
api_router.include_router(logs.router, prefix="/admin", tags=["Logs"])
api_router.include_router(cache.router, prefix="", tags=["Cache"])

