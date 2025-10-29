# core/base_agent.py
"""الوكيل الأساسي - من agents + agentpatterns"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from openai import AsyncAzureOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from core.config import config
from utilities.logger import logger


class AgentMemory:
    """ذاكرة الوكيل"""
    def __init__(self, max_messages: int = 10):
        self.messages: List[Dict] = []
        self.max_messages = max_messages
    
    def add(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_context(self) -> List[Dict]:
        return [{"role": m["role"], "content": m["content"]} for m in self.messages]
    
    def clear(self):
        self.messages = []


class BaseAgent(ABC):
    """الوكيل الأساسي"""
    
    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        enable_memory: bool = True
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.enable_memory = enable_memory
        
        self.memory = AgentMemory() if enable_memory else None
        
        # إعداد OpenAI Client
        if HAS_OPENAI and config.azure_openai.api_key:
            self.client = AsyncAzureOpenAI(
                api_key=config.azure_openai.api_key,
                api_version=config.azure_openai.api_version,
                azure_endpoint=config.azure_openai.endpoint
            )
        else:
            self.client = None
            logger.warning(f"{name} agent: OpenAI not configured")
        
        self.stats = {"calls": 0, "total_tokens": 0, "errors": 0}
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """تنفيذ المهمة - يجب تنفيذها في الصنف الفرعي"""
        pass
    
    async def chat(
        self,
        user_message: str,
        context: Optional[List[Dict]] = None,
        use_memory: bool = True
    ) -> str:
        """محادثة مع الوكيل"""
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if use_memory and self.memory:
                messages.extend(self.memory.get_context())
            
            if context:
                context_text = self._format_context(context)
                messages.append({
                    "role": "system",
                    "content": f"السياق المتاح:\n{context_text}"
                })
            
            messages.append({"role": "user", "content": user_message})
            
            if not self.client:
                return "عذراً، نظام الذكاء الاصطناعي غير متاح حالياً. يرجى التحقق من الإعدادات."
            
            response = await self.client.chat.completions.create(
                model=config.azure_openai.chat_deployment,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content
            
            if use_memory and self.memory:
                self.memory.add("user", user_message)
                self.memory.add("assistant", answer)
            
            self.stats["calls"] += 1
            self.stats["total_tokens"] += response.usage.total_tokens
            
            return answer
        
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error in {self.name} chat: {e}")
            return f"عذراً، حدث خطأ: {str(e)}"
    
    def _format_context(self, context: List[Dict]) -> str:
        formatted = []
        for i, item in enumerate(context, 1):
            if isinstance(item, dict):
                content = item.get("content", str(item))
                title = item.get("title", f"مستند {i}")
                formatted.append(f"[{i}] {title}:\n{content[:500]}...\n")
            else:
                formatted.append(f"[{i}] {str(item)[:500]}...\n")
        return "\n".join(formatted)
    
    def reset_memory(self):
        if self.memory:
            self.memory.clear()
    
    def get_stats(self) -> Dict:
        return {"agent": self.name, **self.stats}