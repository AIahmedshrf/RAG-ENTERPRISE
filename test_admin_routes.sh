#!/bin/bash

API_URL="http://localhost:8000"
ADMIN_EMAIL="admin@demo.com"
ADMIN_PASSWORD="admin123"

echo "=== 🧪 RAG-ENTERPRISE Admin Routes Test ==="
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "\n${YELLOW}1️⃣ Testing Health Check${NC}"
HEALTH=$(curl -s ${API_URL}/health)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ API is running${NC}"
    echo "$HEALTH" | jq '.'
else
    echo -e "${RED}❌ API is not responding${NC}"
    exit 1
fi

# Test 2: Login
echo -e "\n${YELLOW}2️⃣ Testing Authentication${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}")

echo "Login Response:"
echo "$LOGIN_RESPONSE" | jq '.'

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo -e "${RED}❌ Failed to get access token${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Token obtained: ${TOKEN:0:20}...${NC}"

# Test 3: Get Current User
echo -e "\n${YELLOW}3️⃣ Testing Get Current User${NC}"
USER_RESPONSE=$(curl -s -X GET "${API_URL}/api/v1/auth/me" \
    -H "Authorization: Bearer ${TOKEN}")
echo "$USER_RESPONSE" | jq '.'

# Test 4: Admin Datasets
echo -e "\n${YELLOW}4️⃣ Testing GET /api/v1/admin/datasets${NC}"
DATASETS_RESPONSE=$(curl -s -X GET "${API_URL}/api/v1/admin/datasets" \
    -H "Authorization: Bearer ${TOKEN}")
echo "$DATASETS_RESPONSE" | jq '.'

if echo "$DATASETS_RESPONSE" | jq -e '.data' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Datasets endpoint working${NC}"
else
    echo -e "${RED}❌ Datasets endpoint failed${NC}"
fi

# Test 5: Admin Apps
echo -e "\n${YELLOW}5️⃣ Testing GET /api/v1/admin/apps${NC}"
APPS_RESPONSE=$(curl -s -X GET "${API_URL}/api/v1/admin/apps" \
    -H "Authorization: Bearer ${TOKEN}")
echo "$APPS_RESPONSE" | jq '.'

if echo "$APPS_RESPONSE" | jq -e '.data' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Apps endpoint working${NC}"
else
    echo -e "${RED}❌ Apps endpoint failed${NC}"
fi

# Test 6: Admin Workspace
echo -e "\n${YELLOW}6️⃣ Testing GET /api/v1/admin/workspace${NC}"
WORKSPACE_RESPONSE=$(curl -s -X GET "${API_URL}/api/v1/admin/workspace" \
    -H "Authorization: Bearer ${TOKEN}")
echo "$WORKSPACE_RESPONSE" | jq '.'

if echo "$WORKSPACE_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Workspace endpoint working${NC}"
else
    echo -e "${RED}❌ Workspace endpoint failed${NC}"
fi

# Test 7: Workspace Members
echo -e "\n${YELLOW}7️⃣ Testing GET /api/v1/admin/workspace/members${NC}"
MEMBERS_RESPONSE=$(curl -s -X GET "${API_URL}/api/v1/admin/workspace/members" \
    -H "Authorization: Bearer ${TOKEN}")
echo "$MEMBERS_RESPONSE" | jq '.'

if echo "$MEMBERS_RESPONSE" | jq -e '.data' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Workspace members endpoint working${NC}"
else
    echo -e "${RED}❌ Workspace members endpoint failed${NC}"
fi

# Test 8: Create Demo Dataset
echo -e "\n${YELLOW}8️⃣ Testing POST /api/v1/admin/datasets (Create Demo Dataset)${NC}"
CREATE_DATASET=$(curl -s -X POST "${API_URL}/api/v1/admin/datasets?name=Demo%20Dataset&description=Test%20dataset%20for%20RAG&indexing_technique=high_quality" \
    -H "Authorization: Bearer ${TOKEN}")
echo "$CREATE_DATASET" | jq '.'

if echo "$CREATE_DATASET" | jq -e '.id' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Dataset created successfully${NC}"
    DATASET_ID=$(echo "$CREATE_DATASET" | jq -r '.id')
    echo "Dataset ID: $DATASET_ID"
else
    echo -e "${YELLOW}⚠️ Dataset creation failed (might already exist)${NC}"
fi

# Test 9: Create Demo App
echo -e "\n${YELLOW}9️⃣ Testing POST /api/v1/admin/apps (Create Demo App)${NC}"
CREATE_APP=$(curl -s -X POST "${API_URL}/api/v1/admin/apps?name=Demo%20Chat%20App&mode=chat&icon=💬&description=Demo%20chat%20application" \
    -H "Authorization: Bearer ${TOKEN}")
echo "$CREATE_APP" | jq '.'

if echo "$CREATE_APP" | jq -e '.id' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ App created successfully${NC}"
    APP_ID=$(echo "$CREATE_APP" | jq -r '.id')
    echo "App ID: $APP_ID"
else
    echo -e "${YELLOW}⚠️ App creation failed (might already exist)${NC}"
fi

# Test 10: List Datasets Again
echo -e "\n${YELLOW}🔟 Testing GET /api/v1/admin/datasets (After Creation)${NC}"
DATASETS_RESPONSE_2=$(curl -s -X GET "${API_URL}/api/v1/admin/datasets" \
    -H "Authorization: Bearer ${TOKEN}")
echo "$DATASETS_RESPONSE_2" | jq '.'

DATASET_COUNT=$(echo "$DATASETS_RESPONSE_2" | jq '.total // 0')
echo -e "${GREEN}Total Datasets: ${DATASET_COUNT}${NC}"

# Summary
echo -e "\n=========================================="
echo -e "${GREEN}🎉 Admin Routes Test Complete${NC}"
echo "=========================================="

