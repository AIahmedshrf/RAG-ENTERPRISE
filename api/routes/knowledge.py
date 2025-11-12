"""
Knowledge routes (skeleton)
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List
import os
from pathlib import Path
from sqlalchemy.orm import Session
from api.database import get_db
from api.models.document import Document, DocumentType, DocumentStatus
from api.services.document_processor import process_document
import time
from core.auth import get_current_user, get_current_active_user, get_current_admin_user

# jobs directory
JOBS_DIR = Path(os.getenv("JOBS_DIR", "./storage/jobs"))
JOBS_DIR.mkdir(parents=True, exist_ok=True)


def enqueue_job(document_id: str):
    """Create a job file for the worker to pick up"""
    fname = JOBS_DIR / f"{document_id}.job"
    with open(fname, "w") as f:
        f.write(str(time.time()))
    return str(fname)
from api.models.embedding import Embedding
from api.models.document import DocumentSegment
import json
import math


def _cosine(a, b):
    # a and b are lists of numbers
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

router = APIRouter()

STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "./storage/documents"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/search")
async def search(body: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Search the knowledge base using mock embeddings

    body: { q: string, dataset_id?: string, top_k?: int }
    """
    q = body.get('q', '')
    dataset_id = body.get('dataset_id')
    top_k = int(body.get('top_k', 5))

    if not q:
        return {"results": []}

    # generate query embedding using same mock function
    from api.services.document_processor import _mock_embedding

    qvec = _mock_embedding(q)

    # fetch all embeddings (optionally filter by dataset via segment->document)
    candidates = []
    query = db.query(Embedding, DocumentSegment).join(DocumentSegment, Embedding.segment_id == (DocumentSegment.document_id + ':' + DocumentSegment.position))
    # The above string join won't work in SQLAlchemy easily; instead fetch embeddings and segments separately
    all_embs = db.query(Embedding).all()
    for emb in all_embs:
        try:
            vec = json.loads(emb.vector)
        except Exception:
            continue
        score = _cosine(qvec, vec)
        # fetch segment
        seg_id = emb.segment_id
        if ':' in seg_id:
            doc_id, pos = seg_id.split(':', 1)
            seg = db.query(DocumentSegment).filter(DocumentSegment.document_id == doc_id, DocumentSegment.position == int(pos)).first()
            if seg:
                # if dataset_id provided, check document
                if dataset_id:
                    doc = db.query(Document).filter(Document.id == doc_id, Document.dataset_id == dataset_id).first()
                    if not doc:
                        continue
                candidates.append({
                    'document_id': doc_id,
                    'segment_id': seg_id,
                    'score': float(score),
                    'text_snippet': seg.content[:300]
                })

    candidates = sorted(candidates, key=lambda x: x['score'], reverse=True)[:top_k]
    return {'results': candidates}


@router.post("/documents/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    dataset_id: str = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Accept uploaded files and save them to storage (skeleton)

    Returns basic metadata for each uploaded file.
    """
    saved = []
    for f in files:
        try:
            target = STORAGE_DIR / f.filename
            with open(target, "wb") as out:
                content = await f.read()
                out.write(content)

            # Create DB record
            doc = Document(
                name=f.filename,
                type=DocumentType.TEXT,
                dataset_id=dataset_id or 'default',
                status=DocumentStatus.UPLOADING,
                file_path=str(target)
            )
            # set ownership
            try:
                doc.created_by = current_user.id
            except Exception:
                pass
            db.add(doc)
            db.commit()
            db.refresh(doc)

            # enqueue job for external worker
            enqueue_job(doc.id)
            # mark as queued
            doc.status = DocumentStatus.PROCESSING
            db.add(doc)
            db.commit()

            saved.append({"id": doc.id, "filename": f.filename, "path": str(target), "status": "saved"})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"files": saved, "dataset_id": dataset_id}


@router.get("/documents")
async def list_documents(db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    """Lightweight documents list for admin UI (admin only)"""
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    out = []
    for d in docs:
        out.append({
            'id': d.id,
            'name': d.name,
            'dataset_id': d.dataset_id,
            'status': str(d.status),
            'file_path': d.file_path
        })
    return {"documents": out}


@router.post("/reprocess/{document_id}")
async def reprocess_document(document_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    """Enqueue reprocessing for a document"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    enqueue_job(document_id)
    doc.status = DocumentStatus.PROCESSING
    db.add(doc)
    db.commit()
    return {"status": "requeued", "document_id": document_id}


@router.get("/jobs")
async def list_jobs(current_user=Depends(get_current_admin_user)):
    jobs = [p.name for p in JOBS_DIR.glob('*.job')]
    running = [p.name for p in JOBS_DIR.glob('*.running')]
    done = [p.name for p in JOBS_DIR.glob('*.done')]
    return {"queued": jobs, "running": running, "done": done}
