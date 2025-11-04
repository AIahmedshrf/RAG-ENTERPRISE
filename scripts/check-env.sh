#!/usr/bin/env bash
set -e

echo "🔍 Checking RAG-ENTERPRISE environment status..."
echo "---------------------------------------------"

status_ok=true

# Helper function
check() {
  local desc="$1"
  local cmd="$2"
  local expected="$3"
  local result
  result=$(eval "$cmd" 2>/dev/null || echo "❌ ERROR")

  if [[ "$result" == *"$expected"* ]]; then
    echo "✅ $desc → OK"
  else
    echo "❌ $desc → Failed (got: $result)"
    status_ok=false
  fi
}

echo "🧩 Checking environment variables..."
check "TMPDIR" "echo \$TMPDIR" "/tmp"
check "PIP_CACHE_DIR" "echo \$PIP_CACHE_DIR" "/tmp/cache/pip"
check "HF_HOME" "echo \$HF_HOME" "/tmp/cache/huggingface"
check "TORCH_HOME" "echo \$TORCH_HOME" "/tmp/cache/torch"

echo ""
echo "🪶 Checking symbolic links..."
check "venv symlink" "readlink /workspaces/RAG-ENTERPRISE/venv" "/tmp/rag-enterprise/venv"
check "storage symlink" "readlink /workspaces/RAG-ENTERPRISE/storage" "/tmp/rag-enterprise/storage"
check "logs symlink" "readlink /workspaces/RAG-ENTERPRISE/logs" "/tmp/rag-enterprise/logs"

if [ -d "/workspaces/RAG-ENTERPRISE/frontend" ]; then
  check "node_modules symlink" "readlink /workspaces/RAG-ENTERPRISE/frontend/node_modules" "/tmp/rag-enterprise/node_modules"
fi

echo ""
echo "🐍 Checking Python environment..."
check "Python path" "which python" "/workspaces/RAG-ENTERPRISE/venv/bin/python"
check "Python venv location" "python -m pip show pip | grep Location" "/tmp/rag-enterprise/venv"

echo ""
echo "📦 Checking npm cache..."
check "npm cache dir" "npm config get cache" "/tmp/cache/npm"

echo ""
echo "💾 Checking /tmp disk usage..."
df -h /tmp | awk 'NR==2 {print "✅ /tmp usage:", $5, "used, available:", $4}'

echo ""
if [ "$status_ok" = true ]; then
  echo "🎉 All checks passed successfully!"
else
  echo "⚠️ Some checks failed — review the ❌ items above."
fi
echo "---------------------------------------------"
