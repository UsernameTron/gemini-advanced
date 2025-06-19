# 🎛️ Retro AI Desktop - Setup & Launch Guide

## Quick Start (3 Steps)

### 1. **Set Your Google API Key**
```bash
# Edit the .env file
nano .env

# Replace this line:
GOOGLE_API_KEY=your_google_api_key_here

# With your actual API key:
GOOGLE_API_KEY=AIza...your_actual_key_here
```

**Get API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)

### 2. **Launch the Application**

**Option A: Desktop Launcher (Recommended)**
```bash
# Double-click this file in Finder:
desktop-launcher.command

# Or run from terminal:
./desktop-launcher.command
```

**Option B: Command Line**
```bash
# Build and start:
npm run build
npm start

# Or use the launch script:
./launch.sh
```

**Option C: Development Mode**
```bash
# For development with hot reload:
npm run dev
```

### 3. **Access the Interface**

The application will open in two ways:
- **🖥️ Desktop App**: Electron window opens automatically
- **🌐 Web Browser**: Navigate to `http://localhost:3000`

---

## 🚀 Usage Examples

Once launched, try these commands in the terminal:

### **Image Generation**
```bash
# Gemini conversational generation
GEN a cyberpunk cityscape with flying cars at sunset

# Imagen high-quality generation
IMAGEN professional headshot of a business executive, 4K HDR

# Professional photography
PHOTO portrait a woman in business attire
PHOTO landscape mountain range during golden hour
PHOTO macro a dewdrop on a leaf

# Artistic styles
ART cat impressionist
ART robot renaissance
STYLE cyberpunk a coffee shop
```

### **Image Editing**
```bash
# Upload an image first
UPLOAD

# Then edit (replace 'img_123abc' with your session ID)
EDIT img_123abc add a rainbow in the sky
EDIT img_123abc change the lighting to golden hour
EDIT img_123abc remove the background
```

### **Advanced Features**
```bash
# Logo generation
LOGO TechCorp modern software
LOGO MediCore minimalist healthcare

# Batch generation
BATCH 4 variations of a sunset over ocean

# Text in images
TEXT Create a poster with "Welcome to the Future"

# System commands
HELP      # Show all commands
STATUS    # System status
GALLERY   # View image gallery
CLEAR     # Clear terminal
```

---

## 🔧 Building for Distribution

### **Create macOS Installer**
```bash
# Build distributable .dmg file
./build-dist.sh

# The installer will be created in release/
# Share the .dmg file with other users
```

### **Desktop Integration**
```bash
# Copy launcher to desktop
cp desktop-launcher.command ~/Desktop/

# Or create an alias
ln -s $(pwd)/desktop-launcher.command ~/Desktop/RetroAI.command
```

---

## 🎯 Key Features Available

### **🤖 AI Engines**
- ✅ **Gemini 2.0 Flash**: Conversational image generation
- ✅ **Imagen 3.0**: High-quality specialized generation
- ✅ **Multi-turn Editing**: Conversational image modifications

### **🎨 Creative Tools**
- ✅ **Style Transfer**: Apply artistic styles
- ✅ **Professional Photography**: Portrait, macro, landscape modes
- ✅ **Logo Design**: Business logo generation
- ✅ **Quality Controls**: 4K, HDR, aspect ratios
- ✅ **Text Integration**: Add text to images

### **🖥️ Interface Features**
- ✅ **1970s Retro Terminal**: Authentic monospace design
- ✅ **Command History**: Navigate with ↑/↓ arrows
- ✅ **Auto-completion**: Press Tab for suggestions
- ✅ **Image Gallery**: View and manage generated images
- ✅ **Session Management**: Save and restore work sessions

### **📱 Platform Integration**
- ✅ **Native macOS App**: Built with Electron
- ✅ **Web Browser Access**: Works in any modern browser
- ✅ **File Management**: Upload, export, organize images
- ✅ **Keyboard Shortcuts**: Quick access to features

---

## 🛠️ Troubleshooting

### **App Won't Start**
```bash
# Check Node.js version (requires 18+)
node --version

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild application
npm run build
```

### **API Errors**
```bash
# Verify API key is set
echo $GOOGLE_API_KEY

# Check .env file
cat .env

# Test API connection
npm start
# Then type: STATUS
```

### **Build Issues**
```bash
# Clean and rebuild
rm -rf dist/ release/
npm run build

# Check for TypeScript errors
npm run build:main
```

### **Permission Issues (macOS)**
```bash
# Make scripts executable
chmod +x *.sh *.command

# Allow app to run (if blocked by security)
# System Preferences → Security & Privacy → General
# Click "Allow" next to the blocked app
```

---

## 📁 Project Structure

```
retro-ai-desktop/
├── 🚀 desktop-launcher.command    # Double-click to launch
├── 🔧 launch.sh                   # Alternative launcher
├── 📦 build-dist.sh               # Build installer
├── ⚙️  .env                       # Your API key goes here
├── 📖 README.md                   # Full documentation
├── 📋 SETUP.md                    # This file
│
├── src/
│   ├── main/                      # Electron backend
│   └── renderer/                  # Web frontend
│
├── dist/                          # Built application
├── release/                       # Distribution packages
└── assets/                        # Icons and images
```

---

## 🎮 Keyboard Shortcuts

- **Ctrl+Space**: Quick command palette
- **Ctrl+U**: Upload image
- **Ctrl+S**: Save session
- **Ctrl+,**: Open preferences
- **F1**: Show help
- **↑/↓**: Navigate command history
- **Tab**: Auto-complete commands
- **Ctrl+L**: Clear terminal
- **Esc**: Clear current input

---

## 🌟 Next Steps

1. **Set up your Google API key** in `.env`
2. **Launch** with `./desktop-launcher.command`
3. **Try the example commands** above
4. **Upload an image** and test editing features
5. **Generate your first AI image** with `GEN` or `IMAGEN`
6. **Build a distributable** with `./build-dist.sh`

---

**🎛️ Welcome to the future of AI-powered creativity with a retro twist!**
