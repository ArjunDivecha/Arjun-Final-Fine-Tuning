#!/bin/bash
echo "🚀 Starting MLX Fine-Tuning GUI"
echo "================================"
echo ""
echo "Starting backend server..."
cd "/Users/macbook2024/Library/CloudStorage/Dropbox/AAA Backup/A Working/Arjun Final Fine Tuning"
.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
echo ""
sleep 3
echo "Starting Electron GUI..."
npm start
