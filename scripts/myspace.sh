#!/bin/bash
# ============================================
# Complete Storage Optimization Script
# ============================================

cd /workspaces/RAG-ENTERPRISE

echo "🚀 Starting complete storage optimization..."

# 1. Load environment variables
source .envrc

# 2. Create /tmp directories
mkdir -p /tmp/rag-enterprise/{venv,storage,logs,node_modules}
#المرحلة C: توجيه جميع الكاش إلى /tmp
echo ""
echo "3️⃣ توجيه جميع الكاش إلى /tmp..."

# إنشاء مجلدات الكاش
mkdir -p /tmp/cache/{pip,npm,huggingface,torch,transformers,matplotlib}



# Recreate Python venv

python3 -m venv /tmp/rag-enterprise/venv
ln -sfn /tmp/rag-enterprise/venv venv
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✅ Recreate Python venv and installed dependencies" 

# 4. Restore symbolic links
if [ ! -L "storage" ]; then
    ln -sfn /tmp/rag-enterprise/storage storage
fi

if [ ! -L "api.log" ]; then
    ln -sfn /tmp/rag-enterprise/logs/api.log api.log
fi


echo "📦 Installing frontend dependencies..."
cd frontend
ln -sfn /tmp/rag-enterprise/node_modules node_modules
npm install --quiet
cd ..
echo "✅ Frontend dependencies restored"




echo "✅ Optimization complete!"
