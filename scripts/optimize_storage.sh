#!/bin/bash
# ============================================
# Complete Storage Optimization Script
# ============================================

cd /workspaces/RAG-ENTERPRISE

echo "🚀 Starting complete storage optimization..."

# Stop API
./stop_api.sh 2>/dev/null || true

# Create /tmp structure
mkdir -p /tmp/rag-enterprise/{venv,storage,logs,node_modules}
mkdir -p /tmp/cache/{pip,npm,huggingface,torch,transformers}

# Move venv
if [ -d "venv" ] && [ ! -L "venv" ]; then
    source venv/bin/activate
    pip freeze > requirements_frozen.txt
    deactivate
    rm -rf venv
fi

python3 -m venv /tmp/rag-enterprise/venv
ln -sfn /tmp/rag-enterprise/venv venv
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Move node_modules
if [ -d "frontend/node_modules" ] && [ ! -L "frontend/node_modules" ]; then
    rm -rf frontend/node_modules
fi
cd frontend && ln -sfn /tmp/rag-enterprise/node_modules node_modules && cd ..

# Create .envrc
source .envrc 2>/dev/null || true

# Cleanup
pip cache purge 2>/dev/null || true
npm cache clean --force 2>/dev/null || true
find . -type d -name __pycache__ -delete 2>/dev/null || true

echo "✅ Optimization complete!"
df -h | grep -E "/workspaces|/tmp"
