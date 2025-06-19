#!/bin/bash

# Retro AI Desktop - Final Setup and Launch Script
# This script helps complete the setup and launch the application

echo "🖥️  RETRO AI DESKTOP - FINAL SETUP"
echo "=================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Creating from template..."
    cp .env.template .env 2>/dev/null || echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
fi

# Check if API key is set
if grep -q "your_google_api_key_here" .env; then
    echo "⚠️  API Key Setup Required"
    echo "Please edit the .env file and add your Google API key:"
    echo ""
    echo "   1. Get your API key from: https://makersuite.google.com/app/apikey"
    echo "   2. Edit .env file: nano .env"
    echo "   3. Replace 'your_google_api_key_here' with your actual API key"
    echo ""
    read -p "Press Enter after setting up your API key to continue..."
fi

# Check if project is built
if [ ! -d "dist" ]; then
    echo "🔨 Building project..."
    npm run build
fi

# Launch the application
echo "🚀 Launching Retro AI Desktop..."
echo ""
echo "Features available:"
echo "  • GEN <prompt> - Generate images with Gemini"
echo "  • IMAGEN <prompt> - High-quality images with Imagen"
echo "  • EDIT <description> - Edit uploaded images"
echo "  • PHOTO, ART, LOGO - Specialized image types"
echo "  • UPLOAD - Upload images for editing"
echo "  • GALLERY - View image collection"
echo "  • HELP - Full command list"
echo ""

npm start
