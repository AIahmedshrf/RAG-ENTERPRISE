#!/bin/bash
# ============================================
# RAG System Complete Test
# ============================================

cd /workspaces/RAG-ENTERPRISE

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          🧪 RAG System Complete Test Suite                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get token
TOKEN=$(cat .api_token 2>/dev/null)
if [ -z "$TOKEN" ]; then
    echo "❌ No token found. Please login first."
    exit 1
fi

DATASET_ID=$(cat .test_dataset_id 2>/dev/null)
if [ -z "$DATASET_ID" ]; then
    echo "❌ No dataset ID found."
    exit 1
fi

# Test 1: Health Check
echo "1️⃣  API Health Check"
HEALTH=$(curl -s http://localhost:8000/health)
STATUS=$(echo $HEALTH | python -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)

if [ "$STATUS" == "healthy" ]; then
    echo -e "   ${GREEN}✅ API is healthy${NC}"
else
    echo -e "   ${RED}❌ API unhealthy${NC}"
    exit 1
fi

# Test 2: Retrieval Stats
echo ""
echo "2️⃣  Retrieval Statistics"
STATS=$(curl -s -X GET http://localhost:8000/api/v1/chat/retrieval-stats \
    -H "Authorization: Bearer $TOKEN")

echo $STATS | python -c "import sys, json; data=json.load(sys.stdin); print(f\"   Segments in DB: {data['statistics']['total_segments_in_db']}\")"

# Test 3: Index Dataset
echo ""
echo "3️⃣  Dataset Indexing"
INDEX=$(curl -s -X POST "http://localhost:8000/api/v1/chat/index-dataset?dataset_id=$DATASET_ID" \
    -H "Authorization: Bearer $TOKEN")

INDEXED=$(echo $INDEX | python -c "import sys, json; print(json.load(sys.stdin).get('statistics', {}).get('indexed', 0))" 2>/dev/null)

if [ "$INDEXED" -gt "0" ]; then
    echo -e "   ${GREEN}✅ Indexed $INDEXED segments${NC}"
else
    echo -e "   ${YELLOW}⚠️  No segments indexed${NC}"
fi

# Test 4: RAG Chat
echo ""
echo "4️⃣  RAG Chat Test"

CHAT=$(curl -s -X POST http://localhost:8000/api/v1/chat/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"What is RAG?\", \"dataset_id\": \"$DATASET_ID\", \"use_rag\": true, \"top_k\": 3}")

USED_RAG=$(echo $CHAT | python -c "import sys, json; print(json.load(sys.stdin).get('used_rag', False))" 2>/dev/null)
SOURCES=$(echo $CHAT | python -c "import sys, json; print(len(json.load(sys.stdin).get('sources', [])))" 2>/dev/null)

if [ "$USED_RAG" == "True" ]; then
    echo -e "   ${GREEN}✅ RAG used successfully${NC}"
    echo "   📚 Sources retrieved: $SOURCES"
else
    echo -e "   ${YELLOW}⚠️  RAG not used${NC}"
fi

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ Test Summary                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "   API: $STATUS"
echo "   Indexed: $INDEXED segments"
echo "   RAG: $USED_RAG"
echo "   Sources: $SOURCES"
echo ""
echo -e "${GREEN}✅ All tests completed!${NC}"
