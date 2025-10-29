# api/routes/financial.py
"""
Endpoints للخدمات المالية
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from agents.financial.financial_analyst_agent import FinancialAnalystAgent
from agents.investment.investment_advisor_agent import InvestmentAdvisorAgent
from api.routes.documents import get_vector_store, get_embeddings
from knowledge_base.retrieval.hybrid_search import HybridSearchEngine
from utilities.logger import logger

router = APIRouter(prefix="/financial", tags=["Financial Services"])

# إعداد المكونات
embeddings = get_embeddings()
vector_store = get_vector_store()
search_engine = HybridSearchEngine(embeddings, vector_store)

# الوكلاء الماليون
financial_analyst = FinancialAnalystAgent(search_engine)
investment_advisor = InvestmentAdvisorAgent(search_engine)


class FinancialAnalysisRequest(BaseModel):
    """طلب تحليل مالي"""
    query: str
    document_id: Optional[str] = None
    include_ratios: bool = True


class InvestmentAdviceRequest(BaseModel):
    """طلب استشارة استثمارية"""
    query: str
    risk_tolerance: Optional[str] = "moderate"  # conservative, moderate, aggressive


@router.post("/analyze")
async def financial_analysis(request: FinancialAnalysisRequest):
    """
    تحليل مالي متخصص
    
    يستخدم الوكيل المالي لتحليل التقارير المالية
    """
    logger.info(f"Financial analysis: {request.query[:50]}...")
    
    try:
        result = await financial_analyst.execute({
            "query": request.query,
            "top_k": 5,
            "index_name": "financial",
            "use_memory": True
        })
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail="Analysis failed")
        
        return {
            "success": True,
            "analysis": result["answer"],
            "financial_data": result.get("financial_data"),
            "sources": result.get("sources"),
            "agent": financial_analyst.name
        }
    
    except Exception as e:
        logger.error(f"Financial analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/investment-advice")
async def investment_advice(request: InvestmentAdviceRequest):
    """
    استشارة استثمارية
    
    يستخدم وكيل الاستثمار لتقديم توصيات
    """
    logger.info(f"Investment advice: {request.query[:50]}...")
    
    try:
        result = await investment_advisor.execute({
            "query": request.query,
            "use_memory": True
        })
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail="Advice generation failed")
        
        return {
            "success": True,
            "advice": result["answer"],
            "disclaimer": result["disclaimer"],
            "timestamp": result["timestamp"],
            "sources": result.get("sources"),
            "agent": investment_advisor.name
        }
    
    except Exception as e:
        logger.error(f"Investment advice error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_financial_agents():
    """قائمة الوكلاء الماليين"""
    return {
        "agents": [
            {
                "name": financial_analyst.name,
                "description": financial_analyst.description,
                "stats": financial_analyst.get_stats()
            },
            {
                "name": investment_advisor.name,
                "description": investment_advisor.description,
                "stats": investment_advisor.get_stats()
            }
        ]
    }