"""
Response Compression Middleware
"""
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
import gzip
from typing import Callable


class CompressionMiddleware(BaseHTTPMiddleware):
    """Gzip compression for responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Check if client accepts gzip
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding:
            return response
        
        # Only compress if response is large enough (>1KB) and is JSON/text
        content_type = response.headers.get("Content-Type", "")
        if not any(ct in content_type for ct in ["application/json", "text/", "application/javascript"]):
            return response
        
        # Get response body
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # Only compress if body is large enough
        if len(response_body) < 1024:
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        # Compress
        compressed_body = gzip.compress(response_body, compresslevel=6)
        
        # Update headers
        headers = dict(response.headers)
        headers["Content-Encoding"] = "gzip"
        headers["Content-Length"] = str(len(compressed_body))
        headers["Vary"] = "Accept-Encoding"
        
        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )

