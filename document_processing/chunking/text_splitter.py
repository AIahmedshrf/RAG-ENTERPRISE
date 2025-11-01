"""
Text Splitting/Chunking with Arabic Support
"""
from typing import List
import logging

logger = logging.getLogger(__name__)


class TextSplitter:
    """Split text into chunks with overlap"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        """Initialize text splitter"""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.separators = separators or [
            "\n\n",
            "\n",
            ". ",
            "。",
            "؟ ",
            "! ",
            "؛ ",
            ", ",
            " ",
            ""
        ]
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        if not text or len(text) <= self.chunk_size:
            return [text] if text else []
        
        chunks = []
        current_chunk = ""
        
        splits = self._split_by_separators(text)
        
        for split in splits:
            if len(split) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                chunks.extend(self._force_split(split))
                continue
            
            if len(current_chunk) + len(split) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                if chunks and self.chunk_overlap > 0:
                    overlap = chunks[-1][-self.chunk_overlap:]
                    current_chunk = overlap + split
                else:
                    current_chunk = split
            else:
                current_chunk += split
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        chunks = [c for c in chunks if c.strip()]
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def _split_by_separators(self, text: str) -> List[str]:
        """Split text using separators"""
        for separator in self.separators:
            if separator == "":
                return list(text)
            
            if separator in text:
                return text.split(separator)
        
        return [text]
    
    def _force_split(self, text: str) -> List[str]:
        """Force split text that's too large"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end < len(text):
                for i in range(min(50, self.chunk_size // 4)):
                    if text[end - i] == ' ':
                        end = end - i
                        break
            
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
        
        return chunks
