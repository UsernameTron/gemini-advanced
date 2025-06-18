/**
 * Electron Main Process
 * Desktop launcher for the Retro AI Gemini application
 */

const { app, BrowserWindow, Menu, shell, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Load environment variables
require('dotenv').config();

class RetroAIDesktopApp {
    constructor() {
        this.mainWindow = null;
        this.webServer = null;
        this.serverPort = process.env.ELECTRON_PORT || 8082; // Use different port for Electron
    }

    async initialize() {
        // Set up app event handlers
        app.whenReady().then(() => this.createWindow());
        
        app.on('window-all-closed', () => {
            if (process.platform !== 'darwin') {
                this.cleanup();
                app.quit();
            }
        });

        app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0) {
                this.createWindow();
            }
        });

        // Start web server for the application
        this.startWebServer();
    }

    createWindow() {
        // Create the main application window
        this.mainWindow = new BrowserWindow({
            width: 1400,
            height: 900,
            minWidth: 800,
            minHeight: 600,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false,
                webSecurity: true
            },
            icon: path.join(__dirname, 'assets', 'icon.png'),
            title: 'NEXUS Creative AI - Retro Terminal',
            titleBarStyle: 'hiddenInset',
            backgroundColor: '#000000',
            show: false // Don't show until ready
        });

        // Load the application
        const appUrl = `http://localhost:${this.serverPort}`;
        this.mainWindow.loadURL(appUrl);

        // Show window when ready
        this.mainWindow.once('ready-to-show', () => {
            this.mainWindow.show();
            
            // Focus the window
            if (process.platform === 'darwin') {
                app.dock.show();
            }
        });

        // Handle window closed
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });

        // Open external links in browser
        this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
            shell.openExternal(url);
            return { action: 'deny' };
        });

        // Set up menu
        this.createMenu();

        // Development tools
        if (process.env.NODE_ENV === 'development') {
            this.mainWindow.webContents.openDevTools();
        }
    }

    startWebServer() {
        // Start Express server for the web interface
        try {
            // Set a different port for desktop mode to avoid conflicts
            const desktopPort = process.env.DESKTOP_PORT || 8081;
            
            this.webServer = spawn('node', ['server.js'], {
                cwd: __dirname,
                stdio: 'inherit',
                env: { 
                    ...process.env, 
                    PORT: desktopPort,
                    DESKTOP_MODE: 'true'
                }
            });

            // Update server port for this instance
            this.serverPort = desktopPort;

            this.webServer.on('error', (error) => {
                console.error('Failed to start web server:', error);
                this.showErrorDialog('Server Error', 'Failed to start the web server. Please check your configuration.');
            });

            this.webServer.on('exit', (code) => {
                if (code !== 0) {
                    console.error(`Web server exited with code ${code}`);
                }
            });

            console.log(`Web server starting on port ${this.serverPort}`);
        } catch (error) {
            console.error('Error starting web server:', error);
        }
    }

    createMenu() {
        const template = [
            {
                label: 'File',
                submenu: [
                    {
                        label: 'New Session',
                        accelerator: 'CmdOrCtrl+N',
                        click: () => {
                            this.mainWindow.webContents.executeJavaScript(
                                'window.retroAI && window.retroAI.resetSession()'
                            );
                        }
                    },
                    {
                        label: 'Export Session',
                        accelerator: 'CmdOrCtrl+S',
                        click: () => {
                            this.mainWindow.webContents.executeJavaScript(
                                'window.retroAI && window.retroAI.handleExportSession()'
                            );
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Quit',
                        accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                        click: () => {
                            this.cleanup();
                            app.quit();
                        }
                    }
                ]
            },
            {
                label: 'Edit',
                submenu: [
                    { role: 'cut' },
                    { role: 'copy' },
                    { role: 'paste' },
                    { type: 'separator' },
                    { role: 'selectall' }
                ]
            },
            {
                label: 'View',
                submenu: [
                    {
                        label: 'Clear Screen',
                        accelerator: 'CmdOrCtrl+L',
                        click: () => {
                            this.mainWindow.webContents.executeJavaScript(
                                'window.retroAI && window.retroAI.terminal.clearScreen()'
                            );
                        }
                    },
                    { type: 'separator' },
                    { role: 'reload' },
                    { role: 'forceReload' },
                    { role: 'toggleDevTools' },
                    { type: 'separator' },
                    { role: 'resetZoom' },
                    { role: 'zoomIn' },
                    { role: 'zoomOut' },
                    { type: 'separator' },
                    { role: 'togglefullscreen' }
                ]
            },
            {
                label: 'AI',
                submenu: [
                    {
                        label: 'System Status',
                        click: () => {
                            this.mainWindow.webContents.executeJavaScript(
                                'window.retroAI && window.retroAI.displaySystemStatus()'
                            );
                        }
                    },
                    {
                        label: 'Help',
                        accelerator: 'F1',
                        click: () => {
                            this.mainWindow.webContents.executeJavaScript(
                                'window.retroAI && window.retroAI.displayHelp()'
                            );
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Toggle Sound',
                        click: () => {
                            this.mainWindow.webContents.executeJavaScript(
                                'window.retroAI && window.retroAI.terminal.toggleSound()'
                            );
                        }
                    }
                ]
            },
            {
                label: 'Window',
                submenu: [
                    { role: 'minimize' },
                    { role: 'close' }
                ]
            },
            {
                label: 'Help',
                submenu: [
                    {
                        label: 'About NEXUS Creative AI',
                        click: () => {
                            this.showAboutDialog();
                        }
                    },
                    {
                        label: 'Documentation',
                        click: () => {
                            shell.openExternal('https://github.com/UsernameTron/gemini');
                        }
                    },
                    {
                        label: 'Report Issue',
                        click: () => {
                            shell.openExternal('https://github.com/UsernameTron/gemini/issues');
                        }
                    }
                ]
            }
        ];

        // macOS specific menu adjustments
        if (process.platform === 'darwin') {
            template.unshift({
                label: app.getName(),
                submenu: [
                    { role: 'about' },
                    { type: 'separator' },
                    { role: 'services' },
                    { type: 'separator' },
                    { role: 'hide' },
                    { role: 'hideothers' },
                    { role: 'unhide' },
                    { type: 'separator' },
                    { role: 'quit' }
                ]
            });

            // Window menu
            template[5].submenu = [
                { role: 'close' },
                { role: 'minimize' },
                { role: 'zoom' },
                { type: 'separator' },
                { role: 'front' }
            ];
        }

        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }

    showAboutDialog() {
        dialog.showMessageBox(this.mainWindow, {
            type: 'info',
            title: 'About NEXUS Creative AI',
            message: 'NEXUS Creative AI - Retro Terminal',
            detail: `
Version: 1.0.0
A retro-styled AI creative assistant powered by Google Gemini.

Built with:
- Electron
- Google Generative AI
- JavaScript ES6+

Created by UnifiedAIPlatform
            `.trim(),
            buttons: ['OK']
        });
    }

    showErrorDialog(title, message) {
        dialog.showErrorBox(title, message);
    }

    cleanup() {
        // Clean up resources
        if (this.webServer) {
            this.webServer.kill();
            this.webServer = null;
        }
    }
}

// Create and initialize the application
const retroAIApp = new RetroAIDesktopApp();
retroAIApp.initialize();

// Handle certificate errors (for development)
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
    if (process.env.NODE_ENV === 'development') {
        // In development, ignore certificate errors
        event.preventDefault();
        callback(true);
    } else {
        // In production, use default behavior
        callback(false);
    }
});
