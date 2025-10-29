# api/main.py
"""
نقطة الدخول الرئيسية لـ FastAPI
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

from core.config import config
from core.exceptions import RAGEnterpriseException
from utilities.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """دورة حياة التطبيق"""
    # Startup
    logger.info("🚀 Starting RAG-ENTERPRISE...")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Debug mode: {config.debug}")
    
    try:
        config.validate()
        logger.info("✅ Configuration validated successfully")
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        raise
    
    logger.info(f"Configuration summary: {config.get_summary()}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down RAG-ENTERPRISE...")


# إنشاء تطبيق FastAPI
app = FastAPI(
    title="RAG-ENTERPRISE",
    description="AI-Powered Enterprise RAG System with Financial Intelligence",
    version="1.0.0",
    lifespan=lifespan
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware للتوقيت
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# معالج الأخطاء العام
@app.exception_handler(RAGEnterpriseException)
async def rag_exception_handler(request: Request, exc: RAGEnterpriseException):
    logger.error(f"RAG Exception: {exc.message} - Details: {exc.details}")
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred"
        }
    )

# ===== إضافة Routes =====
from api.routes import documents, chat

app.include_router(documents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

# Routes الأساسية
@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "message": "Welcome to RAG-ENTERPRISE",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """فحص الصحة"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": config.environment
    }


@app.get("/config")
async def get_config():
    """عرض ملخص التكوين"""
    return config.get_summary()


# سيتم إضافة المزيد من Routes لاحقاً
# من: api/routes/documents.py, chat.py, financial.py, etc.


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug
    )