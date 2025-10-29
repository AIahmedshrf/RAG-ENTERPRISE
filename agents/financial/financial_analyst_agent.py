# agents/financial/financial_analyst_agent.py
"""
وكيل التحليل المالي - من wealthops
متخصص في تحليل التقارير المالية والقوائم المالية
"""

from typing import Dict, Any, List, Optional
import re

from core.base_agent import BaseAgent
from knowledge_base.retrieval.hybrid_search import HybridSearchEngine
from utilities.logger import logger


class FinancialAnalystAgent(BaseAgent):
    """وكيل التحليل المالي المتخصص"""
    
    def __init__(self, search_engine: HybridSearchEngine):
        super().__init__(
            name="financial_analyst",
            description="وكيل متخصص في تحليل التقارير والبيانات المالية",
            system_prompt="""أنت محلل مالي خبير ومحترف.

مهامك:
- تحليل القوائم المالية (الميزانية، الدخل، التدفقات النقدية)
- حساب النسب المالية الرئيسية
- تقييم الأداء المالي للشركات
- تقديم رؤى استثمارية مبنية على البيانات

النسب المالية المهمة:
- نسب السيولة (Current Ratio, Quick Ratio)
- نسب الربحية (ROA, ROE, Profit Margin)
- نسب المديونية (Debt to Equity)
- نسب الكفاءة (Asset Turnover)

قواعد التحليل:
1. استخدم الأرقام والنسب الفعلية من التقارير
2. قارن بمعايير الصناعة عند الإمكان
3. اذكر المصادر والفترات الزمنية
4. كن موضوعياً وواقعياً
5. قدم توصيات عملية

استخدم اللغة العربية والإنجليزية بطلاقة."""
        )
        
        self.search_engine = search_engine
        
        # مصطلحات مالية
        self.financial_terms = {
            "ar": ["إيرادات", "أرباح", "خسائر", "أصول", "خصوم", "حقوق الملكية", "تدفق نقدي"],
            "en": ["revenue", "profit", "loss", "assets", "liabilities", "equity", "cash flow"]
        }
        
        logger.info(f"Initialized {self.name} with financial expertise")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """تنفيذ التحليل المالي"""
        query = task.get("query") or task.get("input")
        
        if not query:
            return {"success": False, "error": "No query provided"}
        
        logger.info(f"Financial analyst processing: {query[:50]}...")
        
        # البحث في المستندات المالية
        search_results = await self.search_engine.search(
            query=query,
            top_k=task.get("top_k", 5),
            index_name=task.get("index_name", "financial"),
            filters=task.get("filters")
        )
        
        # استخراج الأرقام المالية من النتائج
        financial_data = self._extract_financial_data(search_results)
        
        # إعداد السياق المعزز
        context = self._prepare_financial_context(search_results, financial_data)
        
        # التحليل باستخدام LLM
        answer = await self.chat(
            user_message=query,
            context=context,
            use_memory=task.get("use_memory", True)
        )
        
        return {
            "success": True,
            "query": query,
            "answer": answer,
            "financial_data": financial_data,
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
    
    def _extract_financial_data(self, documents: List[Dict]) -> Dict:
        """استخراج البيانات المالية من المستندات"""
        financial_data = {
            "numbers": [],
            "ratios": [],
            "currencies": []
        }
        
        for doc in documents:
            content = doc.get("content", "")
            
            # استخراج الأرقام الكبيرة (محتمل أن تكون مبالغ مالية)
            numbers = re.findall(r'\d{1,3}(?:[,،]\d{3})*(?:\.\d+)?', content)
            financial_data["numbers"].extend(numbers[:5])  # أول 5 أرقام
            
            # استخراج النسب المئوية
            percentages = re.findall(r'\d+(?:\.\d+)?%', content)
            financial_data["ratios"].extend(percentages[:3])
            
            # استخراج العملات
            currencies = re.findall(r'(?:USD|EUR|SAR|ريال|دولار|\$|€)', content)
            financial_data["currencies"].extend(set(currencies))
        
        return financial_data
    
    def _prepare_financial_context(self, documents: List[Dict], financial_data: Dict) -> List[Dict]:
        """إعداد سياق مالي معزز"""
        context = []
        
        # إضافة المستندات
        for i, doc in enumerate(documents, 1):
            context.append({
                "title": f"تقرير مالي {i} (درجة: {doc['combined_score']:.2f})",
                "content": doc["content"]
            })
        
        # إضافة البيانات المستخرجة
        if financial_data["numbers"] or financial_data["ratios"]:
            summary = f"""
بيانات مالية مستخرجة:
- أرقام رئيسية: {', '.join(financial_data['numbers'][:5])}
- نسب: {', '.join(financial_data['ratios'][:3])}
- عملات: {', '.join(set(financial_data['currencies']))}
            """
            context.append({
                "title": "ملخص البيانات المالية",
                "content": summary
            })
        
        return context