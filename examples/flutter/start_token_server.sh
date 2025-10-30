#!/bin/bash

# Token Server Startup Script
# This script starts the Flask token generation server

echo "🔑 Starting LiveKit Token Server..."

# Check if we're in the right directory
if [ ! -f "backend/token_server.py" ]; then
    echo "❌ Error: Please run this script from the flutter integration root directory"
    echo "   Expected structure: flutter/start_token_server.sh"
    exit 1
fi

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Please copy env.example to .env and configure your credentials:"
    echo "   cp env.example .env"
    echo "   # Then edit .env with your LiveKit credentials"
    echo ""
    echo "   Required environment variables:"
    echo "   - LIVEKIT_API_KEY"
    echo "   - LIVEKIT_API_SECRET"
    echo "   - LIVEKIT_URL"
    echo ""
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Set default port if not specified
export TOKEN_SERVER_PORT=${TOKEN_SERVER_PORT:-3000}
export TOKEN_SERVER_HOST=${TOKEN_SERVER_HOST:-0.0.0.0}

echo "🌐 Starting token server on http://$TOKEN_SERVER_HOST:$TOKEN_SERVER_PORT"
echo "   - Health check: http://$TOKEN_SERVER_HOST:$TOKEN_SERVER_PORT/health"
echo "   - Token endpoint: http://$TOKEN_SERVER_HOST:$TOKEN_SERVER_PORT/token"
echo "   - Configuration: http://$TOKEN_SERVER_HOST:$TOKEN_SERVER_PORT/config"
echo "   - Press Ctrl+C to stop"
echo ""

# Start the token server
python token_server.py
