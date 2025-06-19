#!/bin/bash

# Retro AI Desktop - Web Interface Launcher
# This script launches the application and opens the web browser interface

# Set the project directory
PROJECT_DIR="/Users/cpconnor/projects/UnifiedAIPlatform/retro-ai-desktop"

# Function to check if the application is running
check_app_running() {
    pgrep -f "electron.*retro-ai-desktop" > /dev/null
}

# Function to check if the web server is responding
check_web_server() {
    curl -s -o /dev/null -w "%{http_code}" http://localhost:3002 | grep -q "200"
}

echo "🖥️  RETRO AI DESKTOP - WEB INTERFACE LAUNCHER"
echo "============================================="
echo ""

# Change to project directory
cd "$PROJECT_DIR" || {
    echo "❌ Error: Could not find project directory at $PROJECT_DIR"
    echo "Please update the PROJECT_DIR variable in this script."
    exit 1
}

# Check if the app is already running
if check_app_running; then
    echo "✅ Retro AI Desktop is already running"
    
    # Wait a moment and check if web server is responding
    sleep 2
    if check_web_server; then
        echo "🌐 Opening web interface..."
        open "http://localhost:3002"
        exit 0
    else
        echo "⚠️  App is running but web server not responding. Restarting..."
        pkill -f "electron.*retro-ai-desktop"
        sleep 3
    fi
fi

# Check if project is built
if [ ! -f "dist/main/main.js" ]; then
    echo "🔨 Building project..."
    npm run build
    if [ $? -ne 0 ]; then
        echo "❌ Build failed. Please check the project setup."
        exit 1
    fi
fi

# Check API key
if grep -q "your_google_api_key_here" .env; then
    echo "⚠️  Warning: Please set your Google API key in .env file"
else
    echo "✅ Google API key configured"
fi

echo "🚀 Starting Retro AI Desktop..."

# Start the application in background
npm start > /dev/null 2>&1 &
APP_PID=$!

echo "⏳ Waiting for application to start..."

# Wait for the application to be ready (max 30 seconds)
COUNTER=0
while [ $COUNTER -lt 30 ]; do
    if check_web_server; then
        echo "✅ Application started successfully!"
        echo "🌐 Opening web interface at http://localhost:3002"
        
        # Open the web browser
        open "http://localhost:3002"
        
        echo ""
        echo "🎮 Your 1970s AI Command Center is ready!"
        echo "Available commands:"
        echo "  • GEN <prompt> - Generate images with Gemini"
        echo "  • IMAGEN <prompt> - High-quality images with Imagen"
        echo "  • UPLOAD - Upload images for editing"
        echo "  • GALLERY - View your collection"
        echo "  • HELP - Show all commands"
        echo ""
        echo "To stop the application, close the Electron window or run:"
        echo "  pkill -f 'electron.*retro-ai-desktop'"
        
        exit 0
    fi
    
    sleep 1
    COUNTER=$((COUNTER + 1))
    echo -n "."
done

echo ""
echo "❌ Application failed to start within 30 seconds"
echo "Please check the logs and try again"

# Kill the app if it's still running but not responding
kill $APP_PID 2>/dev/null

exit 1
