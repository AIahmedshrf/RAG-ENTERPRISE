# Knowledge Base MVP Plan

This document describes the immediate MVP plan implemented in the repository and next steps to evolve a production-grade Knowledge Base and Agents Management system.

## Summary of work done (so far)
- Added API skeletons for `knowledge` and `agents` routes. (`/knowledge/*`, `/agents/*`)
- Added Embedding model and document processing service that performs: text extraction (best-effort), chunking, deterministic mock embeddings, and persistence.
- Wired `POST /knowledge/documents/upload` to create `Document` records and enqueue background processing.
- Implemented `POST /knowledge/search` that performs cosine similarity against stored mock embeddings.
- Added frontend pages to test and interact with the new endpoints:
  - `/admin/knowledge` — Knowledge Explorer (search)
  - `/admin/knowledge/upload` — Upload Documents
  - `/admin/knowledge/docs` — Documents list
  - `/admin/agents` — Agents list (CRUD skeleton exists via API)

## Goals for MVP
- Users can upload documents and the backend will process them into searchable segments.
- A basic search endpoint returns relevant segments.
- Admin UI pages allow uploading, listing, and searching documents.

## Architecture (MVP)
- FastAPI backend
  - `knowledge` routes: upload, list, search
  - `document_processor` service: runs in background (currently BackgroundTasks) to process documents
  - Embeddings persisted in `embeddings` table (JSON-encoded vectors)
- SQLite (dev) stores documents, segments, embeddings
- Next.js frontend pages under `frontend/app/admin/knowledge/`

## API Contracts (Implemented)

- POST /knowledge/documents/upload
  - multipart/form-data: files[], dataset_id
  - Response: { files: [{ id, filename, path, status }], dataset_id }

- GET /knowledge/documents
  - Response: { documents: [{ id, name, dataset_id, status, file_path }] }

- POST /knowledge/search
  - JSON body: { q: string, dataset_id?: string, top_k?: int }
  - Response: { results: [{ document_id, segment_id, score, text_snippet }] }

- /agents (CRUD skeleton)

## How processing works (current implementation)
1. File saved to `storage/documents/<filename>`.
2. `Document` DB record created with status `UPLOADING`.
3. Background task `process_document` reads the file as text (best-effort), splits into fixed-size chunks (800 chars), and persisits `DocumentSegment` rows.
4. For each segment a deterministic pseudo-embedding is created by hashing the text and converting bytes into floats. These vectors are stored in `embeddings.vector` as JSON.
5. Document status is updated to `COMPLETED`.

## How to test locally
1. Start backend and frontend (if not already running):

```bash
# Backend
./start_api.sh

# Frontend (inside /workspaces/RAG-ENTERPRISE/frontend)
npm run dev
```

2. Upload a file (example):

```bash
curl -s -X POST http://localhost:8000/knowledge/documents/upload \
  -F "files=@/path/to/file.pdf" -F "dataset_id=demo" | jq .
```

3. Query search (after processing completes):

```bash
curl -s -X POST http://localhost:8000/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"q":"your query", "top_k":5}' | jq .
```

4. Use the frontend pages:
  - http://localhost:3000/admin/knowledge (search)
  - http://localhost:3000/admin/knowledge/upload (upload)
  - http://localhost:3000/admin/knowledge/docs (list documents)

## Next steps (near-term roadmap)

Phase 1 — Stabilize MVP (next 2–3 days)
- Replace mock embeddings with real embeddings (OpenAI/Azure) behind an adapter.
- Use a background task queue (Redis + RQ or Celery) for robust processing and retries.
- Add robust text extraction (PDF/Tika integration) and better chunking (token-based).
- Persist segment embeddings as typed arrays (or integrate FAISS/Weaviate) for efficient retrieval.

Phase 2 — Agents & RAG (3–7 days)
- Implement `/agents` backend with DB model and secure CRUD.
- Implement agent runner that composes retrieval + prompt templates + LLM calls.
- Wire agent selection in chat UI and enable agent-specific retrieval.

Phase 3 — Ops and UX polish (3–5 days)
- Monitoring, retries, reindex endpoints, DB backup UI.
- Admin UI polish: vector visualization, preview, filter by dataset.
- i18n and RTL improvements for Arabic UX.

## Notes and caveats
- Current implementation is intended as a skeleton and demo. It is not production-ready (no ACL checks on knowledge endpoints, embeddings are mock, processing runs in BackgroundTasks without queue).
- Before using real embedding providers, secure secrets and implement usage limits.

If you want, I can now: (choose or I'll proceed with the first by default)
- Implement real embeddings adapter using OpenAI (requires API key in env).
- Swap BackgroundTasks with RQ (Redis) and create worker script.
- Harden endpoints with authentication and per-tenant isolation.
