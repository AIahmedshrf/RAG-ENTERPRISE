"""
Base Document Processor - Fixed
Handles document processing, chunking, and embedding
"""
import os
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import uuid

from api.models.document import Document
from api.models.document_segment import DocumentSegment


def process_document(document_id: str, file_path: str, file_type: str, db: Session) -> Dict[str, Any]:
    """
    Process a document:
    1. Extract text
    2. Chunk text
    3. Create segments
    4. Generate embeddings (mock for now)
    """
    try:
        # Step 1: Extract text
        text = extract_text(file_path, file_type)
        
        if not text:
            raise ValueError("No text extracted from document")
        
        # Step 2: Chunk text
        chunks = chunk_text(text)
        
        # Step 3: Create document segments
        segments_created = 0
        for i, chunk in enumerate(chunks):
            segment = DocumentSegment(
                id=str(uuid.uuid4()),
                document_id=document_id,
                content=chunk['text'],
                position=i,
                word_count=chunk['word_count'],
                char_count=len(chunk['text']),
                meta_data={"chunk_index": i, "source": "auto"}
            )
            db.add(segment)
            segments_created += 1
        
        db.commit()
        
        # Calculate stats
        word_count = sum(chunk['word_count'] for chunk in chunks)
        
        return {
            "success": True,
            "chunk_count": segments_created,
            "word_count": word_count,
            "total_chars": len(text)
        }
        
    except Exception as e:
        print(f"Document processing error: {e}")
        raise


def extract_text(file_path: str, file_type: str) -> str:
    """Extract text from different file types"""
    try:
        if file_type == '.txt' or file_type == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif file_type == '.pdf':
            return f"[PDF Content from {os.path.basename(file_path)}]\n\nThis is a mock extraction. Install PyPDF2 for real PDF processing."
        
        elif file_type in ['.docx', '.doc']:
            return f"[DOCX Content from {os.path.basename(file_path)}]\n\nThis is a mock extraction. Install python-docx for real DOCX processing."
        
        elif file_type == '.csv':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif file_type == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)
                return json.dumps(data, indent=2)
        
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
            
    except Exception as e:
        print(f"Text extraction error: {e}")
        raise ValueError(f"Failed to extract text: {str(e)}")


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """Chunk text into smaller pieces"""
    chunks = []
    sentences = text.split('. ')
    
    current_chunk = ""
    current_words = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        sentence_words = len(sentence.split())
        
        if current_words + sentence_words > chunk_size and current_chunk:
            chunks.append({
                'text': current_chunk.strip(),
                'word_count': current_words
            })
            
            if overlap > 0:
                words = current_chunk.split()
                overlap_words = words[-min(overlap, len(words)):]
                current_chunk = ' '.join(overlap_words) + '. ' + sentence + '. '
                current_words = len(overlap_words) + sentence_words
            else:
                current_chunk = sentence + '. '
                current_words = sentence_words
        else:
            current_chunk += sentence + '. '
            current_words += sentence_words
    
    if current_chunk:
        chunks.append({
            'text': current_chunk.strip(),
            'word_count': current_words
        })
    
    return chunks if chunks else [{'text': text, 'word_count': len(text.split())}]
