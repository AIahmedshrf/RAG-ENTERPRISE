"""
RAG Pipeline - Complete Retrieval-Augmented Generation
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

from knowledge_base.retrieval.retriever import DocumentRetriever
from knowledge_base.embeddings.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Complete RAG pipeline: retrieve → rerank → generate"""
    
    def __init__(self, db: Session):
        self.db = db
        self.retriever = DocumentRetriever(db)
        self.embedding_service = embedding_service
    
    async def process_query(
        self,
        query: str,
        top_k: int = 5,
        dataset_id: Optional[str] = None,
        use_reranking: bool = True
    ) -> Dict[str, Any]:
        """
        Process query through RAG pipeline
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            dataset_id: Optional dataset filter
            use_reranking: Whether to rerank results
            
        Returns:
            Dict with retrieved contexts and metadata
        """
        logger.info(f"Processing RAG query: '{query[:50]}...'")
        
        # Step 1: Retrieve relevant documents
        retrieved_docs = await self.retriever.retrieve(
            query=query,
            top_k=top_k * 2 if use_reranking else top_k,  # Get more for reranking
            dataset_id=dataset_id
        )
        
        if not retrieved_docs:
            logger.warning("No documents retrieved")
            return {
                'contexts': [],
                'sources': [],
                'total_retrieved': 0
            }
        
        # Step 2: Rerank if enabled
        if use_reranking and len(retrieved_docs) > top_k:
            logger.info(f"Reranking {len(retrieved_docs)} documents...")
            retrieved_docs = await self._rerank_documents(query, retrieved_docs, top_k)
        else:
            retrieved_docs = retrieved_docs[:top_k]
        
        # Step 3: Prepare context
        contexts = [doc['text'] for doc in retrieved_docs]
        
        # Step 4: Prepare sources/citations
        sources = []
        for i, doc in enumerate(retrieved_docs, 1):
            sources.append({
                'index': i,
                'segment_id': doc['segment_id'],
                'document_id': doc['document_id'],
                'score': doc['score'],
                'preview': doc['text'][:200] + '...' if len(doc['text']) > 200 else doc['text']
            })
        
        logger.info(f"RAG pipeline: Retrieved {len(contexts)} contexts")
        
        return {
            'contexts': contexts,
            'sources': sources,
            'total_retrieved': len(retrieved_docs),
            'query': query
        }
    
    async def _rerank_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents using cross-encoder or similarity
        
        For now, uses simple similarity reranking
        TODO: Add cross-encoder model for better reranking
        """
        # Simple reranking: already sorted by score from vector search
        # In production, use cross-encoder like ms-marco-MiniLM
        
        return documents[:top_k]
    
    def build_rag_prompt(
        self,
        query: str,
        contexts: List[str],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Build prompt with retrieved contexts
        
        Args:
            query: User query
            contexts: Retrieved contexts
            system_prompt: Optional system prompt
            
        Returns:
            Complete prompt for LLM
        """
        if not system_prompt:
            system_prompt = """أنت مساعد ذكي متخصص في الإجابة على الأسئلة بناءً على المستندات المقدمة.
قواعد الإجابة:
1. استخدم فقط المعلومات من السياق المقدم
2. إذا لم تجد الإجابة في السياق، قل "لا أجد معلومات كافية في المستندات المتاحة"
3. اذكر مصادر المعلومات عند الإمكان
4. كن دقيقاً ومختصراً
5. أجب باللغة العربية أو الإنجليزية حسب لغة السؤال"""
        
        # Build context section
        context_text = "\n\n".join([
            f"[مستند {i+1}]\n{context}"
            for i, context in enumerate(contexts)
        ])
        
        prompt = f"""{system_prompt}

السياق المتاح:
{context_text}

السؤال: {query}

الإجابة:"""
        
        return prompt
