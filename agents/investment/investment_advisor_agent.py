# agents/investment/investment_advisor_agent.py
"""
وكيل الاستشارات الاستثمارية - من investmentagent
متخصص في تقديم توصيات استثمارية
"""

from typing import Dict, Any
from datetime import datetime

from core.base_agent import BaseAgent
from knowledge_base.retrieval.hybrid_search import HybridSearchEngine
from utilities.logger import logger


class InvestmentAdvisorAgent(BaseAgent):
    """وكيل الاستشارات الاستثمارية"""
    
    def __init__(self, search_engine: HybridSearchEngine):
        super().__init__(
            name="investment_advisor",
            description="وكيل متخصص في الاستشارات الاستثمارية والتوصيات",
            system_prompt="""أنت مستشار استثماري خبير.

مهامك:
- تقديم استشارات استثمارية مبنية على البيانات
- تحليل الفرص الاستثمارية
- تقييم المخاطر والعوائد
- المساعدة في بناء محافظ استثمارية متنوعة

مبادئ الاستثمار:
1. التنويع لتقليل المخاطر
2. الأفق الزمني مهم
3. فهم ملف المخاطر للمستثمر
4. المراجعة الدورية للمحفظة

تحذير مهم:
- هذه توصيات تعليمية وليست نصائح استثمارية ملزمة
- يجب استشارة مستشار مالي مرخص قبل اتخاذ قرارات استثمارية
- الأداء السابق لا يضمن النتائج المستقبلية

استخدم لغة واضحة ومهنية."""
        )
        
        self.search_engine = search_engine
        logger.info(f"Initialized {self.name}")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """تنفيذ الاستشارة الاستثمارية"""
        query = task.get("query") or task.get("input")
        
        if not query:
            return {"success": False, "error": "No query provided"}
        
        logger.info(f"Investment advisor processing: {query[:50]}...")
        
        # البحث عن معلومات استثمارية
        search_results = await self.search_engine.search(
            query=query,
            top_k=5,
            index_name="financial"
        )
        
        # إعداد السياق
        context = [
            {
                "title": f"مصدر {i+1}",
                "content": doc["content"]
            }
            for i, doc in enumerate(search_results)
        ]
        
        # التحليل والتوصية
        answer = await self.chat(
            user_message=query,
            context=context,
            use_memory=True
        )
        
        return {
            "success": True,
            "query": query,
            "answer": answer,
            "disclaimer": "⚠️ هذه توصيات تعليمية فقط. استشر مستشاراً مالياً مرخصاً.",
            "timestamp": datetime.now().isoformat(),
            "sources": [
                {"id": doc["id"], "score": doc["combined_score"]}
                for doc in search_results[:3]
            ]
        }