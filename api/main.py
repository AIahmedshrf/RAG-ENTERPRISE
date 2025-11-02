"""
Enhanced FastAPI Main Application
RAG-ENTERPRISE v1.0
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

# Configuration
from core.config import settings

# Database
from api.database import init_db, create_default_data, check_db_connection, get_db_health

# Middleware
from api.middleware import (
    RateLimitMiddleware,
    LoggingMiddleware,
)

# Routes
from api.routes import (
    auth_router,
    documents_router,
    datasets_router,
    chat_router,
    conversations_router,
    financial_router,
    tools_router,
    analytics_router,
    admin_router,
    health_router
)

# Logging
from utilities.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    logger.info("🚀 Starting RAG-ENTERPRISE API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize database
    try:
        logger.info("Initializing database...")
        init_db()
        
        # Create default data if needed
        create_default_data()
        
        # Check connection
        if check_db_connection():
            logger.info("✅ Database initialized successfully")
        else:
            logger.error("❌ Database connection failed")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down RAG-ENTERPRISE API")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise RAG System with Multi-Agent Support",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-RateLimit-*"]
)


# Custom Middleware
app.add_middleware(LoggingMiddleware)

if settings.rate_limit.enabled:
    app.add_middleware(RateLimitMiddleware)
    logger.info("✅ Rate limiting enabled")


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "detail": "Request validation failed",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "detail": "An unexpected error occurred",
            "path": str(request.url.path)
        }
    )


# Include Routers
app.include_router(health_router, tags=["Health"])
app.include_router(auth_router, prefix=settings.api_prefix, tags=["Authentication"])
app.include_router(datasets_router, prefix=settings.api_prefix, tags=["Datasets"])
app.include_router(documents_router, prefix=settings.api_prefix, tags=["Documents"])
app.include_router(conversations_router, prefix=settings.api_prefix, tags=["Conversations"])
app.include_router(chat_router, prefix=settings.api_prefix, tags=["Chat"])
app.include_router(financial_router, prefix=settings.api_prefix, tags=["Financial"])
app.include_router(tools_router, prefix=settings.api_prefix, tags=["Tools"])
app.include_router(analytics_router, prefix=settings.api_prefix, tags=["Analytics"])
app.include_router(admin_router, prefix=settings.api_prefix, tags=["Admin"])


# Root Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


@app.get("/info")
async def system_info():
    """System information endpoint"""
    return {
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment
        },
        "features": {
            "multi_tenancy": True,
            "rbac": True,
            "rate_limiting": settings.rate_limit.enabled,
            "metrics": settings.enable_metrics,
            "tracing": settings.enable_tracing
        },
        "ai": {
            "provider": "Azure OpenAI",
            "embedding_model": settings.azure_openai.embedding_deployment
        },
        "storage": {
            "provider": settings.storage.provider,
            "max_file_size_mb": settings.storage.max_file_size_mb
        },
        "rag": {
            "chunk_size": settings.rag.chunk_size,
            "chunk_overlap": settings.rag.chunk_overlap,
            "top_k": settings.rag.top_k,
            "use_reranking": settings.rag.use_reranking
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )


# === Admin Routes (Adapted from Dify) ===
app.include_router(
    admin_router,
    prefix=f"{settings.api_prefix}/admin",
    tags=["Admin - Dify Adapted"]
)

# === WebSocket Routes ===
from api.routes.websocket import router as websocket_router
app.include_router(websocket_router, tags=["WebSocket"])
