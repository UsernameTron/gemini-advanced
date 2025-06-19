import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Command processing
  processCommand: (command: string) => ipcRenderer.invoke('process-command', command),
  
  // File operations
  uploadImage: () => ipcRenderer.invoke('upload-image'),
  
  // Status and info
  getStatus: () => ipcRenderer.invoke('get-status'),
  
  // Event listeners
  onSaveSession: (callback: () => void) => {
    ipcRenderer.on('save-session', callback);
    return () => ipcRenderer.removeListener('save-session', callback);
  },
  
  onExportGallery: (callback: () => void) => {
    ipcRenderer.on('export-gallery', callback);
    return () => ipcRenderer.removeListener('export-gallery', callback);
  },
  
  onShowCommandPalette: (callback: (command: string) => void) => {
    ipcRenderer.on('show-command-palette', (event, command) => callback(command));
    return () => ipcRenderer.removeListener('show-command-palette', (event, command) => callback(command));
  },
  
  onOpenPreferences: (callback: () => void) => {
    ipcRenderer.on('open-preferences', callback);
    return () => ipcRenderer.removeListener('open-preferences', callback);
  },
  
  onShowHelp: (callback: () => void) => {
    ipcRenderer.on('show-help', callback);
    return () => ipcRenderer.removeListener('show-help', callback);
  }
});

// Type definitions for TypeScript
declare global {
  interface Window {
    electronAPI: {
      processCommand: (command: string) => Promise<any>;
      uploadImage: () => Promise<string | null>;
      getStatus: () => Promise<{
        imageEngine: boolean;
        commandProcessor: boolean;
        server: boolean;
      }>;
      onSaveSession: (callback: () => void) => () => void;
      onExportGallery: (callback: () => void) => () => void;
      onShowCommandPalette: (callback: (command: string) => void) => () => void;
      onOpenPreferences: (callback: () => void) => () => void;
      onShowHelp: (callback: () => void) => () => void;
    };
  }
}
