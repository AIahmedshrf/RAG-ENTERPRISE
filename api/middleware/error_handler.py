"""
Global Error Handler Middleware
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import traceback

from core.exceptions import BaseAPIException
from utilities.logger import get_logger

logger = get_logger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """Global error handler"""
    try:
        return await call_next(request)
    except Exception as exc:
        return handle_exception(exc, request)


def handle_exception(exc: Exception, request: Request) -> JSONResponse:
    """Handle different types of exceptions"""
    
    if isinstance(exc, BaseAPIException):
        logger.error(f"API Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "detail": exc.detail,
                "path": request.url.path
            }
        )
    
    if isinstance(exc, RequestValidationError):
        logger.error(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "detail": "Request validation failed",
                "errors": exc.errors()
            }
        )
    
    if isinstance(exc, SQLAlchemyError):
        logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "database_error",
                "detail": "A database error occurred",
                "path": request.url.path
            }
        )
    
    logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "detail": "An unexpected error occurred",
            "path": request.url.path
        }
    )
