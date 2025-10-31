"""
Custom Exceptions for RAG-ENTERPRISE
"""
from fastapi import HTTPException, status
from typing import Optional, Any


class BaseAPIException(HTTPException):
    """Base exception for all API exceptions"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = "api_error",
        headers: Optional[dict] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class AuthenticationError(BaseAPIException):
    """Authentication failed"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="authentication_error"
        )


class AuthorizationError(BaseAPIException):
    """Authorization failed - insufficient permissions"""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="authorization_error"
        )


class NotFoundError(BaseAPIException):
    """Resource not found"""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="not_found"
        )


class ValidationError(BaseAPIException):
    """Validation error"""
    
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="validation_error"
        )


class ConflictError(BaseAPIException):
    """Resource conflict"""
    
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="conflict"
        )


class RateLimitError(BaseAPIException):
    """Rate limit exceeded"""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="rate_limit_exceeded"
        )


class DatabaseError(BaseAPIException):
    """Database operation failed"""
    
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="database_error"
        )


class ExternalServiceError(BaseAPIException):
    """External service error (Azure OpenAI, etc.)"""
    
    def __init__(self, detail: str = "External service error"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="external_service_error"
        )


class FileProcessingError(BaseAPIException):
    """File processing error"""
    
    def __init__(self, detail: str = "File processing failed"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="file_processing_error"
        )


class TenantError(BaseAPIException):
    """Tenant-related error"""
    
    def __init__(self, detail: str = "Tenant error"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="tenant_error"
        )
