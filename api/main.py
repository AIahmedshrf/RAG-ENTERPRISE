"""
Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import config
from api.database import init_db
from utilities.logger import logger

# إنشاء التطبيق
app = FastAPI(
    title="RAG-ENTERPRISE API",
    description="AI-Powered Enterprise RAG System",
    version="1.0.0",
    docs_url="/docs" if config.debug else None,
    redoc_url="/redoc" if config.debug else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup Event
@app.on_event("startup")
async def startup_event():
    """تهيئة عند البدء"""
    logger.info("🚀 Starting RAG-ENTERPRISE...")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Debug mode: {config.debug}")
    
    # إنشاء قاعدة البيانات
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # عرض معلومات التكوين
    config_summary = {
        "environment": config.environment,
        "debug": config.debug,
        "api": f"{config.api_host}:{config.api_port}",
        "azure_openai_configured": bool(config.azure_openai.api_key),
        "azure_search_configured": bool(config.azure_search.api_key),
        "financial_features_enabled": True,
        "supported_languages": ["ar", "en"],
    }
    
    logger.info(f"Configuration summary: {config_summary}")


# Root endpoint
@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "name": "RAG-ENTERPRISE API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs" if config.debug else "disabled",
        "features": {
            "documents": "✅",
            "chat": "✅",
            "financial": "✅",
            "admin": "✅",
        }
    }


# Health check
@app.get("/health")
async def health_check():
    """فحص صحة النظام"""
    return {
        "status": "healthy",
        "environment": config.environment,
        "version": "1.0.0"
    }


# Config endpoint
@app.get("/config")
async def get_config():
    """عرض التكوين"""
    return {
        "environment": config.environment,
        "debug": config.debug,
        "features": {
            "azure_openai": bool(config.azure_openai.api_key),
            "azure_search": bool(config.azure_search.api_key),
        }
    }


# ===== Import Routes =====
from api.routes import documents, chat, financial
from api.routes.admin import users, models

# ===== Include Routers =====
app.include_router(documents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(financial.router, prefix="/api/v1")

# Admin Routes
app.include_router(users.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug,
    )
