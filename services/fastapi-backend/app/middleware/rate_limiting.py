"""
Rate limiting middleware for API protection.
Implements configurable rate limiting based on client IP or user ID.
"""

import time
from typing import Dict, Tuple, Callable, Optional, Union
from fastapi import Request, Response, HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.config import settings
from app.api.dependencies import get_current_user
from app.models.user import User


class RateLimiter:
    """
    Rate limiter implementation using sliding window algorithm.
    Tracks request counts within a time window for each client.
    """
    
    def __init__(self, window_size: int = 60, max_requests: int = 100):
        """
        Initialize rate limiter.
        
        Args:
            window_size: Time window in seconds
            max_requests: Maximum requests allowed in the window
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.clients: Dict[str, Dict[float, int]] = {}
    
    def is_rate_limited(self, client_id: str) -> Tuple[bool, int, int]:
        """
        Check if client is rate limited.
        
        Args:
            client_id: Unique identifier for the client (IP or user ID)
            
        Returns:
            Tuple of (is_limited, requests_remaining, retry_after)
        """
        current_time = time.time()
        
        # Initialize client if not exists
        if client_id not in self.clients:
            self.clients[client_id] = {}
        
        # Clean up old timestamps
        self._cleanup_old_timestamps(client_id, current_time)
        
        # Count requests in current window
        request_count = sum(self.clients[client_id].values())
        
        # Check if rate limited
        if request_count >= self.max_requests:
            # Calculate retry after time
            oldest_timestamp = min(self.clients[client_id].keys()) if self.clients[client_id] else current_time
            retry_after = int(self.window_size - (current_time - oldest_timestamp))
            return True, 0, max(1, retry_after)
        
        # Record this request
        self.clients[client_id][current_time] = self.clients[client_id].get(current_time, 0) + 1
        
        # Return not limited with remaining requests
        return False, self.max_requests - request_count - 1, 0
    
    def _cleanup_old_timestamps(self, client_id: str, current_time: float) -> None:
        """Remove timestamps outside the current window."""
        cutoff_time = current_time - self.window_size
        self.clients[client_id] = {
            ts: count for ts, count in self.clients[client_id].items()
            if ts > cutoff_time
        }


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API rate limiting.
    
    Features:
    - Different rate limits for authenticated vs anonymous users
    - Path-based rate limit configuration
    - Bypass for internal requests
    - Headers for rate limit information
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        anonymous_rate_limit: int = 60,
        authenticated_rate_limit: int = 300,
        window_size: int = 60,
        exclude_paths: list = None
    ):
        """
        Initialize rate limiting middleware.
        
        Args:
            app: ASGI application
            anonymous_rate_limit: Max requests per window for anonymous users
            authenticated_rate_limit: Max requests per window for authenticated users
            window_size: Time window in seconds
            exclude_paths: List of paths to exclude from rate limiting
        """
        super().__init__(app)
        self.anonymous_limiter = RateLimiter(window_size, anonymous_rate_limit)
        self.authenticated_limiter = RateLimiter(window_size, authenticated_rate_limit)
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/health"]
        self.window_size = window_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Determine client identifier
        client_id = self._get_client_identifier(request)
        
        # Check if authenticated
        is_authenticated = hasattr(request.state, "user") and request.state.user is not None
        
        # Apply appropriate rate limiter
        limiter = self.authenticated_limiter if is_authenticated else self.anonymous_limiter
        is_limited, remaining, retry_after = limiter.is_rate_limited(client_id)
        
        if is_limited:
            # Return rate limit exceeded response
            return self._create_rate_limit_response(remaining, retry_after)
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(
            self.authenticated_limiter.max_requests if is_authenticated 
            else self.anonymous_limiter.max_requests
        )
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.window_size))
        
        return response
    
    def _get_client_identifier(self, request: Request) -> str:
        """
        Get unique client identifier.
        Uses user ID if authenticated, otherwise IP address.
        """
        # Use user ID if available
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"
        
        # Fall back to IP address
        return f"ip:{request.client.host}" if request.client else "ip:unknown"
    
    def _create_rate_limit_response(self, remaining: int, retry_after: int) -> Response:
        """Create response for rate limited requests."""
        return Response(
            content={"detail": "Rate limit exceeded"},
            status_code=429,
            headers={
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(time.time() + retry_after)),
                "Retry-After": str(retry_after),
                "Content-Type": "application/json"
            }
        )


# Dependency for endpoint-specific rate limiting
class EndpointRateLimiter:
    """
    Rate limiter for specific endpoints.
    Can be used as a dependency in FastAPI route functions.
    """
    
    def __init__(
        self, 
        max_requests: int = 10, 
        window_size: int = 60,
        by_user: bool = True
    ):
        """
        Initialize endpoint rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in the window
            window_size: Time window in seconds
            by_user: Whether to limit by user ID (True) or IP (False)
        """
        self.limiter = RateLimiter(window_size, max_requests)
        self.by_user = by_user
    
    async def __call__(
        self, 
        request: Request, 
        user: Optional[User] = Depends(get_current_user)
    ) -> None:
        """
        Check rate limit for the current request.
        
        Args:
            request: FastAPI request object
            user: Current user (from dependency)
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        # Determine client identifier
        if self.by_user and user:
            client_id = f"endpoint:{request.url.path}:user:{user.id}"
        else:
            client_id = f"endpoint:{request.url.path}:ip:{request.client.host}"
        
        # Check rate limit
        is_limited, remaining, retry_after = self.limiter.is_rate_limited(client_id)
        
        if is_limited:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(int(time.time() + retry_after)),
                    "Retry-After": str(retry_after)
                }
            )
