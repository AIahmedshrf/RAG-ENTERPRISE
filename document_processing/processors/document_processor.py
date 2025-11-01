"""
Document Processing Service
"""
from pathlib import Path
from typing import Dict, Any
from sqlalchemy.orm import Session
import logging

from api.models import Document, DocumentSegment, DocumentStatus, DocumentType
from document_processing.parsers.text_parser import TextParser, MarkdownParser, CSVParser
from document_processing.parsers.pdf_parser import PDFParser
from document_processing.parsers.docx_parser import DOCXParser
from document_processing.chunking.text_splitter import TextSplitter
from utilities.storage import storage_manager

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process documents: parse, chunk, and store"""
    
    PARSERS = {
        DocumentType.TEXT: TextParser,
        DocumentType.MARKDOWN: MarkdownParser,
        DocumentType.CSV: CSVParser,
        DocumentType.PDF: PDFParser,
        DocumentType.DOCX: DOCXParser,
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.text_splitter = TextSplitter()
    
    def process_document(self, document_id: str) -> bool:
        """Process a document: parse, chunk, and store segments"""
        try:
            document = self.db.query(Document).filter(Document.id == document_id).first()
            
            if not document:
                logger.error(f"Document not found: {document_id}")
                return False
            
            document.status = DocumentStatus.PARSING
            self.db.commit()
            
            file_path = storage_manager.get_file_path(document.file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            logger.info(f"Parsing document: {document.name} (type: {document.file_type})")
            parsed_data = self._parse_document(document.file_type, file_path)
            
            document.status = DocumentStatus.SPLITTING
            document.word_count = parsed_data['metadata'].get('word_count', 0)
            document.character_count = parsed_data['metadata'].get('character_count', 0)
            document.meta = parsed_data['metadata']
            self.db.commit()
            
            logger.info(f"Splitting document into chunks: {document.name}")
            chunks = self.text_splitter.split_text(parsed_data['content'])
            
            document.status = DocumentStatus.INDEXING
            self.db.commit()
            
            logger.info(f"Creating {len(chunks)} segments for document: {document.name}")
            for i, chunk in enumerate(chunks):
                segment = DocumentSegment(
                    document_id=document.id,
                    dataset_id=document.dataset_id,
                    position=i,
                    content=chunk,
                    word_count=len(chunk.split()),
                    character_count=len(chunk),
                    status='completed',
                    enabled=True
                )
                self.db.add(segment)
            
            document.segment_count = len(chunks)
            document.status = DocumentStatus.COMPLETED
            self.db.commit()
            
            logger.info(f"✅ Document processed: {document.name} ({len(chunks)} segments)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing document {document_id}: {e}")
            
            if document:
                document.status = DocumentStatus.ERROR
                document.error_message = str(e)
                self.db.commit()
            
            return False
    
    def _parse_document(self, file_type: DocumentType, file_path: Path) -> Dict[str, Any]:
        """Parse document based on type"""
        parser_class = self.PARSERS.get(file_type)
        
        if not parser_class:
            raise ValueError(f"No parser available for type: {file_type}")
        
        return parser_class.parse(file_path)
