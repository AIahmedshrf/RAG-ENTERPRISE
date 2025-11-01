"""
Embeddings Service using Azure OpenAI
"""
from typing import List, Union
import asyncio
import logging
from openai import AzureOpenAI

from core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate embeddings using Azure OpenAI"""
    
    def __init__(self):
        self.client = None
        self.model = settings.azure_openai.embedding_deployment
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Azure OpenAI client"""
        try:
            if not settings.azure_openai.api_key or not settings.azure_openai.api_base:
                logger.warning("Azure OpenAI credentials not configured - using mock embeddings")
                self.client = None
                return
            
            self.client = AzureOpenAI(
                api_key=settings.azure_openai.api_key,
                api_version=settings.azure_openai.api_version,
                azure_endpoint=settings.azure_openai.api_base
            )
            logger.info(f"EmbeddingService initialized with model: {self.model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            self.client = None
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        embeddings = await self.generate_embeddings([text])
        return embeddings[0]
    
    async def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 16
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts
            batch_size: Batch size for API calls
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Use mock embeddings if client not initialized
        if self.client is None:
            logger.warning("Using mock embeddings (1536 dimensions)")
            import numpy as np
            return [
                np.random.randn(1536).tolist()
                for _ in texts
            ]
        
        try:
            all_embeddings = []
            
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Call Azure OpenAI
                response = await asyncio.to_thread(
                    self.client.embeddings.create,
                    input=batch,
                    model=self.model
                )
                
                # Extract embeddings
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Generated {len(batch_embeddings)} embeddings (batch {i//batch_size + 1})")
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            # Fallback to mock
            import numpy as np
            return [np.random.randn(1536).tolist() for _ in texts]
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        return 1536  # text-embedding-ada-002 dimension


# Global instance
embedding_service = EmbeddingService()
