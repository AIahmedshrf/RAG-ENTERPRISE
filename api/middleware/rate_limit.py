"""
Rate Limiting Middleware
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict
import time
from collections import defaultdict
import asyncio

from core.config import settings
from utilities.logger import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm"""
    
    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
        asyncio.create_task(self.cleanup_old_requests())
    
    async def dispatch(self, request: Request, call_next):
        if not settings.rate_limit.enabled:
            return await call_next(request)
        
        if request.url.path in ['/health', '/api/v1/health']:
            return await call_next(request)
        
        client_id = self.get_client_id(request)
        
        async with self.lock:
            now = time.time()
            
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if now - req_time < 3600
            ]
            
            minute_ago = now - 60
            hour_ago = now - 3600
            
            requests_last_minute = sum(
                1 for req_time in self.requests[client_id]
                if req_time > minute_ago
            )
            
            requests_last_hour = len(self.requests[client_id])
            
            if requests_last_minute >= settings.rate_limit.requests_per_minute:
                logger.warning(
                    f"Rate limit exceeded for {client_id}: "
                    f"{requests_last_minute} requests in last minute"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit": settings.rate_limit.requests_per_minute,
                        "window": "1 minute",
                        "retry_after": 60
                    }
                )
            
            if requests_last_hour >= settings.rate_limit.requests_per_hour:
                logger.warning(
                    f"Rate limit exceeded for {client_id}: "
                    f"{requests_last_hour} requests in last hour"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit": settings.rate_limit.requests_per_hour,
                        "window": "1 hour",
                        "retry_after": 3600
                    }
                )
            
            self.requests[client_id].append(now)
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit-Minute"] = str(settings.rate_limit.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            settings.rate_limit.requests_per_minute - requests_last_minute
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(settings.rate_limit.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            settings.rate_limit.requests_per_hour - requests_last_hour
        )
        
        return response
    
    def get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                from api.middleware.auth import AuthMiddleware
                token = auth_header.split(' ')[1]
                payload = AuthMiddleware.decode_token(token)
                user_id = payload.get('sub')
                if user_id:
                    return f"user:{user_id}"
            except:
                pass
        
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        
        return f"ip:{request.client.host}"
    
    async def cleanup_old_requests(self):
        """Periodically cleanup old request records"""
        while True:
            await asyncio.sleep(300)
            
            async with self.lock:
                now = time.time()
                hour_ago = now - 3600
                
                clients_to_remove = []
                for client_id, requests in self.requests.items():
                    self.requests[client_id] = [
                        req_time for req_time in requests
                        if req_time > hour_ago
                    ]
                    
                    if not self.requests[client_id]:
                        clients_to_remove.append(client_id)
                
                for client_id in clients_to_remove:
                    del self.requests[client_id]
                
                logger.debug(f"Rate limit cleanup: {len(clients_to_remove)} clients removed")
