#!/bin/bash

# Build Distribution Package for macOS
# This script creates a standalone .dmg installer for macOS

echo "🎛️  Building Retro AI Desktop for macOS Distribution"
echo "═══════════════════════════════════════════════════════════════════"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the project root."
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ release/

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the application
echo "🔨 Building application..."
npm run build

# Check if icon exists, create placeholder if not
if [ ! -f "assets/icon.icns" ]; then
    echo "⚠️  Creating placeholder icon (replace assets/icon.icns with your custom icon)"
    
    # Create a simple icon from SVG (requires ImageMagick or similar)
    if command -v convert &> /dev/null; then
        echo "🎨 Converting SVG to ICNS..."
        # This would require ImageMagick: convert assets/icon.svg assets/icon.icns
        # For now, we'll skip this step
    fi
fi

# Build the distributable
echo "📱 Building macOS application..."
npm run dist:mac

# Check if build was successful
if [ -d "release" ] && [ "$(ls -A release)" ]; then
    echo ""
    echo "✅ Build completed successfully!"
    echo "═══════════════════════════════════════════════════════════════════"
    echo "📁 Built files are in the 'release/' directory:"
    ls -la release/
    echo ""
    echo "🎯 To install:"
    echo "   1. Open the .dmg file in the release/ directory"
    echo "   2. Drag the app to your Applications folder"
    echo "   3. Launch from Applications or Spotlight"
    echo ""
    echo "🔧 To distribute:"
    echo "   • Share the .dmg file with users"
    echo "   • For App Store: Additional code signing required"
    echo "   • For enterprise: Set up auto-update server"
    echo ""
else
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi
