# knowledge_base/retrieval/hybrid_search.py
"""
نظام البحث الهجين - من aisearchmm
يجمع بين Vector Search و Keyword Search
"""

from typing import List, Dict, Optional
import re

from knowledge_base.vector_store.embeddings import EmbeddingsGenerator
from knowledge_base.vector_store.memory_store import MemoryVectorStore
from utilities.logger import logger


class HybridSearchEngine:
    """محرك البحث الهجين"""
    
    def __init__(
        self,
        embeddings_generator: EmbeddingsGenerator,
        vector_store: MemoryVectorStore,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ):
        """
        تهيئة محرك البحث
        
        Args:
            embeddings_generator: مولد embeddings
            vector_store: مخزن vectors
            vector_weight: وزن البحث بالـ vectors
            keyword_weight: وزن البحث بالكلمات المفتاحية
        """
        self.embeddings = embeddings_generator
        self.vector_store = vector_store
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
        
        logger.info(
            f"Initialized HybridSearchEngine "
            f"(vector={vector_weight}, keyword={keyword_weight})"
        )
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        index_name: str = "general",
        filters: Optional[Dict] = None,
        use_vector: bool = True,
        use_keyword: bool = True
    ) -> List[Dict]:
        """
        البحث الهجين
        
        Args:
            query: الاستعلام
            top_k: عدد النتائج
            index_name: الفهرس
            filters: فلاتر
            use_vector: استخدام vector search
            use_keyword: استخدام keyword search
            
        Returns:
            List[Dict]: النتائج المرتبة
        """
        logger.info(f"Hybrid search: '{query[:50]}...'")
        
        results = []
        
        # 1. Vector Search
        if use_vector:
            vector_results = await self._vector_search(
                query, top_k * 2, index_name, filters
            )
            results.extend(vector_results)
        
        # 2. Keyword Search
        if use_keyword:
            keyword_results = await self._keyword_search(
                query, top_k * 2, index_name, filters
            )
            results.extend(keyword_results)
        
        # 3. دمج وترتيب النتائج
        merged_results = self._merge_results(results)
        
        # 4. إرجاع أفضل k
        final_results = merged_results[:top_k]
        
        logger.info(f"Hybrid search returned {len(final_results)} results")
        return final_results
    
    async def _vector_search(
        self,
        query: str,
        top_k: int,
        index_name: str,
        filters: Optional[Dict]
    ) -> List[Dict]:
        """البحث باستخدام vectors"""
        # توليد embedding للاستعلام
        query_embedding = await self.embeddings.generate(query)
        
        # البحث
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            index_name=index_name,
            filters=filters
        )
        
        # إضافة نوع البحث والوزن
        for result in results:
            result["search_type"] = "vector"
            result["weighted_score"] = result["score"] * self.vector_weight
        
        return results
    
    async def _keyword_search(
        self,
        query: str,
        top_k: int,
        index_name: str,
        filters: Optional[Dict]
    ) -> List[Dict]:
        """البحث باستخدام الكلمات المفتاحية"""
        # استخراج الكلمات المفتاحية
        keywords = self._extract_keywords(query)
        
        # الحصول على جميع المستندات من الفهرس
        index = self.vector_store.indexes.get(index_name, {})
        
        results = []
        for doc_id, doc in index.items():
            # تطبيق الفلاتر
            if filters and not self._apply_filters(doc, filters):
                continue
            
            # حساب درجة التطابق
            score = self._calculate_keyword_score(keywords, doc.content)
            
            if score > 0:
                results.append({
                    "id": doc.id,
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "score": score,
                    "search_type": "keyword",
                    "weighted_score": score * self.keyword_weight,
                    "created_at": doc.created_at
                })
        
        # ترتيب
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """استخراج الكلمات المفتاحية"""
        # تنظيف النص
        text = text.lower()
        
        # إزالة علامات الترقيم
        text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
        
        # تقسيم إلى كلمات
        words = text.split()
        
        # إزالة الكلمات القصيرة جداً والشائعة
        stop_words = {'the', 'is', 'at', 'which', 'on', 'في', 'من', 'إلى', 'على', 'هو', 'هي'}
        keywords = [w for w in words if len(w) > 2 and w not in stop_words]
        
        return keywords
    
    def _calculate_keyword_score(self, keywords: List[str], content: str) -> float:
        """حساب درجة التطابق بالكلمات المفتاحية"""
        content_lower = content.lower()
        
        # حساب عدد الكلمات المطابقة
        matches = sum(1 for keyword in keywords if keyword in content_lower)
        
        if not keywords:
            return 0.0
        
        # النسبة المئوية للتطابق
        score = matches / len(keywords)
        
        return score
    
    def _merge_results(self, results: List[Dict]) -> List[Dict]:
        """دمج نتائج البحث المختلفة"""
        # تجميع حسب ID
        merged = {}
        
        for result in results:
            doc_id = result["id"]
            
            if doc_id not in merged:
                merged[doc_id] = result.copy()
                merged[doc_id]["combined_score"] = result["weighted_score"]
                merged[doc_id]["search_types"] = [result["search_type"]]
            else:
                # دمج الدرجات
                merged[doc_id]["combined_score"] += result["weighted_score"]
                if result["search_type"] not in merged[doc_id]["search_types"]:
                    merged[doc_id]["search_types"].append(result["search_type"])
        
        # تحويل إلى قائمة وترتيب
        merged_list = list(merged.values())
        merged_list.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return merged_list
    
    def _apply_filters(self, doc, filters: Dict) -> bool:
        """تطبيق الفلاتر"""
        for key, value in filters.items():
            if key not in doc.metadata:
                return False
            if doc.metadata[key] != value:
                return False
        return True