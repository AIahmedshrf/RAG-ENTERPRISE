# document_processing/processors/base_processor.py
"""
المعالج الأساسي للمستندات - من aisearchmm
يوفر البنية الأساسية لجميع معالجات المستندات
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

from core.exceptions import DocumentProcessingError
from utilities.logger import logger


@dataclass
class DocumentMetadata:
    """البيانات الوصفية للمستند"""
    filename: str
    file_type: str
    file_size: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    language: Optional[str] = None
    page_count: Optional[int] = None
    author: Optional[str] = None
    title: Optional[str] = None
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            "filename": self.filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "created_at": self.created_at,
            "language": self.language,
            "page_count": self.page_count,
            "author": self.author,
            "title": self.title,
            **self.custom_metadata
        }


@dataclass
class ProcessedDocument:
    """المستند بعد المعالجة"""
    id: str
    content: str
    metadata: DocumentMetadata
    chunks: List[str] = field(default_factory=list)
    tables: List[Dict] = field(default_factory=list)
    images: List[Dict] = field(default_factory=list)
    entities: List[Dict] = field(default_factory=list)
    embeddings: Optional[List[float]] = None
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata.to_dict(),
            "chunks": self.chunks,
            "tables": self.tables,
            "images": self.images,
            "entities": self.entities,
            "has_embeddings": self.embeddings is not None
        }
    
    def get_summary(self) -> Dict:
        """ملخص المستند"""
        return {
            "id": self.id,
            "filename": self.metadata.filename,
            "type": self.metadata.file_type,
            "size": self.metadata.file_size,
            "language": self.metadata.language,
            "content_length": len(self.content),
            "chunks_count": len(self.chunks),
            "tables_count": len(self.tables),
            "images_count": len(self.images)
        }


class BaseDocumentProcessor(ABC):
    """
    المعالج الأساسي للمستندات
    جميع المعالجات المتخصصة ترث من هذا الصنف
    """
    
    def __init__(self):
        self.supported_formats: List[str] = []
        self.processor_name: str = self.__class__.__name__
        logger.info(f"Initialized {self.processor_name}")
    
    @abstractmethod
    async def process(self, file_path: str) -> ProcessedDocument:
        """
        معالجة المستند - يجب تنفيذها في الصنف الفرعي
        
        Args:
            file_path: مسار الملف
            
        Returns:
            ProcessedDocument: المستند المعالج
        """
        pass
    
    def can_process(self, file_path: str) -> bool:
        """
        التحقق من إمكانية معالجة الملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            bool: هل يمكن معالجة الملف
        """
        file_type = self._get_file_type(file_path)
        can = file_type in self.supported_formats
        
        if can:
            logger.debug(f"{self.processor_name} can process {file_type}")
        else:
            logger.debug(f"{self.processor_name} cannot process {file_type}")
        
        return can
    
    def _get_file_type(self, file_path: str) -> str:
        """
        الحصول على نوع الملف من الامتداد
        
        Args:
            file_path: مسار الملف
            
        Returns:
            str: نوع الملف
        """
        extension = Path(file_path).suffix.lower()
        
        type_mapping = {
            ".pdf": "pdf",
            ".docx": "docx",
            ".doc": "doc",
            ".xlsx": "xlsx",
            ".xls": "xls",
            ".pptx": "pptx",
            ".ppt": "ppt",
            ".txt": "txt",
            ".md": "markdown",
            ".html": "html",
            ".htm": "html"
        }
        
        return type_mapping.get(extension, "unknown")
    
    def _generate_document_id(self, file_path: str) -> str:
        """
        توليد معرف فريد للمستند
        
        Args:
            file_path: مسار الملف
            
        Returns:
            str: المعرف الفريد
        """
        # استخدام hash من اسم الملف + الوقت
        path = Path(file_path)
        content = f"{path.name}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _extract_metadata(self, file_path: str) -> DocumentMetadata:
        """
        استخراج البيانات الوصفية الأساسية
        
        Args:
            file_path: مسار الملف
            
        Returns:
            DocumentMetadata: البيانات الوصفية
        """
        path = Path(file_path)
        
        if not path.exists():
            raise DocumentProcessingError(
                f"File not found: {file_path}",
                {"file_path": file_path}
            )
        
        return DocumentMetadata(
            filename=path.name,
            file_type=self._get_file_type(file_path),
            file_size=path.stat().st_size
        )
    
    def _validate_file(self, file_path: str) -> None:
        """
        التحقق من صحة الملف
        
        Args:
            file_path: مسار الملف
            
        Raises:
            DocumentProcessingError: إذا كان الملف غير صالح
        """
        path = Path(file_path)
        
        # التحقق من وجود الملف
        if not path.exists():
            raise DocumentProcessingError(
                f"File does not exist: {file_path}",
                {"file_path": file_path}
            )
        
        # التحقق من أن الملف ليس مجلد
        if path.is_dir():
            raise DocumentProcessingError(
                f"Path is a directory, not a file: {file_path}",
                {"file_path": file_path}
            )
        
        # التحقق من حجم الملف (حد أقصى 100 ميجابايت)
        max_size = 100 * 1024 * 1024  # 100 MB
        file_size = path.stat().st_size
        
        if file_size > max_size:
            raise DocumentProcessingError(
                f"File too large: {file_size} bytes (max: {max_size} bytes)",
                {"file_path": file_path, "size": file_size}
            )
        
        # التحقق من أن الملف ليس فارغاً
        if file_size == 0:
            raise DocumentProcessingError(
                f"File is empty: {file_path}",
                {"file_path": file_path}
            )
        
        logger.debug(f"File validation passed: {file_path}")
    
    def _detect_language(self, text: str) -> Optional[str]:
        """
        كشف لغة النص
        
        Args:
            text: النص
            
        Returns:
            Optional[str]: رمز اللغة (ar, en, etc.) أو None
        """
        if not text or len(text.strip()) < 10:
            return None
        
        try:
            import langdetect
            lang = langdetect.detect(text[:1000])  # استخدام أول 1000 حرف
            logger.debug(f"Detected language: {lang}")
            return lang
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return None
    
    async def process_batch(self, file_paths: List[str]) -> List[ProcessedDocument]:
        """
        معالجة مجموعة من المستندات
        
        Args:
            file_paths: قائمة مسارات الملفات
            
        Returns:
            List[ProcessedDocument]: المستندات المعالجة
        """
        processed_docs = []
        
        for file_path in file_paths:
            try:
                logger.info(f"Processing {file_path}...")
                doc = await self.process(file_path)
                processed_docs.append(doc)
                logger.info(f"✅ Successfully processed {file_path}")
            except Exception as e:
                logger.error(f"❌ Failed to process {file_path}: {e}")
                # الاستمرار في معالجة باقي الملفات
                continue
        
        logger.info(f"Batch processing complete: {len(processed_docs)}/{len(file_paths)} successful")
        return processed_docs
    
    def get_stats(self) -> Dict:
        """
        الحصول على إحصائيات المعالج
        
        Returns:
            Dict: الإحصائيات
        """
        return {
            "processor_name": self.processor_name,
            "supported_formats": self.supported_formats
        }