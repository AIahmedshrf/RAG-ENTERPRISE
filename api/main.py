"""
RAG-ENTERPRISE API
Main FastAPI Application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import database initialization
from api.database import init_db, check_database_health

# Import all routers
from api.routes import (
    health,
    auth,
    admin,
    datasets,
    documents,
    chat,
    conversations,
    analytics,
    tools,
    knowledge,
    agents,
    financial,
    websocket
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app
    Handles startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting RAG-ENTERPRISE API...")
    
    # Initialize database
    logger.info("📊 Initializing database...")
    if init_db():
        logger.info("✅ Database initialized successfully")
    else:
        logger.warning("⚠️  Database initialization failed")
    
    # Check database health
    health_status = check_database_health()
    logger.info(f"💚 Database health: {health_status.get('status', 'unknown')}")
    
    logger.info("✅ API started successfully!")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down RAG-ENTERPRISE API...")

# Create FastAPI app
app = FastAPI(
    title="RAG-ENTERPRISE API",
    description="Enterprise-grade RAG platform with multi-agent support",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "name": "RAG-ENTERPRISE API",
        "version": "2.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health/health"
    }

# Include all routers
logger.info("📋 Registering routes...")

# Health routes (no prefix, direct access)
app.include_router(health.router, tags=["health"])

# Authentication routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Admin routes
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Dataset routes
app.include_router(datasets.router, prefix="/datasets", tags=["datasets"])

# Document routes
app.include_router(documents.router, prefix="/documents", tags=["documents"])

# Chat routes
app.include_router(chat.router, prefix="/chat", tags=["chat"])

# Conversation routes
app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])

# Analytics routes
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

# Tools routes
app.include_router(tools.router, prefix="/tools", tags=["tools"])

# Knowledge routes (search/upload skeleton)
app.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])

# Agents management routes (skeleton)
app.include_router(agents.router, prefix="/agents", tags=["agents"])

# Financial routes
app.include_router(financial.router, prefix="/financial", tags=["financial"])

# WebSocket routes
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

logger.info("✅ All routes registered successfully")

# Startup message
@app.on_event("startup")
async def startup_message():
    """Print startup message"""
    logger.info("=" * 60)
    logger.info("  RAG-ENTERPRISE API v2.1.0")
    logger.info("  Status: RUNNING")
    logger.info("  Docs: http://localhost:8000/docs")
    logger.info("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
