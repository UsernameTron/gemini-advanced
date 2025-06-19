# 🖥️ Desktop Shortcuts - Usage Guide

## 🚀 Available Desktop Shortcuts

Your Retro AI Desktop now has **three convenient launch options**:

### 1. 📱 **Retro AI Web.app** (Recommended)
- **Location**: Desktop & Applications folder
- **Description**: Native macOS app that launches the web interface
- **Usage**: Double-click to launch
- **Features**: 
  - Can be added to Dock
  - Native macOS app experience
  - Automatic browser opening
  - Status monitoring

### 2. 🌐 **Retro AI Desktop - Web Interface.command**
- **Location**: Desktop
- **Description**: Terminal-based launcher script
- **Usage**: Double-click to run in Terminal
- **Features**:
  - Detailed startup progress
  - Error diagnostics
  - Health checking
  - Manual control options

### 3. 🎯 **Original Desktop Launcher**
- **Location**: Project folder (`desktop-launcher.command`)
- **Description**: Full application launcher
- **Usage**: For development and debugging
- **Features**:
  - Complete project setup
  - Build validation
  - Environment checking

## 🎮 How to Use

### Quick Start (Recommended):
1. **Double-click** `Retro AI Web.app` on your Desktop
2. **Wait** for the application to start (15-30 seconds)
3. **Browser opens** automatically to http://localhost:3000
4. **Start creating** with commands like:
   - `GEN futuristic robot`
   - `IMAGEN beautiful landscape`
   - `UPLOAD` (to edit images)
   - `HELP` (for all commands)

### Add to Dock:
1. Drag `Retro AI Web.app` from Desktop to your Dock
2. Right-click the Dock icon → Options → Keep in Dock

### Stopping the Application:
- **Method 1**: Close the Electron application window
- **Method 2**: Close the browser tab and Terminal window
- **Method 3**: Run in Terminal: `pkill -f "electron.*retro-ai-desktop"`

## 🎨 Web Interface Features

Once launched, your 1970s AI Command Center provides:

**🤖 AI Generation:**
- **Gemini 2.0 Flash** for conversational image creation
- **Imagen 3.0** for high-quality professional output
- **Specialized modes** for photos, art, and logos

**🖼️ Image Management:**
- **Upload & Edit** existing images
- **Gallery view** of all creations
- **Export** images to your computer
- **Batch operations** for multiple images

**🎯 Command Interface:**
- **Auto-completion** for commands
- **Command history** with up/down arrows
- **Real-time responses** via WebSocket
- **Authentic 1970s terminal styling**

## 🔧 Troubleshooting

**If the app doesn't start:**
1. Check that your Google API key is set in `.env`
2. Try the Terminal launcher for detailed error messages
3. Ensure port 3000 is available
4. Run the comprehensive test: `./comprehensive-test.sh`

**If the browser doesn't open:**
- Manually navigate to http://localhost:3000
- Check if the Electron app window is visible

**For development:**
- Use `npm run dev` for hot-reloading
- Use `npm start` for production mode
- Check logs in the Terminal for debugging

## 🎉 Enjoy Your 1970s AI Experience!

Your retro command center combines the nostalgic computing aesthetic of 1970 with cutting-edge AI capabilities of 2024. Have fun creating amazing images with your authentic terminal interface! 🖥️✨
