# knowledge_base/vector_store/memory_store.py
"""
مخزن vector محلي في الذاكرة - للتطوير والاختبار
في الإنتاج، استخدم Azure AI Search
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

from utilities.logger import logger


@dataclass
class VectorDocument:
    """مستند مع vector embedding"""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            "id": self.id,
            "content": self.content,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "created_at": self.created_at
        }


class MemoryVectorStore:
    """مخزن vectors في الذاكرة"""
    
    def __init__(self):
        """تهيئة المخزن"""
        self.documents: Dict[str, VectorDocument] = {}
        self.indexes: Dict[str, Dict[str, VectorDocument]] = {
            "general": {},
            "financial": {},
            "research": {}
        }
        
        logger.info("Initialized MemoryVectorStore")
    
    async def add_document(
        self,
        doc_id: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict] = None,
        index_name: str = "general"
    ) -> bool:
        """
        إضافة مستند
        
        Args:
            doc_id: معرف المستند
            content: المحتوى
            embedding: Vector embedding
            metadata: بيانات وصفية
            index_name: اسم الفهرس
            
        Returns:
            bool: نجح أم لا
        """
        try:
            # إنشاء المستند
            doc = VectorDocument(
                id=doc_id,
                content=content,
                embedding=embedding,
                metadata=metadata or {}
            )
            
            # حفظ في المخزن الرئيسي
            self.documents[doc_id] = doc
            
            # حفظ في الفهرس المحدد
            if index_name not in self.indexes:
                self.indexes[index_name] = {}
            
            self.indexes[index_name][doc_id] = doc
            
            logger.debug(f"Added document {doc_id} to {index_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    async def add_documents_batch(
        self,
        documents: List[Dict],
        index_name: str = "general"
    ) -> int:
        """
        إضافة مجموعة مستندات
        
        Args:
            documents: قائمة مستندات (كل واحد dict بـ id, content, embedding, metadata)
            index_name: اسم الفهرس
            
        Returns:
            int: عدد المستندات المضافة
        """
        count = 0
        for doc in documents:
            success = await self.add_document(
                doc_id=doc["id"],
                content=doc["content"],
                embedding=doc["embedding"],
                metadata=doc.get("metadata"),
                index_name=index_name
            )
            if success:
                count += 1
        
        logger.info(f"Added {count}/{len(documents)} documents to {index_name}")
        return count
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        index_name: str = "general",
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        البحث عن مستندات مشابهة
        
        Args:
            query_embedding: Embedding الاستعلام
            top_k: عدد النتائج
            index_name: الفهرس
            filters: فلاتر إضافية
            
        Returns:
            List[Dict]: المستندات المطابقة
        """
        # الحصول على الفهرس
        index = self.indexes.get(index_name, {})
        
        if not index:
            logger.warning(f"Index {index_name} is empty")
            return []
        
        # حساب التشابه لكل مستند
        similarities = []
        
        for doc_id, doc in index.items():
            # تطبيق الفلاتر
            if filters:
                if not self._apply_filters(doc, filters):
                    continue
            
            # حساب التشابه
            similarity = self._cosine_similarity(query_embedding, doc.embedding)
            
            similarities.append({
                "id": doc.id,
                "content": doc.content,
                "metadata": doc.metadata,
                "score": similarity,
                "created_at": doc.created_at
            })
        
        # ترتيب حسب الدرجة
        similarities.sort(key=lambda x: x["score"], reverse=True)
        
        # إرجاع أفضل k
        results = similarities[:top_k]
        
        logger.debug(f"Search returned {len(results)} results from {index_name}")
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """حساب التشابه"""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _apply_filters(self, doc: VectorDocument, filters: Dict) -> bool:
        """تطبيق الفلاتر"""
        for key, value in filters.items():
            if key not in doc.metadata:
                return False
            if doc.metadata[key] != value:
                return False
        return True
    
    async def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """الحصول على مستند بالمعرف"""
        return self.documents.get(doc_id)
    
    async def delete_document(self, doc_id: str) -> bool:
        """حذف مستند"""
        if doc_id not in self.documents:
            return False
        
        # حذف من المخزن الرئيسي
        del self.documents[doc_id]
        
        # حذف من جميع الفهارس
        for index in self.indexes.values():
            if doc_id in index:
                del index[doc_id]
        
        logger.debug(f"Deleted document {doc_id}")
        return True
    
    def get_stats(self) -> Dict:
        """إحصائيات المخزن"""
        return {
            "total_documents": len(self.documents),
            "indexes": {
                name: len(docs)
                for name, docs in self.indexes.items()
            }
        }
    
    async def clear_index(self, index_name: str):
        """مسح فهرس"""
        if index_name in self.indexes:
            # حذف من المخزن الرئيسي
            for doc_id in list(self.indexes[index_name].keys()):
                if doc_id in self.documents:
                    del self.documents[doc_id]
            
            # مسح الفهرس
            self.indexes[index_name] = {}
            logger.info(f"Cleared index: {index_name}")