# api/routes/chat.py
"""Endpoints للمحادثة - محدث للاستخدام المخزن المشترك"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from agents.general.researcher_agent import ResearcherAgent
from agents.general.qa_agent import QAAgent
from knowledge_base.retrieval.hybrid_search import HybridSearchEngine
from utilities.logger import logger

# استيراد من documents للحصول على نفس المخزن
from api.routes.documents import get_vector_store, get_embeddings

router = APIRouter(prefix="/chat", tags=["Chat"])

# استخدام المخزن المشترك
embeddings = get_embeddings()
vector_store = get_vector_store()
search_engine = HybridSearchEngine(embeddings, vector_store)

# الوكلاء
researcher_agent = ResearcherAgent(search_engine)
qa_agent = QAAgent()


class ChatRequest(BaseModel):
    """نموذج طلب المحادثة"""
    query: str
    use_search: bool = True
    top_k: Optional[int] = 5
    index_name: Optional[str] = "general"
    agent: Optional[str] = "auto"


class ChatResponse(BaseModel):
    """نموذج رد المحادثة"""
    success: bool
    query: str
    answer: str
    agent_used: str
    sources: Optional[List[dict]] = None
    total_sources: Optional[int] = 0


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """إرسال رسالة ومحادثة ذكية"""
    logger.info(f"Chat: {request.query[:50]}...")
    
    try:
        # اختيار الوكيل
        if request.agent == "auto":
            selected_agent = researcher_agent if request.use_search else qa_agent
        elif request.agent == "researcher":
            selected_agent = researcher_agent
        elif request.agent == "qa":
            selected_agent = qa_agent
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent: {request.agent}")
        
        # تنفيذ
        result = await selected_agent.execute({
            "query": request.query,
            "top_k": request.top_k,
            "index_name": request.index_name,
            "use_memory": True
        })
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed"))
        
        response = ChatResponse(
            success=True,
            query=request.query,
            answer=result["answer"],
            agent_used=selected_agent.name,
            sources=result.get("sources"),
            total_sources=result.get("total_sources", 0)
        )
        
        logger.info(f"✅ Response by {selected_agent.name}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agents():
    """قائمة الوكلاء"""
    return {
        "agents": [
            {
                "name": researcher_agent.name,
                "description": researcher_agent.description,
                "stats": researcher_agent.get_stats()
            },
            {
                "name": qa_agent.name,
                "description": qa_agent.description,
                "stats": qa_agent.get_stats()
            }
        ]
    }


@router.post("/reset-memory")
async def reset_memory():
    """إعادة تعيين الذاكرة"""
    researcher_agent.reset_memory()
    qa_agent.reset_memory()
    return {"success": True, "message": "Memory reset"}