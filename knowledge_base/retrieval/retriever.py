"""
Document Retrieval Service
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

from api.models import DocumentSegment, Dataset
from knowledge_base.vector_store.memory_vector_store import MemoryVectorStore
from knowledge_base.embeddings.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Retrieve relevant document segments"""
    
    def __init__(self, db: Session):
        self.db = db
        self.vector_store = MemoryVectorStore()
        self.embedding_service = embedding_service
    
    async def index_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Index all segments from a dataset into vector store
        
        Args:
            dataset_id: Dataset ID to index
            
        Returns:
            Statistics about indexing
        """
        logger.info(f"Indexing dataset: {dataset_id}")
        
        # Get all segments from dataset
        segments = self.db.query(DocumentSegment).filter(
            DocumentSegment.dataset_id == dataset_id,
            DocumentSegment.enabled == True
        ).all()
        
        if not segments:
            logger.warning(f"No segments found for dataset {dataset_id}")
            return {'indexed': 0, 'dataset_id': dataset_id}
        
        # Prepare data
        texts = [seg.content for seg in segments]
        ids = [seg.id for seg in segments]
        metadatas = [
            {
                'segment_id': seg.id,
                'document_id': seg.document_id,
                'dataset_id': seg.dataset_id,
                'position': seg.position,
                'word_count': seg.word_count
            }
            for seg in segments
        ]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} segments...")
        embeddings = await self.embedding_service.generate_embeddings(texts)
        
        # Add to vector store
        logger.info(f"Adding to vector store...")
        await self.vector_store.add_embeddings(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"✅ Indexed {len(segments)} segments from dataset {dataset_id}")
        
        return {
            'indexed': len(segments),
            'dataset_id': dataset_id,
            'vector_dimension': self.embedding_service.get_embedding_dimension()
        }
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        dataset_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant segments for query
        
        Args:
            query: Search query
            top_k: Number of results
            dataset_id: Optional dataset filter
            
        Returns:
            List of relevant segments with scores
        """
        logger.info(f"Retrieving for query: '{query[:50]}...'")
        
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding(query)
        
        # Build filter
        filter_dict = {}
        if dataset_id:
            filter_dict['dataset_id'] = dataset_id
        
        # Search
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter=filter_dict if filter_dict else None
        )
        
        # Enrich with document info
        enriched_results = []
        for result in results:
            # Get segment from DB for full info
            segment_id = result['metadata']['segment_id']
            segment = self.db.query(DocumentSegment).filter(
                DocumentSegment.id == segment_id
            ).first()
            
            if segment:
                enriched_results.append({
                    'text': result['text'],
                    'score': result['score'],
                    'segment_id': segment.id,
                    'document_id': segment.document_id,
                    'dataset_id': segment.dataset_id,
                    'position': segment.position,
                    'metadata': segment.meta
                })
        
        logger.info(f"Retrieved {len(enriched_results)} relevant segments")
        return enriched_results
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics"""
        vector_stats = await self.vector_store.get_stats()
        
        total_segments = self.db.query(DocumentSegment).count()
        enabled_segments = self.db.query(DocumentSegment).filter(
            DocumentSegment.enabled == True
        ).count()
        
        return {
            'total_segments_in_db': total_segments,
            'enabled_segments': enabled_segments,
            'vector_store': vector_stats
        }
