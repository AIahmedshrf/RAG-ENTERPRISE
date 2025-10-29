#!/bin/bash
# اختبار شامل للنظام

echo "🧪 اختبار شامل لـ RAG-ENTERPRISE"
echo "=================================="

BASE_URL="http://localhost:8000/api/v1"

# 1. Health Check
echo -e "\n1️⃣ Health Check..."
curl -s http://localhost:8000/health | jq .

# 2. Config
echo -e "\n2️⃣ Configuration..."
curl -s http://localhost:8000/config | jq .

# 3. Supported Formats
echo -e "\n3️⃣ Supported Formats..."
curl -s $BASE_URL/documents/supported-formats | jq .

# 4. Agents List
echo -e "\n4️⃣ Chat Agents..."
curl -s $BASE_URL/chat/agents | jq '.agents[] | {name, description}'

# 5. Financial Agents
echo -e "\n5️⃣ Financial Agents..."
curl -s $BASE_URL/financial/agents | jq '.agents[] | {name, description}'

# 6. Stats
echo -e "\n6️⃣ System Stats..."
curl -s $BASE_URL/documents/stats | jq .

echo -e "\n✅ جميع الاختبارات مكتملة!"