#!/usr/bin/env python3
"""
Simple file-based document worker.
Scans storage/jobs for .job files, renames to .running, processes the document, moves to .done on success.
"""
import time
from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.database import SessionLocal
from api.services.document_processor import process_document

JOBS_DIR = Path(os.getenv("JOBS_DIR", "./storage/jobs"))
JOBS_DIR.mkdir(parents=True, exist_ok=True)


def pick_jobs():
    return sorted(JOBS_DIR.glob('*.job'))


def run_once():
    jobs = pick_jobs()
    for job in jobs:
        doc_id = job.stem
        running = job.with_suffix('.running')
        done = job.with_suffix('.done')
        try:
            # atomically rename
            job.rename(running)
        except Exception:
            continue

        print(f"Processing job for document: {doc_id}")
        db = SessionLocal()
        try:
            ok = process_document(db, doc_id)
            db.close()
            if ok:
                running.rename(done)
                print(f"Done: {doc_id}")
            else:
                # failed, move back to .job for retry
                running.rename(job)
                print(f"Failed: {doc_id}, requeued")
        except Exception as e:
            print(f"Worker exception: {e}")
            try:
                running.rename(job)
            except Exception:
                pass


def loop(poll_interval=2):
    print("Document worker started, watching jobs in:", JOBS_DIR)
    while True:
        run_once()
        time.sleep(poll_interval)


if __name__ == '__main__':
    loop()
