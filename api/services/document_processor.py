"""
Simple Document Processor service
 - extract text (best-effort)
 - chunk text into segments
 - generate mock deterministic embedding per segment
 - persist DocumentSegment and Embedding
"""
from sqlalchemy.orm import Session
from api.models.document import Document, DocumentSegment, DocumentStatus
from api.models.embedding import Embedding
import json
import os
import hashlib
import uuid


def _read_text_from_file(path: str) -> str:
    # Best-effort: try to read as text, fallback to empty
    try:
        with open(path, 'rb') as f:
            data = f.read()
        try:
            return data.decode('utf-8')
        except Exception:
            return data.decode('latin-1', errors='ignore')
    except Exception:
        return ""


def _chunk_text(text: str, chunk_size: int = 800) -> list:
    # Paragraph-based chunking: split by double newlines, then ensure chunks are <= chunk_size
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []

    for p in paragraphs:
        if len(p) <= chunk_size:
            chunks.append(p)
        else:
            # split long paragraph into lines first
            lines = [l.strip() for l in p.split('\n') if l.strip()]
            cur = ''
            for line in lines:
                if len(cur) + 1 + len(line) <= chunk_size:
                    cur = (cur + '\n' + line).strip() if cur else line
                else:
                    if cur:
                        chunks.append(cur)
                    # if line itself is very long, split by characters
                    if len(line) > chunk_size:
                        pos = 0
                        while pos < len(line):
                            part = line[pos: pos + chunk_size]
                            chunks.append(part.strip())
                            pos += chunk_size
                        cur = ''
                    else:
                        cur = line
            if cur:
                chunks.append(cur)

    # Edge-case: if still empty, fallback to fixed size
    if not chunks and text:
        pos = 0
        while pos < len(text):
            part = text[pos: pos + chunk_size].strip()
            if part:
                chunks.append(part)
            pos += chunk_size

    return chunks


def _mock_embedding(text: str, dim: int = 32) -> list:
    # Deterministic pseudo-embedding using SHA256 -> numbers
    h = hashlib.sha256(text.encode('utf-8')).digest()
    vec = []
    for i in range(dim):
        byte = h[i % len(h)]
        vec.append((byte / 255.0) * 2 - 1)
    return vec


def process_document(db: Session, document_id: str):
    """Process a single document: extract, chunk, embed, persist segments and embeddings"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        return False

    try:
        doc.status = DocumentStatus.PROCESSING
        db.commit()

        text = _read_text_from_file(doc.file_path or '')
        chunks = _chunk_text(text)

        # clear existing segments for doc
        db.query(DocumentSegment).filter(DocumentSegment.document_id == document_id).delete()
        db.query(Embedding).filter(Embedding.segment_id.like(f"{document_id}:%")).delete()
        db.commit()

        for idx, chunk in enumerate(chunks):
            seg = DocumentSegment(
                id=str(uuid.uuid4()),
                document_id=document_id,
                position=idx,
                content=chunk,
                word_count=len(chunk.split())
            )
            db.add(seg)
            db.commit()
            db.refresh(seg)

            vec = _mock_embedding(chunk)
            emb = Embedding(segment_id=f"{document_id}:{seg.position}", vector=json.dumps(vec))
            db.add(emb)
            db.commit()

        doc.status = DocumentStatus.COMPLETED
        doc.word_count = len(text.split())
        db.commit()
        return True
    except Exception as e:
        doc.status = DocumentStatus.ERROR
        db.commit()
        return False
