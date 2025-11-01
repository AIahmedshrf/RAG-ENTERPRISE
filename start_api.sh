#!/bin/bash

cd /workspaces/RAG-ENTERPRISE
source venv/bin/activate

# Stop old instance
if [ -f api.pid ]; then
    kill $(cat api.pid) 2>/dev/null
    rm api.pid
fi

pkill -f "uvicorn api.main:app" 2>/dev/null
sleep 2

# Start API
nohup uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > api.log 2>&1 &
echo $! > api.pid

echo "API started (PID: $(cat api.pid))"
echo "Logs: tail -f api.log"
