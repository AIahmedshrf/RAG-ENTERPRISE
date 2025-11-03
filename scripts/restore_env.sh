#!/bin/bash
# ============================================
# Restore Environment Script
# للاستخدام بعد restart الـ Codespace
# ============================================

cd /workspaces/RAG-ENTERPRISE

echo "🔄 Restoring environment..."

# 1. Load environment variables
source .envrc

# 2. Create /tmp directories
mkdir -p /tmp/rag-enterprise/{venv,storage,logs,node_modules}
mkdir -p /tmp/cache/{pip,npm,huggingface,torch,transformers}

# 3. Recreate Python venv
if [ ! -d "venv" ] || [ ! -L "venv" ]; then
    echo "📦 Creating Python venv..."
    python3 -m venv /tmp/rag-enterprise/venv
    ln -sfn /tmp/rag-enterprise/venv venv
    
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo "✅ Python venv restored"
fi

# 4. Restore symbolic links
if [ ! -L "storage" ]; then
    ln -sfn /tmp/rag-enterprise/storage storage
fi

if [ ! -L "api.log" ]; then
    ln -sfn /tmp/rag-enterprise/logs/api.log api.log
fi

# 5. Frontend node_modules
if [ -f "frontend/package.json" ] && [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    ln -sfn /tmp/rag-enterprise/node_modules node_modules
    npm install --quiet
    cd ..
    echo "✅ Frontend dependencies restored"
fi

# 6. Initialize database
if [ ! -f "rag_enterprise.db" ]; then
    echo "🗄️  Initializing database..."
    python scripts/init_db.py
fi

echo ""
echo "✅ Environment restored successfully!"
echo ""
echo "🚀 To start API: ./start_api.sh"