#!/bin/bash

# HeySalad Platform - Frontend Startup Script
# Starts the Xin Yi WMS Dashboard

echo "🎨 Starting HeySalad Xin Yi Frontend..."
echo "========================================"
echo ""

# Check if backend is running
if ! curl -s http://localhost:2124/health > /dev/null 2>&1; then
    echo "⚠️  WARNING: Backend doesn't seem to be running!"
    echo "   Please start the backend first:"
    echo "   cd backend && uv run python app_platform.py"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get local IP for display
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "✅ Starting frontend server..."
echo ""
echo "📍 Access the dashboard at:"
echo "   • Local:   http://localhost:2125"
echo "   • Network: http://$LOCAL_IP:2125"
echo ""
echo "🔗 Backend API: http://localhost:2124"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================"
echo ""

cd frontend
python3 server.py
