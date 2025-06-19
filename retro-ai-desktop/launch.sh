#!/bin/bash

# Retro AI Desktop Launcher Script

echo "🎛️  Starting Retro AI Desktop - 1970s Command Center"
echo "=================================================="

# Check if Google API key is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: GOOGLE_API_KEY environment variable not set"
    echo "   You can set it by creating a .env file or exporting it:"
    echo "   export GOOGLE_API_KEY='your_api_key_here'"
    echo ""
fi

# Check if dist directory exists
if [ ! -d "dist" ]; then
    echo "📦 Building application..."
    npm run build
fi

# Start the application
echo "🚀 Launching desktop application..."
echo "   → Server will start on http://localhost:3000"
echo "   → Electron app will open automatically"
echo ""

npm start
