# spms_db/backend/core/rate_limit.py
import time
import logging
from typing import Optional

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import aioredis

logger = logging.getLogger("spms_rate_limit")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limits per user (JWT) or API key.
    
    Uses Redis to track request counts and reset times.
    """
    def __init__(
        self,
        app,
        redis_url: str = "redis://localhost",
        max_requests: int = 100,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None

    async def dispatch(self, request: Request, call_next):
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)

        # Identify client: user_id from JWT or API key
        client_id = await self.get_client_identifier(request)
        if not client_id:
            # Treat as anonymous user
            client_id = f"anon:{request.client.host}"

        key = f"rate:{client_id}"
        count = await self.redis.get(key)
        if count is None:
            # First request in this window
            pipe = self.redis.pipeline()
            pipe.set(key, 1, ex=self.window_seconds)
            await pipe.execute()
            remaining = self.max_requests - 1
        else:
            count = int(count)
            if count >= self.max_requests:
                logger.warning(f"Rate limit exceeded for client: {client_id}")
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds} seconds."
                )
            else:
                await self.redis.incr(key)
                remaining = self.max_requests - (count + 1)

        response: Response = await call_next(request)
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

    async def get_client_identifier(self, request: Request) -> Optional[str]:
        """
        Determine the identifier for the rate limit.
        Priority:
        1. JWT user ID
        2. X-API-Key
        3. Anonymous IP
        """
        # Check API Key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"apikey:{api_key}"

        # Check JWT Bearer token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                from backend.auth.utils import decode_access_token
                payload = decode_access_token(token)
                user_id = payload.get("user_id")
                if user_id:
                    return f"user:{user_id}"
            except Exception:
                return None

        return None
