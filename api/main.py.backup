"""
RAG-ENTERPRISE Main API Application
FastAPI application with all routes and middleware
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from core.config import settings
from api.database import init_db
from api.middleware.logging import LoggingMiddleware
from api.middleware.rate_limit import RateLimitMiddleware

# Import all routers
from api.routes import (
    health_router,
    auth_router,
    datasets_router,
    documents_router,
    conversations_router,
    chat_router,
    financial_router,
    tools_router,
    analytics_router,
    admin_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting RAG-ENTERPRISE API")
    logger.info(f"Environment: {getattr(settings, 'ENVIRONMENT', 'development')}")
    logger.info(f"Debug mode: {getattr(settings, 'DEBUG', True)}")
    
    try:
        logger.info("Initializing database...")
        init_db()
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down RAG-ENTERPRISE API")


# Create FastAPI app
app = FastAPI(
    title="RAG-ENTERPRISE API",
    description="Enterprise RAG Platform with Multi-Agent Support",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, 'ALLOWED_ORIGINS', ['*']),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Register routers
# Health check (no prefix)
app.include_router(health_router, tags=["Health"])

# Authentication routes
app.include_router(
    auth_router,
    prefix=f"{settings.api_prefix}/auth",
    tags=["Authentication"]
)

# Main API routes
app.include_router(
    datasets_router,
    prefix=settings.api_prefix,
    tags=["Datasets"]
)

app.include_router(
    documents_router,
    prefix=settings.api_prefix,
    tags=["Documents"]
)

app.include_router(
    conversations_router,
    prefix=settings.api_prefix,
    tags=["Conversations"]
)

app.include_router(
    chat_router,
    prefix=settings.api_prefix,
    tags=["Chat"]
)

app.include_router(
    financial_router,
    prefix=settings.api_prefix,
    tags=["Financial"]
)

app.include_router(
    tools_router,
    prefix=settings.api_prefix,
    tags=["Tools"]
)

app.include_router(
    analytics_router,
    prefix=settings.api_prefix,
    tags=["Analytics"]
)

# Admin routes
app.include_router(
    admin_router,
    prefix=f"{settings.api_prefix}/admin",
    tags=["Admin"]
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "RAG-ENTERPRISE API",
        "version": "2.1.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
