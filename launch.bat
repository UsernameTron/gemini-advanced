@echo off
:: Retro AI Gemini Launcher Script for Windows
:: This script installs dependencies and launches the application

echo.
echo 🚀 NEXUS Creative AI - Retro Terminal Launcher
echo ==============================================
echo.

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

:: Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed
    echo Please install npm usually comes with Node.js
    pause
    exit /b 1
)

echo ✅ Node.js version:
node --version
echo ✅ npm version:
npm --version
echo.

:: Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
    
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    
    echo ✅ Dependencies installed successfully
    echo.
)

:: Check if .env file exists
if not exist ".env" (
    echo ⚠️  No .env file found, creating from template...
    echo GOOGLE_API_KEY=AIzaSyCEJ3ee1y00U-TrILQBmRmhALU65j7JoP8 > .env
    echo ✅ .env file created
    echo.
)

:: Display launch options
echo 🎮 Launch Options:
echo ==================
echo 1. Desktop Application (Electron)
echo 2. Web Browser (Express Server)
echo 3. Development Mode
echo.

set /p "choice=Select option (1-3) [1]: "
if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo 🖥️  Launching Desktop Application...
    npm start
) else if "%choice%"=="2" (
    echo 🌐 Starting Web Server...
    start /b npm run web
    echo 🔗 Opening browser...
    timeout /t 3 /nobreak >nul
    start http://localhost:8080
    echo.
    echo Press Ctrl+C to stop the server
    pause
) else if "%choice%"=="3" (
    echo 🔧 Starting Development Mode...
    set NODE_ENV=development
    npm run dev
) else (
    echo ❌ Invalid option selected
    pause
    exit /b 1
)
