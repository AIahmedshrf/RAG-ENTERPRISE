#!/bin/bash

echo "🚀 Starting RAG-ENTERPRISE Full System"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Start Backend
echo "1️⃣ Starting Backend API..."
cd /workspaces/RAG-ENTERPRISE
source venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend
sleep 5

# Start Frontend
echo ""
echo "2️⃣ Starting Frontend..."
cd /workspaces/RAG-ENTERPRISE/frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ System Running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Backend API:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
echo "🎨 Frontend:     http://localhost:3000"
echo "👑 Admin Panel:  http://localhost:3000/admin"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Wait for interruption
wait
