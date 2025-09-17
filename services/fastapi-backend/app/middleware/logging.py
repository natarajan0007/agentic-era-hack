"""
Logging middleware for request/response tracking.
Provides detailed logging for API requests and responses.
"""

import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Configure logger
logger = logging.getLogger("api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request and response details.
    
    Logs:
    - Request method, path, headers
    - Response status, processing time
    - Request/response correlation ID
    - User ID (if authenticated)
    """
    
    def __init__(self, app: ASGIApp, log_level: int = logging.INFO):
        super().__init__(app)
        self.log_level = log_level
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.time()
        
        # Log request details
        await self._log_request(request)
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Log response details
            self._log_response(request, response, process_time)
            
            return response
            
        except Exception as e:
            # Log exception
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"- Error: {str(e)} - Time: {process_time:.4f}s - ID: {request_id}"
            )
            raise
    
    async def _log_request(self, request: Request) -> None:
        """Log incoming request details."""
        # Extract user ID if available
        user_id = "anonymous"
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.id
        
        # Get client IP
        client_host = request.client.host if request.client else "unknown"
        
        # Log request
        logger.log(
            self.log_level,
            f"Request: {request.method} {request.url.path} "
            f"- Client: {client_host} - User: {user_id} "
            f"- ID: {request.state.request_id}"
        )
        
        # Log request headers at debug level
        if logger.isEnabledFor(logging.DEBUG):
            headers = dict(request.headers.items())
            # Remove sensitive headers
            if "authorization" in headers:
                headers["authorization"] = "[REDACTED]"
            if "cookie" in headers:
                headers["cookie"] = "[REDACTED]"
                
            logger.debug(f"Request headers: {headers} - ID: {request.state.request_id}")
    
    def _log_response(self, request: Request, response: Response, process_time: float) -> None:
        """Log response details."""
        logger.log(
            self.log_level,
            f"Response: {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time:.4f}s "
            f"- ID: {request.state.request_id}"
        )
        
        # Log response headers at debug level
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Response headers: {dict(response.headers.items())} "
                f"- ID: {request.state.request_id}"
            )
