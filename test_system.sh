#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║        🧪 RAG-ENTERPRISE - COMPREHENSIVE TEST 🧪         ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
PASS=0
FAIL=0

test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $response)"
        ((PASS++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $response, expected $expected_status)"
        ((FAIL++))
        return 1
    fi
}

# 1. Stop existing API
echo "1️⃣ Stopping existing API..."
pkill -f "uvicorn api.main:app" 2>/dev/null
pkill -f "python.*api.main" 2>/dev/null
sleep 2
echo -e "${GREEN}✅ Done${NC}\n"

# 2. Start API
echo "2️⃣ Starting API server..."
cd /workspaces/RAG-ENTERPRISE

# 🔧 Fixed: Use python3 -m uvicorn instead of uvicorn directly
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/api_test.log 2>&1 &
API_PID=$!
echo "   PID: $API_PID"

# Wait for API to start
echo -n "   Waiting for API to be ready"
for i in {1..15}; do
    sleep 1
    echo -n "."
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        break
    fi
done
echo ""

if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${RED}❌ API failed to start!${NC}"
    echo "Logs:"
    tail -30 /tmp/api_test.log
    exit 1
fi

echo -e "${GREEN}✅ API started successfully${NC}\n"

# 3. Test Health Endpoints
echo "3️⃣ Testing Health Endpoints..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Health Check" "http://localhost:8000/health/health"
test_endpoint "Database Health" "http://localhost:8000/health/db"
test_endpoint "System Stats" "http://localhost:8000/health/stats"

echo ""

# 4. Test Health Check Details
echo "4️⃣ Health Check Details..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s http://localhost:8000/health/health | jq '.' 2>/dev/null || curl -s http://localhost:8000/health/health
echo ""

# 5. Test Database Stats
echo "5️⃣ Database Statistics..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s http://localhost:8000/health/stats | jq '.statistics' 2>/dev/null || curl -s http://localhost:8000/health/stats
echo ""

# 6. Test Authentication
echo "6️⃣ Testing Authentication..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Login
echo -n "Testing Login (admin)... "
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@demo.com","password":"admin123"}')

if echo "$LOGIN_RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS++))
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
    echo "   Token: ${TOKEN:0:50}..."
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL++))
    echo "   Response: $LOGIN_RESPONSE"
fi

echo ""

# 7. Test Protected Endpoints
if [ ! -z "$TOKEN" ]; then
    echo "7️⃣ Testing Protected Endpoints..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Get current user
    echo -n "Testing /auth/me... "
    ME_RESPONSE=$(curl -s http://localhost:8000/auth/me \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$ME_RESPONSE" | jq -e '.email' > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASS++))
        echo "   User: $(echo $ME_RESPONSE | jq -r '.email')"
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAIL++))
    fi
    
    echo ""
fi

# 8. Database File Check
echo "8️⃣ Database File Status..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "rag_enterprise.db" ]; then
    DB_SIZE=$(ls -lh rag_enterprise.db | awk '{print $5}')
    echo -e "${GREEN}✅ Database file exists${NC}"
    echo "   Size: $DB_SIZE"
    echo "   Location: $(pwd)/rag_enterprise.db"
    ((PASS++))
else
    echo -e "${RED}❌ Database file not found${NC}"
    ((FAIL++))
fi

echo ""

# 9. API Documentation
echo "9️⃣ API Documentation..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "OpenAPI Docs" "http://localhost:8000/docs" 200

echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                     TEST SUMMARY                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "   ${GREEN}✅ Passed: $PASS${NC}"
echo -e "   ${RED}❌ Failed: $FAIL${NC}"
echo ""

TOTAL=$((PASS + FAIL))
if [ $TOTAL -gt 0 ]; then
    SUCCESS_RATE=$((PASS * 100 / TOTAL))
    echo "   Success Rate: $SUCCESS_RATE%"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   ACCESS INFORMATION                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "   🌐 API URL:       http://localhost:8000"
echo "   📚 API Docs:      http://localhost:8000/docs"
echo "   🔍 Health Check:  http://localhost:8000/health/health"
echo ""
echo "   👤 Admin:  admin@demo.com / admin123"
echo "   👤 User:   user@demo.com / password123"
echo "   👤 Viewer: viewer@demo.com / viewer123"
echo ""
echo "   📊 API Process ID: $API_PID"
echo "   📋 Logs: /tmp/api_test.log"
echo ""
echo "   To stop API: kill $API_PID"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          ✅ ALL TESTS PASSED - SYSTEM READY! ✅          ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              ⚠️  SOME TESTS FAILED  ⚠️                   ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    
    if [ $FAIL -le 2 ]; then
        echo ""
        echo "💡 Tip: Check the logs at /tmp/api_test.log for details"
    fi
    
    exit 1
fi
