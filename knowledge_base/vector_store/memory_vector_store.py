"""
In-Memory Vector Store (للتطوير والاختبار)
"""
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import logging

from .base_vector_store import BaseVectorStore

logger = logging.getLogger(__name__)


class MemoryVectorStore(BaseVectorStore):
    """In-memory vector store using numpy for similarity search"""
    
    def __init__(self):
        self.vectors: List[np.ndarray] = []
        self.texts: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.ids: List[str] = []
        logger.info("MemoryVectorStore initialized")
    
    async def add_embeddings(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add embeddings to memory store"""
        
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in texts]
        
        # Convert to numpy arrays
        for i, (text, embedding, metadata, id_) in enumerate(zip(texts, embeddings, metadatas, ids)):
            self.vectors.append(np.array(embedding))
            self.texts.append(text)
            self.metadatas.append({
                **metadata,
                'added_at': datetime.utcnow().isoformat()
            })
            self.ids.append(id_)
        
        logger.info(f"Added {len(texts)} embeddings to memory store")
        return ids
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search using cosine similarity"""
        
        if not self.vectors:
            logger.warning("Vector store is empty")
            return []
        
        # Convert query to numpy
        query_vector = np.array(query_embedding)
        
        # Calculate cosine similarities
        similarities = []
        for i, vector in enumerate(self.vectors):
            # Apply filter if provided
            if filter:
                match = all(
                    self.metadatas[i].get(key) == value
                    for key, value in filter.items()
                )
                if not match:
                    continue
            
            # Cosine similarity
            similarity = np.dot(query_vector, vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(vector)
            )
            similarities.append((i, float(similarity)))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top k
        results = []
        for i, score in similarities[:top_k]:
            results.append({
                'id': self.ids[i],
                'text': self.texts[i],
                'metadata': self.metadatas[i],
                'score': score
            })
        
        logger.info(f"Search returned {len(results)} results")
        return results
    
    async def delete(self, ids: List[str]) -> bool:
        """Delete by IDs"""
        try:
            indices_to_remove = []
            for id_ in ids:
                if id_ in self.ids:
                    idx = self.ids.index(id_)
                    indices_to_remove.append(idx)
            
            # Remove in reverse order to maintain indices
            for idx in sorted(indices_to_remove, reverse=True):
                del self.vectors[idx]
                del self.texts[idx]
                del self.metadatas[idx]
                del self.ids[idx]
            
            logger.info(f"Deleted {len(indices_to_remove)} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return {
            'total_vectors': len(self.vectors),
            'vector_dimension': len(self.vectors[0]) if self.vectors else 0,
            'storage_type': 'memory'
        }
    
    def clear(self):
        """Clear all data"""
        self.vectors = []
        self.texts = []
        self.metadatas = []
        self.ids = []
        logger.info("Vector store cleared")
