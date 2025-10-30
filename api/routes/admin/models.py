"""
AI Models Management APIs
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from utilities.logger import logger

router = APIRouter(prefix="/admin/models", tags=["Admin - Models"])


class ModelConfig(BaseModel):
    name: str
    provider: str  # openai, azure, anthropic
    deployment_name: Optional[str] = None
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7


# Mock data للتطوير
MODELS_DB = [
    {
        "id": "1",
        "name": "GPT-4",
        "provider": "azure",
        "deployment_name": "gpt-4",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "2",
        "name": "GPT-3.5 Turbo",
        "provider": "azure",
        "deployment_name": "gpt-35-turbo",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z"
    }
]


@router.get("/")
async def list_models():
    """قائمة النماذج المتاحة"""
    return {
        "success": True,
        "models": MODELS_DB
    }


@router.get("/{model_id}")
async def get_model(model_id: str):
    """الحصول على نموذج محدد"""
    model = next((m for m in MODELS_DB if m["id"] == model_id), None)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.post("/")
async def create_model(model: ModelConfig):
    """إضافة نموذج جديد"""
    new_model = {
        "id": str(len(MODELS_DB) + 1),
        "name": model.name,
        "provider": model.provider,
        "deployment_name": model.deployment_name,
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z"
    }
    MODELS_DB.append(new_model)
    
    logger.info(f"Created model: {model.name}")
    return {"success": True, "model": new_model}


@router.delete("/{model_id}")
async def delete_model(model_id: str):
    """حذف نموذج"""
    global MODELS_DB
    MODELS_DB = [m for m in MODELS_DB if m["id"] != model_id]
    
    logger.info(f"Deleted model: {model_id}")
    return {"success": True, "message": "Model deleted"}


@router.get("/providers/list")
async def list_providers():
    """قائمة مقدمي الخدمة المدعومين"""
    return {
        "providers": [
            {"id": "azure", "name": "Azure OpenAI"},
            {"id": "openai", "name": "OpenAI"},
            {"id": "anthropic", "name": "Anthropic Claude"}
        ]
    }
