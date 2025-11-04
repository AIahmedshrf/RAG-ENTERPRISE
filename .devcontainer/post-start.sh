#!/usr/bin/env bash
set -e

echo "⚙️ Initializing /tmp environment optimization..."

# 1️⃣ إنشاء المجلدات الأساسية
mkdir -p /tmp/rag-enterprise/{venv,storage,logs,node_modules}
mkdir -p /tmp/cache/{pip,npm,huggingface,torch,transformers,matplotlib,poetry,nltk_data,spacy,azure,python}

# 2️⃣ إنشاء ملف المتغيرات .envrc إن لم يكن موجودًا
if [ ! -f "/workspaces/RAG-ENTERPRISE/.envrc" ]; then
cat > /workspaces/RAG-ENTERPRISE/.envrc << 'ENVEOF'
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

# Docker
export DOCKER_TMPDIR=/tmp/docker

# Azure
export AZURE_CONFIG_DIR=/tmp/cache/azure

# General cache
export XDG_CACHE_HOME=/tmp/cache
ENVEOF
fi

# 3️⃣ تحميل المتغيرات
source /workspaces/RAG-ENTERPRISE/.envrc

# 4️⃣ إنشاء البيئة الافتراضية في /tmp
if [ ! -d "/tmp/rag-enterprise/venv" ]; then
    echo "📦 Creating Python venv..."
    python3 -m venv /tmp/rag-enterprise/venv
    /tmp/rag-enterprise/venv/bin/pip install -q --upgrade pip
    if [ -f "/workspaces/RAG-ENTERPRISE/requirements.txt" ]; then
        /tmp/rag-enterprise/venv/bin/pip install -q -r /workspaces/RAG-ENTERPRISE/requirements.txt
    fi
fi
ln -sfn /tmp/rag-enterprise/venv /workspaces/RAG-ENTERPRISE/venv

# 5️⃣ مجلدات التخزين والسجلات
ln -sfn /tmp/rag-enterprise/storage /workspaces/RAG-ENTERPRISE/storage
ln -sfn /tmp/rag-enterprise/logs /workspaces/RAG-ENTERPRISE/logs

# 6️⃣ node_modules
if [ -d "/workspaces/RAG-ENTERPRISE/frontend" ]; then
  cd /workspaces/RAG-ENTERPRISE/frontend
  ln -sfn /tmp/rag-enterprise/node_modules node_modules
  if [ -f "package.json" ]; then
      echo "📦 npm install..."
      npm install --quiet --no-fund --no-audit || true
  fi
  cd /workspaces/RAG-ENTERPRISE
fi

# 7️⃣ تنظيف الملفات الأقدم من أسبوع لتوفير المساحة
find /tmp/rag-enterprise -type f -mtime +7 -delete 2>/dev/null || true
find /tmp/cache -type f -mtime +7 -delete 2>/dev/null || true

echo "✅ /tmp environment fully initialized"
