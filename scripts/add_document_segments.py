"""
Add document_segments table
"""
import sys
sys.path.insert(0, '/workspaces/RAG-ENTERPRISE')

from sqlalchemy import create_engine, text
from core.config import settings

engine = create_engine(settings.database_url)

# Create document_segments table
create_table_sql = """
CREATE TABLE IF NOT EXISTS document_segments (
    id VARCHAR PRIMARY KEY,
    document_id VARCHAR NOT NULL,
    content TEXT NOT NULL,
    position INTEGER NOT NULL,
    word_count INTEGER DEFAULT 0,
    char_count INTEGER DEFAULT 0,
    embedding JSON,
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);
"""

try:
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
        print("✅ document_segments table created successfully")
except Exception as e:
    print(f"Error: {e}")
