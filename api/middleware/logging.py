"""
Logging Middleware
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json

from utilities.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/Response logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        request_info = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        
        logger.info(f"Request started: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            duration = time.time() - start_time
            
            response_info = {
                **request_info,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2)
            }
            
            if response.status_code >= 400:
                logger.warning(f"Request completed with error: {json.dumps(response_info)}")
            else:
                logger.info(f"Request completed: {json.dumps(response_info)}")
            
            response.headers["X-Process-Time"] = str(duration)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"after {round(duration * 1000, 2)}ms - {str(e)}"
            )
            raise
