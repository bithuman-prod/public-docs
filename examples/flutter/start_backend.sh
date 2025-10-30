#!/bin/bash

# Flutter Integration Backend Startup Script
# This script starts the Python backend with bitHuman avatar integration

echo "🚀 Starting Flutter Integration Backend..."

# Check if we're in the right directory
if [ ! -f "backend/agent.py" ]; then
    echo "❌ Error: Please run this script from the flutter integration root directory"
    echo "   Expected structure: flutter/start_backend.sh"
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
    echo "   # Then edit .env with your API keys"
    echo ""
    echo "   Required environment variables:"
    echo "   - BITHUMAN_API_SECRET"
    echo "   - OPENAI_API_KEY"
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

# Run diagnostic check
echo "🔍 Running diagnostic check..."
python diagnose.py

if [ $? -ne 0 ]; then
    echo "❌ Diagnostic check failed. Please fix the issues above."
    exit 1
fi

echo "✅ Diagnostic check passed!"

# Start the agent
echo "🎯 Starting bitHuman agent..."
echo "   - Agent will automatically connect to any room Flutter app joins"
echo "   - Avatar will be available for Flutter app"
echo "   - Press Ctrl+C to stop"
echo ""

python agent.py dev
