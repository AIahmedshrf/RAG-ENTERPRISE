# orchestration/patterns/router_pattern.py
"""
نمط التوجيه - من agentpatterns
يختار الوكيل الأنسب للمهمة تلقائياً
"""

from typing import Dict, Any, List
import re

from utilities.logger import logger


class RouterPattern:
    """نمط توجيه الوكلاء"""
    
    def __init__(self):
        self.name = "router"
        
        # قواعد التوجيه
        self.routing_rules = {
            "financial": {
                "keywords": [
                    "سهم", "أسهم", "استثمار", "محفظة", "مالي", "تقرير مالي",
                    "stock", "investment", "portfolio", "financial", "revenue"
                ],
                "agents": ["financial_analyst", "investment_advisor"]
            },
            "research": {
                "keywords": [
                    "بحث", "دراسة", "ورقة علمية", "مرجع", "اقتباس",
                    "research", "study", "paper", "citation", "reference"
                ],
                "agents": ["deep_research", "researcher"]
            },
            "general": {
                "keywords": [],  # افتراضي
                "agents": ["researcher", "qa"]
            }
        }
        
        logger.info("Initialized RouterPattern")
    
    def route(self, query: str, available_agents: List[str]) -> str:
        """
        توجيه الاستعلام للوكيل المناسب
        
        Args:
            query: الاستعلام
            available_agents: الوكلاء المتاحين
            
        Returns:
            str: اسم الوكيل المختار
        """
        query_lower = query.lower()
        
        # المرور على قواعد التوجيه
        for category, rules in self.routing_rules.items():
            # التحقق من الكلمات المفتاحية
            for keyword in rules["keywords"]:
                if keyword in query_lower:
                    # اختيار أول وكيل متاح من الفئة
                    for agent in rules["agents"]:
                        if agent in available_agents:
                            logger.info(
                                f"Routed to {agent} (category: {category}, "
                                f"keyword: {keyword})"
                            )
                            return agent
        
        # افتراضي: أول وكيل عام متاح
        for agent in self.routing_rules["general"]["agents"]:
            if agent in available_agents:
                logger.info(f"Routed to {agent} (default)")
                return agent
        
        # إذا لم يوجد، أول وكيل متاح
        if available_agents:
            logger.warning(f"Using fallback: {available_agents[0]}")
            return available_agents[0]
        
        raise ValueError("No agents available for routing")
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        تحليل الاستعلام
        
        Returns:
            Dict: تحليل شامل
        """
        query_lower = query.lower()
        
        analysis = {
            "query": query,
            "length": len(query),
            "word_count": len(query.split()),
            "detected_categories": [],
            "has_question": self._is_question(query),
            "language": "ar" if self._is_arabic(query) else "en"
        }
        
        # كشف الفئات
        for category, rules in self.routing_rules.items():
            matched_keywords = [
                kw for kw in rules["keywords"]
                if kw in query_lower
            ]
            if matched_keywords:
                analysis["detected_categories"].append({
                    "category": category,
                    "keywords": matched_keywords
                })
        
        return analysis
    
    def _is_question(self, text: str) -> bool:
        """التحقق من كون النص سؤالاً"""
        question_indicators = [
            "؟", "?", "ما", "من", "كيف", "لماذا", "متى", "أين", "هل",
            "what", "who", "how", "why", "when", "where", "is", "are"
        ]
        text_lower = text.lower()
        return any(ind in text_lower for ind in question_indicators)
    
    def _is_arabic(self, text: str) -> bool:
        """التحقق من وجود نص عربي"""
        return bool(re.search(r'[\u0600-\u06FF]', text))