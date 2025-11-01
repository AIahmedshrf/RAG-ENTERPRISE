"""
PDF Document Parser
"""
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """Parse PDF files"""
    
    @staticmethod
    def parse(file_path: Path) -> Dict[str, Any]:
        """
        Parse PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dict with 'content' and 'metadata'
        """
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(str(file_path))
            
            # Extract text from all pages
            text_content = []
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append(text)
            
            content = '\n\n'.join(text_content)
            
            # Extract metadata
            metadata = {
                'page_count': len(reader.pages),
                'format': 'pdf'
            }
            
            # Add PDF metadata if available
            if reader.metadata:
                pdf_meta = reader.metadata
                metadata.update({
                    'title': pdf_meta.get('/Title', ''),
                    'author': pdf_meta.get('/Author', ''),
                    'subject': pdf_meta.get('/Subject', ''),
                    'creator': pdf_meta.get('/Creator', ''),
                })
            
            # Count words
            word_count = len(content.split())
            char_count = len(content)
            
            metadata['word_count'] = word_count
            metadata['character_count'] = char_count
            
            logger.info(f"Parsed PDF: {len(reader.pages)} pages, {word_count} words")
            
            return {
                'content': content,
                'metadata': metadata
            }
            
        except ImportError:
            logger.error("pypdf not installed. Install with: pip install pypdf")
            raise
        except Exception as e:
            logger.error(f"Error parsing PDF file: {e}")
            raise
