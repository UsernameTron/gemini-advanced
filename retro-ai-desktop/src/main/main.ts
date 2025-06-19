import { app, BrowserWindow, ipcMain, Menu, dialog } from 'electron';
import { join } from 'path';
import { config } from 'dotenv';
import { createServer } from './server';
import { RetroImageEngine } from './image-engine';
import { EnhancedCommandProcessor } from './command-processor';

// Load environment variables
config({ path: join(__dirname, '../../.env') });

interface AppState {
  mainWindow: BrowserWindow | null;
  server: any;
  imageEngine: RetroImageEngine | null;
  commandProcessor: EnhancedCommandProcessor | null;
}

class RetroAIDesktopApp {
  private state: AppState = {
    mainWindow: null,
    server: null,
    imageEngine: null,
    commandProcessor: null
  };

  constructor() {
    this.initializeApp();
  }

  private async initializeApp(): Promise<void> {
    // Handle app ready
    app.whenReady().then(() => {
      this.createMainWindow();
      this.setupMenu();
      this.initializeBackend();
      
      app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
          this.createMainWindow();
        }
      });
    });

    // Handle app window close
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    // Setup IPC handlers
    this.setupIpcHandlers();
  }

  private createMainWindow(): void {
    this.state.mainWindow = new BrowserWindow({
      width: 1400,
      height: 900,
      minWidth: 1200,
      minHeight: 800,
      title: 'Retro AI Desktop - 1970s Command Center',
      titleBarStyle: 'hiddenInset',
      backgroundColor: '#000000',
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: join(__dirname, 'preload.js'),
        webSecurity: true
      },
      icon: join(__dirname, '../../assets/icon.png'),
      show: false
    });

    // Load the application
    const port = process.env.PORT || 3001;
    this.state.mainWindow.loadURL(`http://localhost:${port}`);

    // Show window when ready
    this.state.mainWindow.once('ready-to-show', () => {
      this.state.mainWindow?.show();
      
      // Open DevTools in development
      if (process.env.NODE_ENV === 'development') {
        this.state.mainWindow?.webContents.openDevTools();
      }
    });

    // Handle window closed
    this.state.mainWindow.on('closed', () => {
      this.state.mainWindow = null;
    });
  }

  private setupMenu(): void {
    const template = [
      {
        label: 'Retro AI Desktop',
        submenu: [
          { role: 'about' },
          { type: 'separator' },
          { 
            label: 'Preferences',
            accelerator: 'CmdOrCtrl+,',
            click: () => this.openPreferences()
          },
          { type: 'separator' },
          { role: 'quit' }
        ]
      },
      {
        label: 'File',
        submenu: [
          {
            label: 'Upload Image',
            accelerator: 'CmdOrCtrl+O',
            click: () => this.uploadImage()
          },
          {
            label: 'Save Session',
            accelerator: 'CmdOrCtrl+S',
            click: () => this.saveSession()
          },
          { type: 'separator' },
          {
            label: 'Export Gallery',
            click: () => this.exportGallery()
          }
        ]
      },
      {
        label: 'Edit',
        submenu: [
          { role: 'undo' },
          { role: 'redo' },
          { type: 'separator' },
          { role: 'cut' },
          { role: 'copy' },
          { role: 'paste' }
        ]
      },
      {
        label: 'View',
        submenu: [
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
        label: 'AI Commands',
        submenu: [
          {
            label: 'Generate Image (Gemini)',
            accelerator: 'CmdOrCtrl+G',
            click: () => this.showCommandPalette('GEN')
          },
          {
            label: 'Generate Image (Imagen)',
            accelerator: 'CmdOrCtrl+I',
            click: () => this.showCommandPalette('IMAGEN')
          },
          {
            label: 'Edit Image',
            accelerator: 'CmdOrCtrl+E',
            click: () => this.showCommandPalette('EDIT')
          },
          { type: 'separator' },
          {
            label: 'Code Analysis',
            accelerator: 'CmdOrCtrl+Shift+C',
            click: () => this.showCommandPalette('CODE')
          },
          {
            label: 'Debug Assistance',
            accelerator: 'CmdOrCtrl+Shift+D',
            click: () => this.showCommandPalette('DEBUG')
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
            label: 'Command Reference',
            click: () => this.showHelp()
          },
          {
            label: 'About Retro AI Desktop',
            click: () => this.showAbout()
          }
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template as any);
    Menu.setApplicationMenu(menu);
  }

  private async initializeBackend(): Promise<void> {
    try {
      // Initialize image engine
      this.state.imageEngine = new RetroImageEngine();
      
      // Initialize command processor with existing agent factory
      this.state.commandProcessor = new EnhancedCommandProcessor(
        null, // Will integrate with your existing agent factory
        this.state.imageEngine
      );

      // Start the web server
      this.state.server = await createServer({
        imageEngine: this.state.imageEngine,
        commandProcessor: this.state.commandProcessor
      });

      console.log('Backend services initialized successfully');
    } catch (error) {
      console.error('Failed to initialize backend:', error);
      dialog.showErrorBox('Initialization Error', 
        'Failed to initialize AI services. Please check your API keys and try again.');
    }
  }

  private setupIpcHandlers(): void {
    ipcMain.handle('process-command', async (event, command: string) => {
      if (!this.state.commandProcessor) {
        throw new Error('Command processor not initialized');
      }
      return await this.state.commandProcessor.processCommand(command);
    });

    ipcMain.handle('upload-image', async () => {
      return await this.uploadImage();
    });

    ipcMain.handle('get-status', async () => {
      return {
        imageEngine: !!this.state.imageEngine,
        commandProcessor: !!this.state.commandProcessor,
        server: !!this.state.server
      };
    });
  }

  private async uploadImage(): Promise<string | null> {
    if (!this.state.mainWindow) return null;

    const result = await dialog.showOpenDialog(this.state.mainWindow, {
      title: 'Upload Image for Editing',
      filters: [
        { name: 'Images', extensions: ['jpg', 'jpeg', 'png', 'gif', 'bmp'] }
      ],
      properties: ['openFile']
    });

    if (!result.canceled && result.filePaths.length > 0) {
      return result.filePaths[0];
    }
    return null;
  }

  private saveSession(): void {
    this.state.mainWindow?.webContents.send('save-session');
  }

  private exportGallery(): void {
    this.state.mainWindow?.webContents.send('export-gallery');
  }

  private showCommandPalette(command: string): void {
    this.state.mainWindow?.webContents.send('show-command-palette', command);
  }

  private openPreferences(): void {
    this.state.mainWindow?.webContents.send('open-preferences');
  }

  private showHelp(): void {
    this.state.mainWindow?.webContents.send('show-help');
  }

  private showAbout(): void {
    dialog.showMessageBox(this.state.mainWindow!, {
      type: 'info',
      title: 'About Retro AI Desktop',
      message: 'Retro AI Desktop v1.0.0',
      detail: '1970s-style AI Command Center with Gemini & Imagen Integration\n\nBuilt with Electron, TypeScript, and the power of Google AI.'
    });
  }
}

// Initialize the application
new RetroAIDesktopApp();
