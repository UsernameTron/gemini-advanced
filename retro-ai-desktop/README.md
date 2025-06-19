# Retro AI Desktop - 1970s Command Center

A standalone desktop application featuring a 1970s-style terminal interface with full **Gemini & Imagen integration** for AI-powered image generation, editing, and multimodal capabilities.

## Features

### 🎛️ 1970s Retro Terminal Interface
- Authentic monospace terminal design with green phosphor styling
- ASCII art headers and retro command prompts
- Real-time command processing with visual feedback
- Command history and auto-completion

### 🤖 Dual AI Engine Integration
- **Gemini 2.0 Flash**: Conversational image generation with context awareness
- **Imagen 3.0**: High-quality specialized image generation
- Seamless switching between engines based on use case

### 🖼️ Complete Image Generation Suite
- **Text-to-Image**: Generate images from natural language descriptions
- **Image Editing**: Multi-turn conversational editing of uploaded images
- **Style Transfer**: Apply artistic styles and transformations
- **Professional Photography**: Portrait, macro, landscape, and street photography modes
- **Logo Design**: Parameterized business logo generation
- **Batch Processing**: Generate multiple variations efficiently

### 🎨 Advanced Creative Features
- **Artistic Styles**: Impressionist, Renaissance, Pop Art, Cyberpunk, Art Deco
- **Quality Controls**: 4K, HDR, aspect ratios (1:1, 3:4, 4:3, 9:16, 16:9)
- **Text Integration**: Add custom text to generated images
- **Material Simulation**: Create objects in different materials and textures

### 🖥️ Desktop Integration
- **Native macOS App**: Built with Electron for seamless desktop experience
- **Web Browser Navigation**: Access through localhost web interface
- **File Management**: Upload, export, and organize image galleries
- **Session Management**: Save and restore work sessions
- **Keyboard Shortcuts**: Quick access to all features

## Installation & Setup

### Prerequisites
```bash
# macOS with Node.js 18+ installed
node --version  # Should be 18.0.0 or higher
npm --version   # Should be 9.0.0 or higher
```

### Quick Start
```bash
# Clone and setup
git clone <your-repo-url>
cd retro-ai-desktop

# Install dependencies
npm install

# Set up environment
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env

# Build and run
npm run build
npm start
```

### Build for Distribution
```bash
# Build macOS app (.dmg)
npm run dist:mac

# The built app will be in the `release/` directory
```

## Usage Guide

### Command Reference

#### Image Generation
```bash
# Gemini conversational generation
GEN a cyberpunk cityscape with flying cars at sunset

# Imagen high-quality generation  
IMAGEN professional headshot of a business executive, 4K HDR

# Professional photography
PHOTO portrait a business professional
PHOTO macro a dewdrop on a leaf
PHOTO landscape mountain range during golden hour

# Artistic styles
ART cat impressionist
ART robot renaissance
STYLE cyberpunk a coffee shop
```

#### Image Editing
```bash
# Upload an image first, then edit
UPLOAD  # Use the upload button or this command
EDIT img_123abc add a rainbow in the sky
EDIT img_123abc change the lighting to golden hour
EDIT img_123abc remove the background
```

#### Advanced Features
```bash
# Logo generation
LOGO TechCorp modern software
LOGO MediCore minimalist healthcare

# Batch generation
BATCH 4 variations of a sunset over ocean

# Parameterized generation
PARAM A {minimalist} logo for a {healthcare} company with text {MediCore}

# Text in images
TEXT Create a poster with "Welcome to the Future"
```

#### System Commands
```bash
HELP      # Show full command reference
STATUS    # System status and diagnostics
GALLERY   # View image gallery
HISTORY   # Command history
CLEAR     # Clear terminal
UPLOAD    # Upload image for editing
```

### Keyboard Shortcuts
- **Ctrl+Space**: Quick command palette
- **Ctrl+U**: Upload image
- **Ctrl+S**: Save session
- **Ctrl+,**: Open preferences
- **F1**: Show help
- **↑/↓**: Navigate command history
- **Tab**: Auto-complete commands
- **Ctrl+L**: Clear terminal

## Integration with Existing Systems

This application is designed to integrate with your existing **VectorDBRAG agent ecosystem**. The command processor includes handlers for:

- **CEO Agent**: Strategic analysis and decision making
- **Code Analysis**: Security reviews and optimization
- **Debug Agent**: Error diagnosis and troubleshooting  
- **Research Agent**: Information gathering and insights
- **Test Generator**: Automated test case creation

## Architecture

```
retro-ai-desktop/
├── src/
│   ├── main/           # Electron main process
│   │   ├── main.ts     # Application entry point
│   │   ├── server.ts   # Express/Socket.IO server
│   │   ├── image-engine.ts      # Gemini/Imagen integration
│   │   ├── command-processor.ts # Command routing
│   │   └── preload.ts  # IPC bridge
│   ├── renderer/       # Web frontend
│   │   ├── index.html  # Main interface
│   │   ├── styles/     # 1970s retro CSS
│   │   └── js/         # Interactive components
│   └── shared/         # Type definitions
├── assets/             # Icons and images
├── uploads/            # User uploaded images
├── generated/          # AI generated content
└── release/            # Built applications
```

## API Integration

### Google AI Configuration
```typescript
// Environment setup
GOOGLE_API_KEY=your_api_key_here

// Gemini 2.0 Flash for conversational generation
const geminiModel = genai.getGenerativeModel({ 
  model: "gemini-2.0-flash-exp" 
});

// Imagen 3.0 for high-quality generation
const imagenModel = "imagen-3.0-generate-002";
```

### RESTful API Endpoints
```bash
POST /api/command        # Execute terminal commands
POST /api/upload         # Upload images for editing
GET  /api/status         # System status
GET  /api/gallery        # Image gallery
```

### WebSocket Events
```javascript
socket.emit('command', { command: 'GEN sunset over mountains' });
socket.on('command-result', (data) => { /* handle result */ });
socket.emit('image-upload', { imageData: base64Data });
socket.on('image-result', (data) => { /* handle image */ });
```

## Development

### Development Mode
```bash
# Run in development with hot reload
npm run dev

# This starts:
# - TypeScript compilation in watch mode
# - Electron app with DevTools
# - Express server on localhost:3000
```

### Building Components
```bash
# Build main process only
npm run build:main

# Build renderer process only  
npm run build:renderer

# Build everything
npm run build
```

### Debugging
- Electron DevTools: `Ctrl+Shift+I`
- Backend logs: Check terminal output
- Network requests: Browser DevTools Network tab

## Deployment

### Creating Installer
```bash
# Build for macOS
npm run dist:mac

# Generated files:
# - release/Retro AI Desktop-1.0.0.dmg     # Installer
# - release/mac/Retro AI Desktop.app       # Application bundle
```

### Distribution
1. **Code Signing**: Configure developer certificates in `electron-builder`
2. **Notarization**: Set up Apple notarization for macOS distribution
3. **Auto-Updates**: Integrate with update servers if needed

## Troubleshooting

### Common Issues

**API Key Not Working**
```bash
# Check environment variable
echo $GOOGLE_API_KEY

# Verify in app preferences
# Open app → Cmd+, → API Configuration
```

**Images Not Generating**
- Verify Google AI API quota and billing
- Check network connectivity
- Review terminal output for error messages

**Build Failures**
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# Rebuild native modules
npm run postinstall
```

**App Won't Start**
```bash
# Check Electron installation
npx electron --version

# Run in debug mode
DEBUG=* npm start
```

## Contributing

This application serves as a foundation for AI-powered desktop tools. Key extension points:

1. **Agent Integration**: Connect to your VectorDBRAG system
2. **Custom Commands**: Add domain-specific command handlers  
3. **UI Themes**: Create additional retro terminal themes
4. **Export Formats**: Support additional image and data formats
5. **Cloud Integration**: Add cloud storage and sharing features

## License

MIT License - See LICENSE file for details.

---

**Built with**: Electron, TypeScript, Express, Socket.IO, Google AI APIs

**Compatible with**: macOS 10.14+, requires Node.js 18+
