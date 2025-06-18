# Retro AI Gemini Creative Agent

A standalone application featuring a retro terminal interface powered by Google Gemini AI. Experience the classic "SHALL WE PLAY A GAME?" aesthetic while leveraging cutting-edge AI capabilities for creative projects.

![Retro AI Terminal Interface](https://img.shields.io/badge/Interface-Retro%20Terminal-00ff41?style=for-the-badge&logo=terminal)
![Powered by Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285f4?style=for-the-badge&logo=google)
![macOS Optimized](https://img.shields.io/badge/Platform-macOS-000000?style=for-the-badge&logo=apple)

## ✅ DEPLOYMENT STATUS: COMPLETE & OPERATIONAL

**🎮 SYSTEM FULLY FUNCTIONAL** - All components tested and verified

### Current Running Status:
- ✅ **Web Interface**: http://localhost:8080 (Standalone browser access)
- ✅ **Desktop Application**: http://localhost:8082 (Electron app with native integration)
- ✅ **API Endpoints**: All REST endpoints operational
- ✅ **Google Gemini AI**: API integration validated and working
- ✅ **Terminal Interface**: Retro UI with authentic sound effects
- ✅ **macOS App Bundle**: `Retro AI Gemini.app` ready for Applications folder

### Recent Fixes Applied:
- ✅ Fixed `TerminalInterface.js` missing sound methods (`createBootSound`, `createErrorSound`)
- ✅ Resolved port conflicts between web (8080) and desktop (8082) modes
- ✅ Enhanced server configuration for multiple deployment scenarios
- ✅ Validated all API endpoints with live Gemini API calls
- ✅ Tested cross-platform compatibility and file upload functionality

### Launch Options:
```bash
# Web Browser Mode
npm run web          # Opens on http://localhost:8080

# Desktop Application
npm start            # Launches Electron app on port 8082

# Enhanced Launcher
./launch_enhanced.sh # Interactive menu with all options

# CLI Tool
node cli.js --help   # Command-line interface
```

## ✨ Features

### 🎮 Retro Terminal Experience
- Classic green-on-black terminal aesthetic
- Typewriter-style text animation
- Authentic sound effects and visual feedback
- "SHALL WE PLAY A GAME?" startup sequence

### 🤖 Google Gemini AI Integration
- **Text Generation**: Advanced conversational AI
- **Vision Analysis**: Brand material and image analysis
- **Creative Generation**: Content and concept creation
- **Campaign Orchestration**: Strategic planning assistance

### 🖥️ Multiple Launch Options
- **Web Browser**: Access via any modern browser
- **Desktop App**: Native Electron application
- **macOS App Bundle**: Drag-and-drop installation
- **Background Service**: Always-available web service

### 🎨 Creative Missions
- **Brand Analysis**: Decode visual identity and strategy
- **Creative Generation**: Generate concepts and copy
- **Campaign Development**: Build comprehensive strategies
- **Visual Exploration**: Analyze and enhance brand materials

## 🌟 Features

### 🎮 Retro Terminal Experience
- Authentic retro computer terminal aesthetic
- Typing effects with sound feedback
- Classic green-on-black color scheme
- Immersive sci-fi computer interface

### 🤖 Google Gemini AI Integration
- **Text Generation**: Advanced conversational AI capabilities
- **Vision Analysis**: Upload and analyze images with AI
- **Multi-Modal Understanding**: Process text, images, and creative requests
- **Creative Assistance**: Brand analysis, campaign development, code creation

### 🎯 Specialized Missions
- **Brand Visual Analysis**: Analyze logos, marketing materials, and brand assets
- **Creative Asset Generation**: Conceptual design and creative direction
- **Campaign Strategy Development**: Marketing and creative campaign planning
- **Code Creation & Analysis**: Programming assistance and code review
- **Document Processing**: Analyze and extract insights from documents

### 🖥️ Dual Interface Options
- **Desktop Application**: Electron-based standalone app with native OS integration
- **Web Browser**: Access via any modern web browser
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ installed
- Google API Key for Gemini AI
- Modern web browser (for web version)

### Installation

1. **Clone or download the application**:
   ```bash
   cd retro-ai-gemini
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure your Google API key**:
   - The API key is already configured in the `.env` file
   - For custom setup, edit `.env` and update `GOOGLE_API_KEY`

4. **Run the application**:

   **Desktop Version**:
   ```bash
   npm start
   ```

   **Web Browser Version**:
   ```bash
   npm run web
   ```
   Then open http://localhost:8080 in your browser

## 🎮 Usage Guide

### Getting Started
1. Launch the application (desktop or web)
2. Wait for the initialization sequence
3. See the classic "SHALL WE PLAY A GAME?" prompt
4. Type your creative challenge or select a mission

### Mission Types

#### Brand Visual Analysis
```
"analyze my brand logo"
"review this marketing material"
"brand strategy insights"
```

#### Creative Asset Generation
```
"create a campaign concept for..."
"generate design ideas for..."
"creative brief for..."
```

#### Campaign Strategy Development
```
"campaign strategy for..."
"marketing plan for..."
"audience targeting for..."
```

#### Code Creation & Analysis
```
"create a website for..."
"analyze this code"
"build a script that..."
```

### Special Commands
- `help` - Show available commands
- `status` - Display system status
- `clear` - Clear the terminal screen
- `export` - Save conversation history
- `new session` - Start fresh
- `sound on/off` - Toggle audio effects

### File Upload
- Drag and drop images directly into the terminal
- Supports JPG, PNG, GIF, PDF, DOC, TXT files
- AI will automatically analyze uploaded content

## 🔧 Configuration

### Environment Variables (.env)
```env
GOOGLE_API_KEY=your_gemini_api_key_here
NODE_ENV=development
PORT=8080
DEBUG=true
THEME=retro
TERMINAL_STYLE=classic
```

### Customization Options
- **Sound Effects**: Toggle audio feedback on/off
- **Typing Speed**: Adjust terminal typing animation speed
- **Theme**: Classic green terminal or custom color schemes
- **Session Management**: Auto-save conversations

## 🛠️ Development

### Project Structure
```
retro-ai-gemini/
├── core/
│   └── GeminiAgent.js      # AI logic and conversation management
├── ui/
│   └── TerminalInterface.js # Retro terminal UI and effects
├── app.js                  # Main application controller
├── main.js                 # Electron desktop launcher
├── server.js               # Express web server
├── index.html              # Web interface entry point
├── package.json            # Dependencies and scripts
└── .env                    # Configuration
```

### Key Components

#### RetroAIAgent (core/GeminiAgent.js)
- Manages Google Gemini API integration
- Handles conversation history and context
- Processes different mission types
- Provides image analysis capabilities

#### RetroTerminalInterface (ui/TerminalInterface.js)
- Creates authentic retro terminal experience
- Handles typing effects and animations
- Manages sound effects and visual feedback
- Provides responsive design for different screen sizes

#### Main Application (app.js)
- Orchestrates AI agent and terminal interface
- Manages application state and user sessions
- Handles special commands and file uploads
- Coordinates mission workflows

### Building for Production
```bash
# Build desktop application
npm run build

# Start production web server
NODE_ENV=production npm run web
```

## 🎨 Creative Mission Examples

### Brand Analysis
Upload a logo or marketing material and ask:
- "Analyze this brand's visual identity"
- "What does this logo communicate about the brand?"
- "Suggest improvements for this design"

### Campaign Development
Describe your project:
- "Create a social media campaign for a tech startup"
- "Develop brand messaging for a sustainable fashion company"
- "Design a product launch strategy"

### Code Projects
Request programming help:
- "Build a responsive landing page"
- "Create a data visualization script"
- "Review this code for optimization"

## 🔊 Audio Experience

The application includes immersive audio effects:
- **Keystroke Sounds**: Authentic terminal typing audio
- **Notification Chimes**: Mission alerts and system notifications
- **Processing Sounds**: AI thinking and analysis feedback
- **Boot Sequence**: Retro computer startup sounds

## 📱 Cross-Platform Support

### Desktop Application
- Native OS integration with Electron
- Menu bar and keyboard shortcuts
- File system access for uploads and exports
- System notifications

### Web Browser
- Works in any modern browser
- Responsive design for mobile devices
- Progressive Web App capabilities
- Bookmark and share conversations

## 🚀 Advanced Features

### Session Management
- Automatic conversation saving
- Export chat history as JSON
- Resume sessions across restarts
- Share conversations with team members

### AI Capabilities
- Context-aware responses
- Multi-turn conversations
- Image analysis and description
- Creative concept generation
- Technical documentation creation

### Performance Optimization
- Lazy loading of AI models
- Efficient conversation history management
- Optimized terminal rendering
- Minimal resource usage

## 🆘 Troubleshooting

### Common Issues

1. **API Key Error**:
   ```
   Error: API key not configured
   Solution: Check .env file has valid GOOGLE_API_KEY
   ```

2. **Terminal Not Loading**:
   ```
   Check browser console for JavaScript errors
   Ensure all dependencies are installed
   ```

3. **Sound Not Working**:
   ```
   Browser may block audio without user interaction
   Click anywhere on the page to enable audio
   ```

4. **File Upload Fails**:
   ```
   Check file size (max 10MB)
   Ensure supported file format
   ```

### Debug Mode
```bash
DEBUG=true npm start
```

## 🤝 Contributing

This is a standalone application built for the UnifiedAIPlatform project. For modifications or enhancements:

1. Fork the repository
2. Create a feature branch
3. Test thoroughly across platforms
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Links

- Google Gemini AI: https://ai.google.dev/
- Electron: https://electronjs.org/
- Node.js: https://nodejs.org/

---

**Created by UnifiedAIPlatform** | **Powered by Google Gemini AI**
