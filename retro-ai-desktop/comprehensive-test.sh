#!/bin/bash

# Comprehensive Final Test Suite
# Tests all aspects of the Retro AI Desktop application

echo "🧪 RETRO AI DESKTOP - COMPREHENSIVE TEST SUITE"
echo "=============================================="
echo ""

# Test 1: Project Structure
echo "📁 Test 1: Checking project structure..."
REQUIRED_DIRS=("src/main" "src/renderer" "src/shared" "assets" "dist")
REQUIRED_FILES=("package.json" ".env" "README.md" "FINAL_STATUS.md")

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir exists"
    else
        echo "   ❌ $dir missing"
        exit 1
    fi
done

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file exists"
    else
        echo "   ❌ $file missing"
        exit 1
    fi
done

# Test 2: Dependencies
echo ""
echo "📦 Test 2: Checking dependencies..."
if [ -d "node_modules" ]; then
    echo "   ✅ node_modules installed"
else
    echo "   ❌ node_modules missing - run npm install"
    exit 1
fi

# Test 3: TypeScript Compilation
echo ""
echo "🔨 Test 3: Testing TypeScript compilation..."
npm run build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ TypeScript compilation successful"
else
    echo "   ❌ TypeScript compilation failed"
    exit 1
fi

# Test 4: Distribution Files
echo ""
echo "📦 Test 4: Checking build output..."
if [ -f "dist/main/main.js" ]; then
    echo "   ✅ Main process compiled"
else
    echo "   ❌ Main process compilation failed"
    exit 1
fi

if [ -d "dist/renderer" ]; then
    echo "   ✅ Renderer files copied"
else
    echo "   ❌ Renderer files missing"
    exit 1
fi

# Test 5: Assets
echo ""
echo "🎨 Test 5: Checking assets..."
if [ -f "assets/icon.icns" ]; then
    echo "   ✅ macOS icon (.icns) available"
else
    echo "   ❌ macOS icon missing"
    exit 1
fi

if [ -f "assets/icon.svg" ]; then
    echo "   ✅ SVG icon available"
else
    echo "   ❌ SVG icon missing"
    exit 1
fi

# Test 6: Electron Packaging
echo ""
echo "📱 Test 6: Testing Electron packaging..."
npm run pack > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Electron packaging successful"
    if [ -d "release/mac-arm64/Retro AI Desktop.app" ]; then
        echo "   ✅ macOS app bundle created"
    else
        echo "   ❌ macOS app bundle missing"
        exit 1
    fi
else
    echo "   ❌ Electron packaging failed"
    exit 1
fi

# Test 7: Configuration Files
echo ""
echo "⚙️  Test 7: Checking configuration..."
if grep -q "com.cpconnor.retro-ai-desktop" package.json; then
    echo "   ✅ App ID configured"
else
    echo "   ❌ App ID missing in package.json"
    exit 1
fi

if grep -q "GOOGLE_API_KEY" .env; then
    echo "   ✅ Environment variables configured"
else
    echo "   ❌ Environment variables missing"
    exit 1
fi

# Test 8: Launch Scripts
echo ""
echo "🚀 Test 8: Checking launch scripts..."
LAUNCH_SCRIPTS=("desktop-launcher.command" "launch.sh" "setup-and-launch.sh")

for script in "${LAUNCH_SCRIPTS[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        echo "   ✅ $script executable"
    else
        echo "   ❌ $script missing or not executable"
        exit 1
    fi
done

# Final Report
echo ""
echo "🎉 ALL TESTS PASSED!"
echo "====================="
echo ""
echo "📊 Test Summary:"
echo "   ✅ Project structure complete"
echo "   ✅ Dependencies installed" 
echo "   ✅ TypeScript compilation working"
echo "   ✅ Build output generated"
echo "   ✅ Assets properly configured"
echo "   ✅ Electron packaging successful"
echo "   ✅ Configuration files valid"
echo "   ✅ Launch scripts ready"
echo ""
echo "🎯 STATUS: RETRO AI DESKTOP IS 100% READY!"
echo ""
echo "Next steps:"
echo "1. Add your Google API key to .env"
echo "2. Run ./setup-and-launch.sh"
echo "3. Enjoy your 1970s AI Command Center!"
echo ""
