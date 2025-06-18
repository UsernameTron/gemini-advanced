#!/bin/bash

# Retro AI Gemini Launcher Script for macOS/Linux
# This script installs dependencies and launches the application

echo "🚀 NEXUS Creative AI - Retro Terminal Launcher"
echo "=============================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed"
    echo "Please install npm (usually comes with Node.js)"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"
echo ""

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    
    echo "✅ Dependencies installed successfully"
    echo ""
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found, creating from template..."
    cp .env.example .env 2>/dev/null || echo "GOOGLE_API_KEY=AIzaSyCEJ3ee1y00U-TrILQBmRmhALU65j7JoP8" > .env
    echo "✅ .env file created"
    echo ""
fi

# Display launch options
echo "🎮 Launch Options:"
echo "=================="
echo "1. Desktop Application (Electron)"
echo "2. Web Browser (Express Server)"
echo "3. Development Mode"
echo ""

read -p "Select option (1-3) [1]: " choice
choice=${choice:-1}

case $choice in
    1)
        echo "🖥️  Launching Desktop Application..."
        npm start
        ;;
    2)
        echo "🌐 Starting Web Server..."
        npm run web &
        SERVER_PID=$!
        echo "📍 Server PID: $SERVER_PID"
        echo "🔗 Opening browser..."
        sleep 3
        
        # Open browser based on platform
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open http://localhost:8080
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            xdg-open http://localhost:8080
        else
            echo "Please open http://localhost:8080 in your browser"
        fi
        
        echo ""
        echo "Press Ctrl+C to stop the server"
        wait $SERVER_PID
        ;;
    3)
        echo "🔧 Starting Development Mode..."
        NODE_ENV=development npm run dev
        ;;
    *)
        echo "❌ Invalid option selected"
        exit 1
        ;;
esac
