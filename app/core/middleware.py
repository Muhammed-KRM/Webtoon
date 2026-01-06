"""
Custom Middleware
"""
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from loguru import logger
from app.core.config import settings


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to all requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Add to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses to database"""
    
    async def dispatch(self, request: Request, call_next):
        # Start time
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Get user info if authenticated
        user_id = None
        if hasattr(request.state, "user"):
            user_id = request.state.user.id
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request to database
        from app.services.db_logger import DatabaseLogger
        DatabaseLogger.info(
            message=f"{request.method} {request.url.path}",
            module="LoggingMiddleware",
            request_id=request_id,
            user_id=user_id,
            ip_address=client_ip,
            user_agent=user_agent,
            extra_data={"method": request.method, "path": request.url.path}
        )
        
        # Also log to console
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Client: {client_ip}"
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error to database
            process_time = time.time() - start_time
            DatabaseLogger.error(
                message=f"ERROR {request.method} {request.url.path}: {str(e)}",
                module="LoggingMiddleware",
                request_id=request_id,
                user_id=user_id,
                ip_address=client_ip,
                user_agent=user_agent,
                extra_data={"error": str(e), "process_time": process_time}
            )
            
            # Also log to console
            logger.error(
                f"[{request_id}] ERROR {request.method} {request.url.path} - "
                f"{str(e)} - {process_time:.3f}s"
            )
            raise
        
        # Calculate process time
        process_time = time.time() - start_time
        
        # Log response to database (only errors and slow requests)
        if response.status_code >= 400 or process_time > 1.0:
            DatabaseLogger.warning(
                message=f"{request.method} {request.url.path} - Status: {response.status_code} - {process_time:.3f}s",
                module="LoggingMiddleware",
                request_id=request_id,
                user_id=user_id,
                ip_address=client_ip,
                user_agent=user_agent,
                extra_data={"status_code": response.status_code, "process_time": process_time}
            )
        
        # Log to console
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Status: {response.status_code} - {process_time:.3f}s"
        )
        
        # Add process time to headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Remove server header (security)
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class CORSHeadersMiddleware(BaseHTTPMiddleware):
    """Enhanced CORS handling"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add CORS headers if not already present
        origin = request.headers.get("origin")
        if origin and origin in settings.ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response

