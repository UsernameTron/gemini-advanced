#!/bin/bash

# Retro AI Desktop - Quick Launcher for macOS
# This script can be saved as "Retro AI Desktop.command" on your desktop

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="/Users/cpconnor/projects/UnifiedAIPlatform/retro-ai-desktop"

# Change to the application directory
cd "$APP_DIR" || {
    echo "❌ Error: Could not find application directory at $APP_DIR"
    echo "Please update the APP_DIR variable in this script to point to your installation."
    exit 1
}

# ASCII Art Header
cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║                🎛️  RETRO AI DESKTOP LAUNCHER                    ║
║                    1970s Command Center                         ║
╚══════════════════════════════════════════════════════════════════╝
EOF

echo ""
echo "🔍 Checking system requirements..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18 or higher is required. Current version: $(node --version)"
    exit 1
fi

echo "✅ Node.js $(node --version) detected"

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if application is built
if [ ! -d "dist" ]; then
    echo "🔨 Building application..."
    npm run build
fi

# Check for Google API key
if [ -f ".env" ]; then
    source .env
fi

if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_google_api_key_here" ]; then
    echo ""
    echo "⚠️  Google API Key Setup Required"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "To use image generation features, you need a Google AI API key:"
    echo ""
    echo "1. Visit: https://makersuite.google.com/app/apikey"
    echo "2. Create a new API key"
    echo "3. Edit the .env file in this directory and replace:"
    echo "   GOOGLE_API_KEY=your_google_api_key_here"
    echo "   with your actual API key"
    echo ""
    read -p "Press ENTER to continue without API key (limited functionality) or Ctrl+C to exit..."
    echo ""
fi

echo "🚀 Starting Retro AI Desktop..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Application will be available at: http://localhost:3000"
echo "🖥️  Desktop app will open automatically"
echo ""
echo "💡 Quick Commands to try:"
echo "   • HELP - Show all commands"
echo "   • STATUS - Check system status"
echo "   • GEN a cyberpunk cityscape - Generate an image"
echo ""
echo "Press Ctrl+C to stop the application"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the application
npm start
