"""
Rate Limiting Middleware
"""

from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List


class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[datetime]] = defaultdict(list)
    
    async def check(self, request: Request):
        """التحقق من معدل الطلبات"""
        client_ip = request.client.host
        now = datetime.now()
        
        # تنظيف الطلبات القديمة
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # التحقق من الحد
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        # إضافة الطلب الحالي
        self.requests[client_ip].append(now)


rate_limiter = RateLimiter(requests_per_minute=100)
