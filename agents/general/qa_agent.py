# agents/general/qa_agent.py
"""
وكيل الأسئلة والأجوبة - مبسط وسريع
"""

from typing import Dict, Any

from core.base_agent import BaseAgent
from utilities.logger import logger


class QAAgent(BaseAgent):
    """وكيل بسيط للأسئلة والأجوبة"""
    
    def __init__(self):
        super().__init__(
            name="qa",
            description="وكيل للإجابة على الأسئلة العامة",
            system_prompt="""أنت مساعد ذكي ومفيد.
            
أجب على الأسئلة بوضوح ودقة.
استخدم نفس لغة السؤال في الإجابة.
إذا لم تعرف الإجابة، قل ذلك بصراحة."""
        )
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """تنفيذ مهمة السؤال والجواب"""
        query = task.get("query") or task.get("input")
        
        if not query:
            return {"success": False, "error": "No query provided"}
        
        logger.info(f"QA agent processing: {query[:50]}...")
        
        # إجابة مباشرة بدون بحث
        answer = await self.chat(
            user_message=query,
            context=task.get("context"),
            use_memory=task.get("use_memory", True)
        )
        
        return {
            "success": True,
            "query": query,
            "answer": answer,
            "agent": self.name
        }