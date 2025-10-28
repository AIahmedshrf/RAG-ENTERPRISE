# setup_project.py - النسخة المبسطة الجاهزة
#!/usr/bin/env python3
import os
from pathlib import Path

base = Path("/workspaces/RAG-ENTERPRISE")

# المجلدات
folders = [
    "core", "document_processing/processors", "document_processing/parsers",
    "document_processing/chunking", "knowledge_base/vector_store",
    "knowledge_base/graph_store", "knowledge_base/retrieval",
    "agents/general", "agents/financial", "agents/investment", "agents/research",
    "financial/analysis", "financial/portfolio", "financial/risk", "financial/market",
    "orchestration/patterns", "orchestration/workflow",
    "api/routes", "api/models", "api/middleware",
    "utilities", "web/static/css", "web/static/js", "web/static/images",
    "web/templates", "tests/unit", "tests/integration", "tests/e2e",
    "scripts", "docs", "config", "logs", "data/documents", "data/indexes", "data/temp"
]

print("إنشاء المجلدات...")
for folder in folders:
    (base / folder).mkdir(parents=True, exist_ok=True)
    (base / folder / "__init__.py").touch(exist_ok=True)
    print(f"✓ {folder}")

# الملفات الجذرية
files = {
    ".gitignore": "*.pyc\n__pycache__/\nvenv/\n.env\nlogs/\ndata/",
    "requirements.txt": "fastapi==0.109.0\nuvicorn==0.27.0\nazure-search-documents==11.4.0\nopenai==1.12.0",
    "README.md": "# RAG-ENTERPRISE\n\nنظام ذكاء اصطناعي متكامل",
    ".env.example": "AZURE_OPENAI_KEY=your-key\nAZURE_SEARCH_KEY=your-key"
}

print("\nإنشاء الملفات الجذرية...")
for name, content in files.items():
    (base / name).write_text(content)
    print(f"✓ {name}")

print("\n✅ تم الإنشاء بنجاح!")
print("الخطوات التالية:")
print("1. cd /workspaces/RAG-ENTERPRISE")
print("2. python -m venv venv")
print("3. source venv/bin/activate")