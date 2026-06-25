"""
Error Handling and Logging Middleware for FastAPI

Provides:
- Global exception handling
- Structured logging middleware
- Request ID tracking
- Error response formatting
"""
import logging
import sys
import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from functools import wraps

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError as PydanticValidationError

logger = logging.getLogger(__name__)


class ErrorCode:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    SERVER_ERROR = "SERVER_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    CONFLICT = "CONFLICT"


class APIException(Exception):
    """Base API Exception with structured error information."""
    
    def __init__(
        self,
        message: str,
        code: str = ErrorCode.SERVER_ERROR,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(APIException):
    """Validation error for invalid input data."""
    
    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details
        )


class NotFoundError(APIException):
    """Resource not found error."""
    
    def __init__(self, message: str = "Resource not found", resource: Optional[str] = None):
        details = {"resource": resource} if resource else {}
        super().__init__(
            message=message,
            code=ErrorCode.NOT_FOUND,
            status_code=404,
            details=details
        )


class AuthenticationError(APIException):
    """Authentication required error."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            code=ErrorCode.AUTHENTICATION_ERROR,
            status_code=401
        )


class AuthorizationError(APIException):
    """Authorization denied error."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            code=ErrorCode.AUTHORIZATION_ERROR,
            status_code=403
        )


class ConflictError(APIException):
    """Resource conflict error (e.g., duplicate)."""
    
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.CONFLICT,
            status_code=409,
            details=details
        )


class RateLimitError(APIException):
    """Rate limit exceeded error."""
    
    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(
            message=message,
            code=ErrorCode.RATE_LIMIT_ERROR,
            status_code=429
        )


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str
    code: str
    status_code: int
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    timestamp: str


from starlette.types import ASGIApp, Receive, Scope, Send


class RequestLoggingMiddleware:
    """
    ASGI middleware for logging all requests and responses.

    Implemented as native ASGI middleware (not BaseHTTPMiddleware)
    so that WebSocket upgrade requests are properly forwarded.

    Logs:
    - Request method, path, query params
    - Response status code and duration
    - Request ID for traceability
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        request_id = None
        start_time = time.time()

        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            request_id = (
                headers.get(b"x-request-id", b"").decode()
                or str(uuid.uuid4())
            )
            method = scope.get("method", "")
            path = scope.get("path", "")
            query = scope.get("query_string", b"").decode()

            logger.info(
                f"Request started: {method} {path}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "query": query,
                },
            )

            async def send_with_logging(message):
                if message["type"] == "http.response.start":
                    duration_ms = (time.time() - start_time) * 1000
                    status_code = message.get("status", 0)
                    logger.info(
                        f"Request completed: {method} {path} -> {status_code} ({duration_ms:.2f}ms)",
                        extra={
                            "request_id": request_id,
                            "method": method,
                            "path": path,
                            "status_code": status_code,
                            "duration_ms": duration_ms,
                        },
                    )

                if request_id and message["type"] == "http.response_start":
                    headers = list(message.get("headers", []))
                    headers.append((b"x-request-id", request_id.encode()))
                    duration_ms = (time.time() - start_time) * 1000
                    headers.append(
                        (b"x-response-time", f"{duration_ms:.2f}ms".encode())
                    )
                    message["headers"] = headers

                await send(message)

            await self.app(scope, receive, send_with_logging)
        else:
            path = scope.get("path", "")
            logger.info(f"WebSocket connection: {path}")
            await self.app(scope, receive, send)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle APIException and return structured error response."""
    request_id = request.headers.get("X-Request-ID")
    
    logger.warning(
        f"API Exception: {exc.code} - {exc.message}",
        extra={
            "request_id": request_id,
            "error_code": exc.code,
            "status_code": exc.status_code,
            "details": exc.details,
        }
    )
    
    error_response = ErrorResponse(
        error=exc.message,
        code=exc.code,
        status_code=exc.status_code,
        details=exc.details if exc.details else None,
        request_id=request_id,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
        headers={"X-Request-ID": request_id} if request_id else {}
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions and return generic error response."""
    request_id = request.headers.get("X-Request-ID")
    
    logger.error(
        f"Unexpected error: {type(exc).__name__}: {str(exc)}",
        extra={
            "request_id": request_id,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        },
        exc_info=True
    )
    
    error_response = ErrorResponse(
        error="An unexpected error occurred. Please try again later.",
        code=ErrorCode.SERVER_ERROR,
        status_code=500,
        request_id=request_id,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(),
        headers={"X-Request-ID": request_id} if request_id else {}
    )


async def validation_exception_handler(request: Request, exc: PydanticValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    request_id = request.headers.get("X-Request-ID")
    
    errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors[field] = error["msg"]
    
    logger.warning(
        f"Validation error: {errors}",
        extra={
            "request_id": request_id,
            "validation_errors": errors,
        }
    )
    
    error_response = ErrorResponse(
        error="Validation error",
        code=ErrorCode.VALIDATION_ERROR,
        status_code=422,
        details={"fields": errors},
        request_id=request_id,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump(),
        headers={"X-Request-ID": request_id} if request_id else {}
    )


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    include_timestamp: bool = True
) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_string: Custom log format string
        include_timestamp: Whether to include timestamp in logs
    """
    if format_string is None:
        if include_timestamp:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:
            format_string = "%(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
    )
    
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def log_function_call(func: Callable) -> Callable:
    """Decorator to log function calls with arguments and results."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__qualname__
        logger.debug(f"Calling {func_name}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func_name} failed: {type(e).__name__}: {str(e)}")
            raise
    
    return wrapper


def log_async_function_call(func: Callable) -> Callable:
    """Decorator to log async function calls with arguments and results."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        func_name = func.__qualname__
        logger.debug(f"Calling {func_name}")
        
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"{func_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func_name} failed: {type(e).__name__}: {str(e)}")
            raise
    
    return wrapper


class ContextLogger:
    """Context manager for logging operations with context."""
    
    def __init__(self, operation: str, **context):
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Starting {self.operation}", extra=self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000 if self.start_time else 0
        
        if exc_type:
            logger.error(
                f"Failed {self.operation}: {exc_type.__name__}: {exc_val}",
                extra={**self.context, "duration_ms": duration_ms},
                exc_info=True
            )
        else:
            logger.info(
                f"Completed {self.operation}",
                extra={**self.context, "duration_ms": duration_ms}
            )
        
        return False
    
    async def __aenter__(self):
        self.start_time = time.time()
        logger.info(f"Starting {self.operation}", extra=self.context)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000 if self.start_time else 0
        
        if exc_type:
            logger.error(
                f"Failed {self.operation}: {exc_type.__name__}: {exc_val}",
                extra={**self.context, "duration_ms": duration_ms},
                exc_info=True
            )
        else:
            logger.info(
                f"Completed {self.operation}",
                extra={**self.context, "duration_ms": duration_ms}
            )
        
        return False
