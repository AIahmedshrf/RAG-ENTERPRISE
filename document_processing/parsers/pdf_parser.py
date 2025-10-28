# document_processing/parsers/pdf_parser.py
"""
محلل ملفات PDF - من aisearchmm
يدعم استخراج النصوص والجداول والصور
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
import io

try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

from core.exceptions import DocumentProcessingError
from utilities.logger import logger


class PDFParser:
    """محلل ملفات PDF"""
    
    def __init__(self):
        if not HAS_PYPDF2:
            logger.warning("PyPDF2 not installed. PDF parsing will be limited.")
        
        self.parser_name = "PDFParser"
        logger.info(f"Initialized {self.parser_name}")
    
    def parse(self, file_path: str) -> Dict:
        """
        تحليل ملف PDF
        
        Args:
            file_path: مسار ملف PDF
            
        Returns:
            Dict: محتوى PDF المستخرج
        """
        if not HAS_PYPDF2:
            raise DocumentProcessingError(
                "PyPDF2 is required for PDF parsing. Install it with: pip install PyPDF2",
                {"file_path": file_path}
            )
        
        logger.info(f"Parsing PDF: {file_path}")
        
        try:
            result = {
                "text": "",
                "pages": [],
                "metadata": {},
                "page_count": 0
            }
            
            # فتح وقراءة PDF
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # عدد الصفحات
                result["page_count"] = len(pdf_reader.pages)
                logger.debug(f"PDF has {result['page_count']} pages")
                
                # استخراج البيانات الوصفية
                if pdf_reader.metadata:
                    result["metadata"] = {
                        "title": pdf_reader.metadata.get('/Title', ''),
                        "author": pdf_reader.metadata.get('/Author', ''),
                        "subject": pdf_reader.metadata.get('/Subject', ''),
                        "creator": pdf_reader.metadata.get('/Creator', ''),
                        "producer": pdf_reader.metadata.get('/Producer', ''),
                    }
                
                # استخراج النص من كل صفحة
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        
                        if page_text:
                            page_text = page_text.strip()
                            result["text"] += page_text + "\n\n"
                            result["pages"].append({
                                "page_number": page_num,
                                "text": page_text,
                                "char_count": len(page_text)
                            })
                            
                            logger.debug(f"Extracted {len(page_text)} chars from page {page_num}")
                    
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num}: {e}")
                        result["pages"].append({
                            "page_number": page_num,
                            "text": "",
                            "error": str(e)
                        })
            
            result["text"] = result["text"].strip()
            
            logger.info(f"✅ PDF parsed successfully: {len(result['text'])} total chars, {result['page_count']} pages")
            return result
        
        except Exception as e:
            logger.error(f"❌ Failed to parse PDF {file_path}: {e}")
            raise DocumentProcessingError(
                f"Failed to parse PDF: {str(e)}",
                {"file_path": file_path}
            )
    
    def extract_page(self, file_path: str, page_number: int) -> str:
        """
        استخراج صفحة محددة
        
        Args:
            file_path: مسار PDF
            page_number: رقم الصفحة (يبدأ من 1)
            
        Returns:
            str: نص الصفحة
        """
        if not HAS_PYPDF2:
            raise DocumentProcessingError("PyPDF2 is required")
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                if page_number < 1 or page_number > len(pdf_reader.pages):
                    raise ValueError(f"Page number {page_number} out of range (1-{len(pdf_reader.pages)})")
                
                page = pdf_reader.pages[page_number - 1]
                return page.extract_text()
        
        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to extract page {page_number}: {str(e)}",
                {"file_path": file_path, "page_number": page_number}
            )
    
    def get_page_count(self, file_path: str) -> int:
        """
        الحصول على عدد الصفحات
        
        Args:
            file_path: مسار PDF
            
        Returns:
            int: عدد الصفحات
        """
        if not HAS_PYPDF2:
            raise DocumentProcessingError("PyPDF2 is required")
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                return len(pdf_reader.pages)
        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to get page count: {str(e)}",
                {"file_path": file_path}
            )