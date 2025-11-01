"""
Base Vector Store Interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseVectorStore(ABC):
    """Abstract base class for vector stores"""
    
    @abstractmethod
    async def add_embeddings(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add embeddings to vector store
        
        Args:
            texts: List of text contents
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts
            ids: Optional list of IDs
            
        Returns:
            List of inserted IDs
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            filter: Optional metadata filter
            
        Returns:
            List of results with scores
        """
        pass
    
    @abstractmethod
    async def delete(self, ids: List[str]) -> bool:
        """Delete vectors by IDs"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        pass
