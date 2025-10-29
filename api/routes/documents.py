# api/routes/documents.py
"""
Endpoints لإدارة المستندات
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Optional
from pathlib import Path
import os

from document_processing.processors.general_processor import GeneralDocumentProcessor
from utilities.helpers import (
    sanitize_filename, 
    ensure_directory, 
    save_upload_file,
    format_file_size,
    get_file_extension
)
from utilities.logger import logger
from core.exceptions import DocumentProcessingError

router = APIRouter(prefix="/documents", tags=["Documents"])

# إنشاء معالج المستندات
processor = GeneralDocumentProcessor()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    """
    رفع ومعالجة مستند
    
    Args:
        file: الملف المرفوع
        language: اللغة (اختياري)
        
    Returns:
        dict: معلومات المستند المعالج
    """
    logger.info(f"Received upload request: {file.filename}")
    
    try:
        # التحقق من نوع الملف
        file_ext = get_file_extension(file.filename)
        
        if file_ext not in processor.supported_formats:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "UnsupportedFileFormat",
                    "message": f"File format .{file_ext} is not supported",
                    "supported_formats": processor.supported_formats
                }
            )
        
        # تنظيف اسم الملف
        safe_filename = sanitize_filename(file.filename)
        
        # مسار الحفظ
        upload_dir = ensure_directory("data/documents")
        file_path = upload_dir / safe_filename
        
        # إذا كان الملف موجود، إضافة رقم
        counter = 1
        original_path = file_path
        while file_path.exists():
            name = original_path.stem
            ext = original_path.suffix
            file_path = upload_dir / f"{name}_{counter}{ext}"
            counter += 1
        
        # حفظ الملف
        saved_path = await save_upload_file(file, str(file_path))
        logger.info(f"File saved to: {saved_path}")
        
        # معالجة المستند
        logger.info("Processing document...")
        processed_doc = await processor.process(saved_path)
        
        # إعداد النتيجة
        result = {
            "success": True,
            "document": {
                "id": processed_doc.id,
                "filename": processed_doc.metadata.filename,
                "file_type": processed_doc.metadata.file_type,
                "file_size": processed_doc.metadata.file_size,
                "file_size_formatted": format_file_size(processed_doc.metadata.file_size),
                "language": processed_doc.metadata.language or language,
                "page_count": processed_doc.metadata.page_count,
                "content_length": len(processed_doc.content),
                "chunks_count": len(processed_doc.chunks),
                "tables_count": len(processed_doc.tables),
                "images_count": len(processed_doc.images),
                "created_at": processed_doc.metadata.created_at
            },
            "summary": processed_doc.get_summary(),
            "preview": processed_doc.content[:500] + "..." if len(processed_doc.content) > 500 else processed_doc.content
        }
        
        logger.info(f"✅ Document processed successfully: {processed_doc.id}")
        return result
    
    except DocumentProcessingError as e:
        logger.error(f"Document processing error: {e.message}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "DocumentProcessingError",
                "message": e.message,
                "details": e.details
            }
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}", exc_info=True)
        
        # حذف الملف في حالة الفشل
        if 'saved_path' in locals() and os.path.exists(saved_path):
            os.remove(saved_path)
            logger.info(f"Removed failed upload: {saved_path}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "InternalServerError",
                "message": "Failed to process document"
            }
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """الحصول على قائمة الصيغ المدعومة"""
    return {
        "supported_formats": processor.supported_formats,
        "processor": processor.processor_name
    }