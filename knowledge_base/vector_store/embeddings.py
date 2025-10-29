# knowledge_base/vector_store/embeddings.py
"""
نظام Embeddings - محدث لـ openai>=1.0.0
"""

from typing import List, Union
import hashlib

try:
    from openai import AsyncAzureOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from core.config import config
from utilities.logger import logger


class EmbeddingsGenerator:
    """مولد Embeddings - متوافق مع OpenAI 1.0+"""
    
    def __init__(self):
        """تهيئة مولد Embeddings"""
        if not HAS_OPENAI:
            logger.warning("OpenAI not installed. Using fallback embeddings.")
            self.client = None
        else:
            try:
                # إعداد Azure OpenAI Client الجديد
                self.client = AsyncAzureOpenAI(
                    api_key=config.azure_openai.api_key,
                    api_version=config.azure_openai.api_version,
                    azure_endpoint=config.azure_openai.endpoint
                )
                self.deployment = config.azure_openai.embedding_deployment
                logger.info("✅ Azure OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        
        self.cache = {}
        logger.info(f"Initialized EmbeddingsGenerator (using_openai={self.client is not None})")
    
    async def generate(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """توليد embeddings للنص"""
        if isinstance(text, str):
            return await self._generate_single(text)
        
        embeddings = []
        for t in text:
            emb = await self._generate_single(t)
            embeddings.append(emb)
        return embeddings
    
    async def _generate_single(self, text: str) -> List[float]:
        """توليد embedding لنص واحد"""
        if not text or not text.strip():
            return self._get_zero_embedding()
        
        cache_key = self._get_cache_key(text)
        if cache_key in self.cache:
            logger.debug("Using cached embedding")
            return self.cache[cache_key]
        
        if self.client:
            embedding = await self._generate_with_openai(text)
        else:
            embedding = self._generate_fallback(text)
        
        self.cache[cache_key] = embedding
        return embedding
    
    async def _generate_with_openai(self, text: str) -> List[float]:
        """توليد embedding باستخدام Azure OpenAI (API الجديد)"""
        try:
            if len(text) > 8000:
                text = text[:8000]
                logger.warning("Text truncated to 8000 chars")
            
            response = await self.client.embeddings.create(
                input=text,
                model=self.deployment
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated OpenAI embedding: {len(embedding)} dims")
            return embedding
        
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            logger.warning("Falling back to simple embedding")
            return self._generate_fallback(text)
    
    def _generate_fallback(self, text: str) -> List[float]:
        """توليد embedding بسيط (للتطوير)"""
        text_hash = hashlib.sha256(text.encode()).digest()
        embedding = [float(b) / 255.0 for b in text_hash]
        
        while len(embedding) < 1536:
            embedding.extend(embedding[:min(32, 1536 - len(embedding))])
        
        embedding = embedding[:1536]
        logger.debug(f"Generated fallback embedding: {len(embedding)} dims")
        return embedding
    
    def _get_zero_embedding(self) -> List[float]:
        return [0.0] * 1536
    
    def _get_cache_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    def cosine_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """حساب التشابه"""
        import math
        dot = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = math.sqrt(sum(a * a for a in emb1))
        norm2 = math.sqrt(sum(b * b for b in emb2))
        return dot / (norm1 * norm2) if norm1 and norm2 else 0.0
    
    def clear_cache(self):
        self.cache.clear()
        logger.info("Embeddings cache cleared")