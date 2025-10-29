# api/routes/documents.py
"""Endpoints لإدارة المستندات - محدث مع الفهرسة"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Optional
from pathlib import Path
import os

from document_processing.processors.general_processor import GeneralDocumentProcessor
from knowledge_base.vector_store.embeddings import EmbeddingsGenerator
from knowledge_base.vector_store.memory_store import MemoryVectorStore
from utilities.helpers import (
    sanitize_filename, ensure_directory, save_upload_file,
    format_file_size, get_file_extension
)
from utilities.logger import logger
from core.exceptions import DocumentProcessingError

router = APIRouter(prefix="/documents", tags=["Documents"])

# المعالج والمخزن (مشترك مع chat)
processor = GeneralDocumentProcessor()
embeddings = EmbeddingsGenerator()
vector_store = MemoryVectorStore()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    index_name: str = Form("general")
):
    """
    رفع ومعالجة وفهرسة مستند
    
    التحديث الجديد:
    - يقوم بفهرسة المستند تلقائياً في vector store
    - جاهز للبحث والمحادثة فوراً
    """
    logger.info(f"Upload + Index request: {file.filename}")
    
    try:
        # 1. التحقق من نوع الملف
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
        
        # 2. حفظ الملف
        safe_filename = sanitize_filename(file.filename)
        upload_dir = ensure_directory("data/documents")
        file_path = upload_dir / safe_filename
        
        counter = 1
        original_path = file_path
        while file_path.exists():
            name = original_path.stem
            ext = original_path.suffix
            file_path = upload_dir / f"{name}_{counter}{ext}"
            counter += 1
        
        saved_path = await save_upload_file(file, str(file_path))
        
        # 3. معالجة المستند
        logger.info("Processing document...")
        processed_doc = await processor.process(saved_path)
        
        # 4. فهرسة في vector store (الجديد!)
        logger.info("Indexing document chunks...")
        indexed_count = 0
        
        for i, chunk in enumerate(processed_doc.chunks):
            try:
                # توليد embedding للقطعة
                chunk_embedding = await embeddings.generate(chunk)
                
                # إضافة للمخزن
                await vector_store.add_document(
                    doc_id=f"{processed_doc.id}_chunk_{i}",
                    content=chunk,
                    embedding=chunk_embedding,
                    metadata={
                        "document_id": processed_doc.id,
                        "filename": processed_doc.metadata.filename,
                        "chunk_index": i,
                        "total_chunks": len(processed_doc.chunks),
                        "language": processed_doc.metadata.language or language,
                        "file_type": processed_doc.metadata.file_type
                    },
                    index_name=index_name
                )
                indexed_count += 1
            
            except Exception as e:
                logger.warning(f"Failed to index chunk {i}: {e}")
        
        logger.info(f"✅ Indexed {indexed_count}/{len(processed_doc.chunks)} chunks")
        
        # 5. إحصائيات المخزن
        store_stats = vector_store.get_stats()
        
        # 6. إعداد النتيجة
        result = {
            "success": True,
            "message": "Document uploaded, processed, and indexed successfully",
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
                "indexed_chunks": indexed_count,
                "tables_count": len(processed_doc.tables),
                "images_count": len(processed_doc.images),
                "created_at": processed_doc.metadata.created_at
            },
            "indexing": {
                "index_name": index_name,
                "chunks_indexed": indexed_count,
                "status": "ready_for_search"
            },
            "vector_store_stats": store_stats,
            "preview": processed_doc.content[:300] + "..." if len(processed_doc.content) > 300 else processed_doc.content
        }
        
        logger.info(f"✅ Complete: {processed_doc.id} → {indexed_count} chunks indexed")
        return result
    
    except DocumentProcessingError as e:
        logger.error(f"Document processing error: {e.message}")
        raise HTTPException(status_code=400, detail={
            "error": "DocumentProcessingError",
            "message": e.message,
            "details": e.details
        })
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        if 'saved_path' in locals() and os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(status_code=500, detail={
            "error": "InternalServerError",
            "message": "Failed to process document"
        })


@router.get("/supported-formats")
async def get_supported_formats():
    """الصيغ المدعومة"""
    return {
        "supported_formats": processor.supported_formats,
        "processor": processor.processor_name
    }


@router.get("/stats")
async def get_stats():
    """إحصائيات المستندات والفهرسة"""
    return {
        "vector_store": vector_store.get_stats(),
        "processor": {
            "name": processor.processor_name,
            "supported_formats": processor.supported_formats
        }
    }


# تصدير للاستخدام في chat
def get_vector_store():
    """للوصول من chat.py"""
    return vector_store

def get_embeddings():
    """للوصول من chat.py"""
    return embeddings