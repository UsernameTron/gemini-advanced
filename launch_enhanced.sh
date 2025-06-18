#!/bin/bash

# Enhanced Retro AI Gemini Launcher Script for macOS/Linux
# This script provides multiple ways to launch the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Header
show_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    NEXUS CREATIVE AI                         ║"
    echo "║                  Retro Terminal Interface                    ║"
    echo "║               Powered by Google Gemini AI                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check dependencies
check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm is not installed. Please install npm first.${NC}"
        exit 1
    fi
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        echo -e "${RED}❌ package.json not found. Please run this script from the retro-ai-gemini directory.${NC}"
        exit 1
    fi
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}⚠️  Dependencies not installed. Installing now...${NC}"
        npm install
    fi
    
    echo -e "${GREEN}✅ All dependencies satisfied${NC}"
}

# Check environment configuration
check_environment() {
    echo -e "${YELLOW}Checking environment configuration...${NC}"
    
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env file not found. Creating default configuration...${NC}"
        cat > .env << EOL
# Retro AI Gemini Creative Agent
GOOGLE_API_KEY=AIzaSyCEJ3ee1y00U-TrILQBmRmhALU65j7JoP8
NODE_ENV=development
PORT=8080
DEBUG=true
THEME=retro
TERMINAL_STYLE=classic
ENABLE_BRAND_ANALYSIS=true
ENABLE_CREATIVE_GENERATION=true
ENABLE_CAMPAIGN_ORCHESTRATION=true
EOL
        echo -e "${GREEN}✅ Default .env file created${NC}"
    fi
    
    # Source the .env file
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_api_key_here" ]; then
        echo -e "${RED}❌ Google API Key not configured properly in .env file${NC}"
        echo -e "${YELLOW}Please edit .env file and add your Google Gemini API key${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Environment configuration valid${NC}"
}

# Launch web version
launch_web() {
    echo -e "${BLUE}🚀 Starting Retro AI Gemini Web Server...${NC}"
    echo -e "${CYAN}Access the application at: http://localhost:${PORT:-8080}${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    echo ""
    npm run web
}

# Launch desktop version
launch_desktop() {
    echo -e "${BLUE}🚀 Starting Retro AI Gemini Desktop Application...${NC}"
    
    # Check if Electron is available
    if ! npm list electron &> /dev/null; then
        echo -e "${YELLOW}⚠️  Electron not found. Installing...${NC}"
        npm install electron --save-dev
    fi
    
    echo -e "${CYAN}Desktop application will open in a new window${NC}"
    echo -e "${YELLOW}Close the window to exit the application${NC}"
    echo ""
    npm run start
}

# Build for production
build_application() {
    echo -e "${BLUE}🔨 Building Retro AI Gemini for production...${NC}"
    
    # Check if electron-builder is available
    if ! npm list electron-builder &> /dev/null; then
        echo -e "${YELLOW}⚠️  electron-builder not found. Installing...${NC}"
        npm install electron-builder --save-dev
    fi
    
    echo -e "${CYAN}Building application packages...${NC}"
    npm run build
    
    echo -e "${GREEN}✅ Build complete! Check the 'dist' directory for packages${NC}"
}

# Show usage menu
show_menu() {
    echo -e "${CYAN}Choose your launch option:${NC}"
    echo ""
    echo -e "${GREEN}1)${NC} Launch Web Version (Browser Interface)"
    echo -e "${GREEN}2)${NC} Launch Desktop Version (Electron App)"
    echo -e "${GREEN}3)${NC} Open in Browser (Background Server)"
    echo -e "${GREEN}4)${NC} Build for Production"
    echo -e "${GREEN}5)${NC} Create macOS App Bundle"
    echo -e "${GREEN}6)${NC} Install as macOS Service"
    echo -e "${GREEN}7)${NC} Run Development Tests"
    echo -e "${GREEN}8)${NC} View System Information"
    echo -e "${GREEN}9)${NC} Open Documentation"
    echo -e "${GREEN}q)${NC} Quit"
    echo ""
    echo -n "Enter your choice [1-9/q]: "
}

# Run development tests
run_tests() {
    echo -e "${BLUE}🧪 Running development tests...${NC}"
    
    echo -e "${YELLOW}Testing API connection...${NC}"
    curl -s http://localhost:${PORT:-8080}/health > /dev/null && echo -e "${GREEN}✅ Server health check passed${NC}" || echo -e "${RED}❌ Server not running${NC}"
    
    echo -e "${YELLOW}Testing Gemini API...${NC}"
    if [ ! -z "$GOOGLE_API_KEY" ]; then
        node -e "
        const { GoogleGenerativeAI } = require('@google/generative-ai');
        const genAI = new GoogleGenerativeAI('$GOOGLE_API_KEY');
        const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
        model.generateContent('Test').then(() => {
            console.log('✅ Gemini API connection successful');
        }).catch(err => {
            console.log('❌ Gemini API connection failed:', err.message);
        });
        " 2>/dev/null || echo -e "${RED}❌ Gemini API test failed${NC}"
    else
        echo -e "${RED}❌ No API key configured${NC}"
    fi
}

# Show system information
show_system_info() {
    echo -e "${BLUE}📊 System Information${NC}"
    echo "================================"
    echo "Node.js Version: $(node --version)"
    echo "npm Version: $(npm --version)"
    echo "Operating System: $(uname -s)"
    echo "Architecture: $(uname -m)"
    echo "Current Directory: $(pwd)"
    echo "Port: ${PORT:-8080}"
    echo "Environment: ${NODE_ENV:-development}"
    echo "API Key Configured: $([ ! -z "$GOOGLE_API_KEY" ] && echo 'Yes' || echo 'No')"
    echo "================================"
}

# Open documentation
open_documentation() {
    echo -e "${BLUE}📚 Opening documentation...${NC}"
    
    if command -v open &> /dev/null; then
        # macOS
        open README.md
    else
        echo -e "${YELLOW}Please manually open README.md to view documentation${NC}"
    fi
}

# Open application in browser (macOS specific)
open_in_browser() {
    echo -e "${BLUE}🌐 Opening Retro AI Gemini in your default browser...${NC}"
    
    # Start server in background if not running
    if ! curl -s http://localhost:${PORT:-8080}/health > /dev/null 2>&1; then
        echo -e "${YELLOW}Starting server...${NC}"
        npm run web &
        sleep 3
    fi
    
    # Open in default browser
    open "http://localhost:${PORT:-8080}"
    echo -e "${GREEN}✅ Application opened in browser${NC}"
    echo -e "${YELLOW}Server is running in the background. Use 'killall node' to stop.${NC}"
}

# Create macOS app bundle
create_macos_app() {
    echo -e "${BLUE}📱 Creating macOS App Bundle...${NC}"
    
    APP_NAME="Retro AI Gemini"
    APP_DIR="$APP_NAME.app"
    
    # Create app structure
    mkdir -p "$APP_DIR/Contents/MacOS"
    mkdir -p "$APP_DIR/Contents/Resources"
    
    # Create Info.plist
    cat > "$APP_DIR/Contents/Info.plist" << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>RetroAI</string>
    <key>CFBundleIdentifier</key>
    <string>com.unifiedai.retro-gemini</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOL

    # Create launcher script
    cat > "$APP_DIR/Contents/MacOS/RetroAI" << EOL
#!/bin/bash
cd "\$(dirname "\$0")/../../.."
./launch_enhanced.sh desktop
EOL

    chmod +x "$APP_DIR/Contents/MacOS/RetroAI"
    
    echo -e "${GREEN}✅ macOS App Bundle created: $APP_DIR${NC}"
    echo -e "${CYAN}You can now drag this to your Applications folder${NC}"
}

# Install as macOS service
install_service() {
    echo -e "${BLUE}⚙️  Installing as macOS LaunchAgent...${NC}"
    
    PLIST_NAME="com.unifiedai.retro-gemini"
    PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"
    CURRENT_DIR=$(pwd)
    
    cat > "$PLIST_PATH" << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>
    <key>ProgramArguments</key>
    <array>
        <string>$CURRENT_DIR/launch_enhanced.sh</string>
        <string>web</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$CURRENT_DIR</string>
    <key>RunAtLoad</key>
    <false/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/retro-ai-gemini.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/retro-ai-gemini-error.log</string>
</dict>
</plist>
EOL

    echo -e "${GREEN}✅ LaunchAgent installed${NC}"
    echo -e "${CYAN}Use 'launchctl load $PLIST_PATH' to start service${NC}"
    echo -e "${CYAN}Use 'launchctl unload $PLIST_PATH' to stop service${NC}"
}

# Main execution
main() {
    show_header
    check_dependencies
    check_environment
    
    # If arguments provided, execute directly
    case "${1:-}" in
        "web"|"--web"|"-w")
            launch_web
            exit 0
            ;;
        "desktop"|"--desktop"|"-d")
            launch_desktop
            exit 0
            ;;
        "browser"|"--browser"|"-br")
            open_in_browser
            exit 0
            ;;
        "build"|"--build"|"-b")
            build_application
            exit 0
            ;;
        "app"|"--app"|"-a")
            create_macos_app
            exit 0
            ;;
        "service"|"--service"|"-s")
            install_service
            exit 0
            ;;
        "test"|"--test"|"-t")
            run_tests
            exit 0
            ;;
        "info"|"--info"|"-i")
            show_system_info
            exit 0
            ;;
        "help"|"--help"|"-h")
            echo "Usage: $0 [web|desktop|browser|build|app|service|test|info|help]"
            echo ""
            echo "Options:"
            echo "  web      Launch web version"
            echo "  desktop  Launch desktop version"
            echo "  browser  Open in browser (background server)"
            echo "  build    Build for production"
            echo "  app      Create macOS App Bundle"
            echo "  service  Install as macOS Service"
            echo "  test     Run development tests"
            echo "  info     Show system information"
            echo "  help     Show this help message"
            exit 0
            ;;
    esac
    
    # Interactive menu
    while true; do
        echo ""
        show_menu
        read -r choice
        
        case $choice in
            1)
                launch_web
                break
                ;;
            2)
                launch_desktop
                break
                ;;
            3)
                open_in_browser
                break
                ;;
            4)
                build_application
                ;;
            5)
                create_macos_app
                ;;
            6)
                install_service
                ;;
            7)
                run_tests
                ;;
            8)
                show_system_info
                ;;
            9)
                open_documentation
                ;;
            q|Q)
                echo -e "${GREEN}Thanks for using Retro AI Gemini! 🚀${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option. Please try again.${NC}"
                ;;
        esac
    done
}

# Error handling
trap 'echo -e "\n${RED}Script interrupted${NC}"; exit 1' INT

# Run main function
main "$@"
