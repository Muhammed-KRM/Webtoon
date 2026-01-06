"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router
from app.core.exceptions import (
    global_exception_handler,
    validation_exception_handler,
    database_exception_handler
)
from app.core.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    SecurityHeadersMiddleware
)
from app.core.compression import CompressionMiddleware
from app.core.metrics import metrics
import time

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    description="Webtoon AI Translator - Profesyonel makine çeviri platformu",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Custom Middleware (order matters!)
app.add_middleware(RequestIDMiddleware)  # First: Add request ID
# app.add_middleware(CompressionMiddleware)  # Disabled: Causes issues with Swagger UI
app.add_middleware(LoggingMiddleware)  # Third: Log requests
app.add_middleware(SecurityHeadersMiddleware)  # Fourth: Security headers

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Add exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Collect metrics for all requests"""
    start_time = time.time()
    
    # Increment request counter
    metrics.increment_counter("api.requests")
    
    try:
        response = await call_next(request)
        
        # Record timing
        duration = time.time() - start_time
        metrics.record_timing("api.duration", duration)
        
        # Increment error counter if error
        if response.status_code >= 400:
            metrics.increment_counter("api.errors")
        
        return response
    except Exception as e:
        # Record error
        metrics.increment_counter("api.errors")
        raise


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Webtoon AI Translator API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Detailed health check with actual connection tests"""
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "version": settings.APP_VERSION
    }
    
    # Test database connection
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Test Redis connection
    try:
        import redis
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        health_status["redis"] = "connected"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return health_status

