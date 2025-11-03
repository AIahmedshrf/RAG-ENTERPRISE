#🚀 خطة التحسين الشاملة
# المرحلة A: نقل البيئة الافتراضية إلى /tmp

cd /workspaces/RAG-ENTERPRISE

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🚀 Storage Optimization - Complete Strategy              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 1. قياس المساحة الحالية
echo "📊 المساحة قبل التحسين:"
du -sh /workspaces/RAG-ENTERPRISE/{venv,frontend/node_modules} 2>/dev/null
df -h | grep -E "Filesystem|/workspaces"

echo ""
echo "⏳ بدء التحسين..."

# 2. إيقاف API
./stop_api.sh 2>/dev/null || kill $(cat api.pid) 2>/dev/null || true

# 3. نسخ venv الحالي إلى /tmp (للحفاظ على الحزم المثبتة)
echo ""
echo "1️⃣ نقل Python venv إلى /tmp..."

if [ -d "venv" ]; then
    # حفظ requirements أولاً
    source venv/bin/activate
    pip freeze > requirements_frozen.txt
    deactivate
    
    # حذف venv القديم
    rm -rf venv
fi

# إنشاء venv جديد في /tmp
python3 -m venv /tmp/rag-enterprise/venv

# إنشاء symbolic link
ln -sfn /tmp/rag-enterprise/venv venv

echo "✅ venv -> /tmp/rag-enterprise/venv"

# تفعيل البيئة الجديدة
source venv/bin/activate

# إعادة تثبيت الحزم بسرعة
echo "📦 إعادة تثبيت الحزم..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✅ Python environment في /tmp"

#المرحلة B: نقل node_modules إلى /tmp

echo ""
echo "2️⃣ نقل node_modules إلى /tmp..."

if [ -d "frontend/node_modules" ]; then
    # حذف node_modules القديم
    rm -rf frontend/node_modules
fi

# إنشاء في /tmp
mkdir -p /tmp/rag-enterprise/node_modules

# إنشاء symbolic link
cd frontend
ln -sfn /tmp/rag-enterprise/node_modules node_modules
cd ..

echo "✅ node_modules -> /tmp/rag-enterprise/node_modules"

# إعادة تثبيت (إذا كان package.json موجود)
if [ -f "frontend/package.json" ]; then
    echo "📦 npm install..."
    cd frontend
    npm install --quiet 2>/dev/null || true
    cd ..
fi

#المرحلة C: توجيه جميع الكاش إلى /tmp
echo ""
echo "3️⃣ توجيه جميع الكاش إلى /tmp..."

# إنشاء مجلدات الكاش
mkdir -p /tmp/cache/{pip,npm,huggingface,torch,transformers,matplotlib}

# إنشاء ملف بيئة
cat > /workspaces/RAG-ENTERPRISE/.envrc << 'ENVEOF'
# ==============================================
# Environment Variables for /tmp optimization
# ==============================================

# General
export TMPDIR=/tmp
export TEMP=/tmp
export TMP=/tmp

# Python & Pip
export PIP_CACHE_DIR=/tmp/cache/pip
export PYTHONPYCACHEPREFIX=/tmp/cache/python
export POETRY_CACHE_DIR=/tmp/cache/poetry

# Hugging Face & Transformers
export HF_HOME=/tmp/cache/huggingface
export TRANSFORMERS_CACHE=/tmp/cache/huggingface/transformers
export HF_DATASETS_CACHE=/tmp/cache/huggingface/datasets

# PyTorch
export TORCH_HOME=/tmp/cache/torch
export TORCH_EXTENSIONS_DIR=/tmp/cache/torch/extensions

# ML Libraries
export MATPLOTLIB_CACHE=/tmp/cache/matplotlib
export MPLCONFIGDIR=/tmp/cache/matplotlib
export NLTK_DATA=/tmp/cache/nltk_data
export SPACY_DATA=/tmp/cache/spacy

# Node.js
export NPM_CONFIG_CACHE=/tmp/cache/npm
export NODE_OPTIONS="--max-old-space-size=4096"

# Docker (if used)
export DOCKER_TMPDIR=/tmp/docker

# Azure
export AZURE_CONFIG_DIR=/tmp/cache/azure

# General cache
export XDG_CACHE_HOME=/tmp/cache
ENVEOF

# تحميل المتغيرات في الجلسة الحالية
source .envrc

echo "✅ Environment variables configured"

# إضافة إلى bashrc للجلسات المستقبلية
if ! grep -q "source /workspaces/RAG-ENTERPRISE/.envrc" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# RAG-ENTERPRISE cache optimization" >> ~/.bashrc
    echo "if [ -f /workspaces/RAG-ENTERPRISE/.envrc ]; then" >> ~/.bashrc
    echo "    source /workspaces/RAG-ENTERPRISE/.envrc" >> ~/.bashrc
    echo "fi" >> ~/.bashrc
fi

echo "✅ Added to ~/.bashrc"

#المرحلة D: تنظيف الكاش القديم
echo ""
echo "4️⃣ تنظيف الكاش القديم..."

# تنظيف pip cache القديم
pip cache purge 2>/dev/null || true

# تنظيف npm cache
npm cache clean --force 2>/dev/null || true

# حذف __pycache__
find /workspaces/RAG-ENTERPRISE -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find /workspaces/RAG-ENTERPRISE -type f -name "*.pyc" -delete 2>/dev/null || true

# حذف .next build (frontend)
rm -rf /workspaces/RAG-ENTERPRISE/frontend/.next 2>/dev/null || true

echo "✅ Old cache cleaned"

