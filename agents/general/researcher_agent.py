# agents/general/researcher_agent.py
"""
وكيل الباحث - من agents
يبحث في المستندات ويجيب على الأسئلة
"""

from typing import Dict, List, Any, Optional

from core.base_agent import BaseAgent
from knowledge_base.retrieval.hybrid_search import HybridSearchEngine
from utilities.logger import logger


class ResearcherAgent(BaseAgent):
    """وكيل الباحث الذكي"""
    
    def __init__(self, search_engine: HybridSearchEngine):
        """
        تهيئة الوكيل
        
        Args:
            search_engine: محرك البحث
        """
        super().__init__(
            name="researcher",
            description="وكيل متخصص في البحث في المستندات والإجابة على الأسئلة",
            system_prompt="""أنت باحث خبير ومساعد ذكي.
            
مهمتك:
- البحث في المستندات المتاحة
- تقديم إجابات دقيقة ومفصلة
- الاستشهاد بالمصادر
- دعم اللغتين العربية والإنجليزية

قواعد الإجابة:
1. استخدم فقط المعلومات من المستندات المتاحة
2. إذا لم تجد إجابة، قل ذلك بصراحة
3. اذكر المصادر دائماً
4. كن واضحاً ومختصراً
5. استخدم نفس لغة السؤال في الإجابة"""
        )
        
        self.search_engine = search_engine
        logger.info(f"Initialized {self.name} agent with search capabilities")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ مهمة البحث
        
        Args:
            task: المهمة (يجب أن تحتوي على 'query')
            
        Returns:
            Dict: النتيجة
        """
        query = task.get("query") or task.get("input")
        
        if not query:
            return {
                "success": False,
                "error": "No query provided"
            }
        
        logger.info(f"Researcher agent processing: {query[:50]}...")
        
        # 1. البحث عن مستندات ذات صلة
        search_results = await self.search_engine.search(
            query=query,
            top_k=task.get("top_k", 5),
            index_name=task.get("index_name", "general")
        )
        
        logger.info(f"Found {len(search_results)} relevant documents")
        
        # 2. إعداد السياق
        context = self._prepare_context(search_results)
        
        # 3. توليد الإجابة باستخدام LLM
        answer = await self.chat(
            user_message=query,
            context=context,
            use_memory=task.get("use_memory", True)
        )
        
        # 4. إعداد النتيجة
        result = {
            "success": True,
            "query": query,
            "answer": answer,
            "sources": [
                {
                    "id": doc["id"],
                    "score": doc["combined_score"],
                    "preview": doc["content"][:200] + "..."
                }
                for doc in search_results[:3]
            ],
            "total_sources": len(search_results)
        }
        
        return result
    
    def _prepare_context(self, search_results: List[Dict]) -> List[Dict]:
        """إعداد السياق من نتائج البحث"""
        context = []
        
        for i, result in enumerate(search_results, 1):
            context.append({
                "title": f"مصدر {i} (درجة: {result['combined_score']:.2f})",
                "content": result["content"]
            })
        
        return context