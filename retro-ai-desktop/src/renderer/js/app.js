class RetroAIApp {
    constructor() {
        this.socket = null;
        this.connectionStatus = 'disconnected';
        this.init();
    }

    init() {
        this.setupSocketConnection();
        this.setupEventListeners();
        this.setupElectronAPI();
        this.addContextMenuStyles();
    }

    setupSocketConnection() {
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                this.connectionStatus = 'connected';
                this.updateConnectionStatus();
                console.log('Connected to server');
            });

            this.socket.on('disconnect', () => {
                this.connectionStatus = 'disconnected';
                this.updateConnectionStatus();
                console.log('Disconnected from server');
            });

            this.socket.on('command-result', (data) => {
                this.handleSocketCommandResult(data);
            });

            this.socket.on('image-result', (data) => {
                this.handleSocketImageResult(data);
            });
        }
    }

    setupEventListeners() {
        // Command palette buttons
        document.querySelectorAll('.palette-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const command = btn.dataset.command;
                this.executeQuickCommand(command);
            });
        });

        // Help modal
        const helpModal = document.getElementById('help-modal');
        const closeBtn = helpModal.querySelector('.close-btn');
        
        closeBtn.addEventListener('click', () => {
            helpModal.classList.add('hidden');
        });

        // Close modal on outside click
        helpModal.addEventListener('click', (e) => {
            if (e.target === helpModal) {
                helpModal.classList.add('hidden');
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleGlobalKeydown(e);
        });

        // Prevent default drag and drop
        document.addEventListener('dragover', (e) => e.preventDefault());
        document.addEventListener('drop', (e) => e.preventDefault());
    }

    setupElectronAPI() {
        if (window.electronAPI) {
            // Set up Electron API event listeners
            window.electronAPI.onSaveSession(() => {
                this.saveSession();
            });

            window.electronAPI.onExportGallery(() => {
                if (window.gallery) {
                    window.gallery.exportGallery();
                }
            });

            window.electronAPI.onShowCommandPalette((command) => {
                this.showCommandPalette();
                if (command && window.terminal) {
                    window.terminal.executeCommandProgrammatically(command + ' ');
                }
            });

            window.electronAPI.onOpenPreferences(() => {
                this.showPreferences();
            });

            window.electronAPI.onShowHelp(() => {
                this.showHelp();
            });
        }
    }

    executeQuickCommand(command) {
        const prompts = {
            'GEN': 'Enter your image generation prompt:',
            'IMAGEN': 'Enter your high-quality image prompt:',
            'EDIT': 'Enter your image editing prompt:',
            'PHOTO': 'Enter subject for photography:',
            'ART': 'Enter subject and style (e.g., "cat impressionist"):',
            'LOGO': 'Enter company, style, industry (e.g., "TechCorp modern software"):',
            'CODE': 'Enter code or question for analysis:',
            'DEBUG': 'Describe the bug or issue:'
        };

        const prompt = prompts[command];
        if (prompt) {
            const userInput = window.prompt(prompt);
            if (userInput) {
                if (window.terminal) {
                    window.terminal.executeCommandProgrammatically(`${command} ${userInput}`);
                }
                this.hideCommandPalette();
            }
        } else {
            if (window.terminal) {
                window.terminal.executeCommandProgrammatically(command);
            }
            this.hideCommandPalette();
        }
    }

    showCommandPalette() {
        const palette = document.getElementById('command-palette');
        palette.classList.remove('hidden');
    }

    hideCommandPalette() {
        const palette = document.getElementById('command-palette');
        palette.classList.add('hidden');
    }

    showHelp() {
        const modal = document.getElementById('help-modal');
        modal.classList.remove('hidden');
    }

    showPreferences() {
        // Create preferences modal dynamically
        const modal = this.createPreferencesModal();
        document.body.appendChild(modal);
    }

    createPreferencesModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>PREFERENCES</h2>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="pref-section">
                        <h3>API Configuration</h3>
                        <div class="pref-item">
                            <label for="google-api-key">Google API Key:</label>
                            <input type="password" id="google-api-key" placeholder="Enter your Google API key">
                        </div>
                    </div>
                    <div class="pref-section">
                        <h3>Terminal Settings</h3>
                        <div class="pref-item">
                            <label for="font-size">Font Size:</label>
                            <select id="font-size">
                                <option value="12">12px</option>
                                <option value="14" selected>14px</option>
                                <option value="16">16px</option>
                                <option value="18">18px</option>
                            </select>
                        </div>
                        <div class="pref-item">
                            <label for="theme">Theme:</label>
                            <select id="theme">
                                <option value="green" selected>Green Terminal</option>
                                <option value="amber">Amber Terminal</option>
                                <option value="blue">Blue Terminal</option>
                            </select>
                        </div>
                    </div>
                    <div class="pref-actions">
                        <button class="retro-btn" onclick="this.closest('.modal').remove()">CANCEL</button>
                        <button class="retro-btn" onclick="app.savePreferences(this.closest('.modal'))">SAVE</button>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners
        const closeBtn = modal.querySelector('.close-btn');
        closeBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });

        return modal;
    }

    savePreferences(modal) {
        const apiKey = modal.querySelector('#google-api-key').value;
        const fontSize = modal.querySelector('#font-size').value;
        const theme = modal.querySelector('#theme').value;

        // Save to localStorage
        const preferences = {
            apiKey: apiKey,
            fontSize: fontSize,
            theme: theme,
            timestamp: new Date().toISOString()
        };

        localStorage.setItem('retro-ai-preferences', JSON.stringify(preferences));

        // Apply theme changes
        this.applyTheme(theme);
        this.applyFontSize(fontSize);

        // Show success message
        if (window.gallery) {
            window.gallery.showSuccess('Preferences saved successfully');
        }

        document.body.removeChild(modal);
    }

    applyTheme(theme) {
        const root = document.documentElement;
        
        switch (theme) {
            case 'amber':
                root.style.setProperty('--terminal-text', '#ffaa00');
                root.style.setProperty('--accent-color', '#ffaa00');
                break;
            case 'blue':
                root.style.setProperty('--terminal-text', '#00aaff');
                root.style.setProperty('--accent-color', '#00aaff');
                break;
            default: // green
                root.style.setProperty('--terminal-text', '#00ff00');
                root.style.setProperty('--accent-color', '#00ffff');
        }
    }

    applyFontSize(size) {
        const root = document.documentElement;
        root.style.setProperty('--font-size-base', `${size}px`);
    }

    handleGlobalKeydown(e) {
        // Global keyboard shortcuts
        if (e.key === 'Escape') {
            // Close any open modals
            document.querySelectorAll('.modal:not(.hidden)').forEach(modal => {
                modal.classList.add('hidden');
            });
            this.hideCommandPalette();
        }
        
        if (e.key === 'F1') {
            e.preventDefault();
            this.showHelp();
        }
        
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case ',':
                    e.preventDefault();
                    this.showPreferences();
                    break;
                case 'u':
                    e.preventDefault();
                    if (window.gallery) {
                        window.gallery.triggerUpload();
                    }
                    break;
            }
        }
    }

    handleSocketCommandResult(data) {
        if (window.terminal) {
            if (data.success) {
                window.terminal.addOutput(data.result.output, data.result.type);
                
                if (data.result.type === 'image' && data.result.data) {
                    this.handleImageResult(data.result.data);
                }
            } else {
                window.terminal.addOutput(`ERROR: ${data.error}`, 'error');
            }
        }
    }

    handleSocketImageResult(data) {
        if (data.success && window.gallery) {
            if (data.result.images) {
                data.result.images.forEach(imagePath => {
                    window.gallery.addImage(imagePath, data.result.sessionId);
                });
            }
        }
    }

    updateConnectionStatus() {
        const indicator = document.getElementById('status-indicator');
        if (this.connectionStatus === 'connected') {
            indicator.textContent = 'OPERATIONAL';
            indicator.className = 'status-ok';
        } else {
            indicator.textContent = 'OFFLINE';
            indicator.className = 'status-error';
        }
    }

    saveSession() {
        const sessionData = {
            timestamp: new Date().toISOString(),
            terminal: {
                history: window.terminal ? window.terminal.commandHistory : [],
                currentSession: window.terminal ? window.terminal.getCurrentSessionId() : null
            },
            gallery: {
                images: window.gallery ? window.gallery.images : [],
                selectedImage: window.gallery ? window.gallery.selectedImage : null
            }
        };

        // Download session file
        const blob = new Blob([JSON.stringify(sessionData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `retro-ai-session-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        if (window.gallery) {
            window.gallery.showSuccess('Session saved successfully');
        }
    }

    addContextMenuStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .context-menu {
                background: var(--secondary-bg);
                border: 1px solid var(--border-color);
                border-radius: var(--border-radius);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
                padding: 4px 0;
                min-width: 150px;
                font-family: var(--font-mono);
                font-size: var(--font-size-small);
            }
            
            .context-item {
                padding: 8px 16px;
                color: var(--terminal-text);
                cursor: pointer;
                transition: background-color 0.2s ease;
            }
            
            .context-item:hover {
                background: var(--accent-color);
                color: var(--primary-bg);
            }
            
            .gallery-item.selected {
                border-color: var(--accent-color);
                box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
            }
            
            .image-placeholder {
                height: 120px;
                background: var(--primary-bg);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: var(--border-color);
                font-size: 12px;
                text-align: center;
            }
            
            .placeholder-icon {
                font-size: 24px;
                margin-bottom: 8px;
            }
            
            .pref-section {
                margin-bottom: 24px;
            }
            
            .pref-section h3 {
                color: var(--amber-text);
                font-size: 14px;
                font-weight: 700;
                margin-bottom: 16px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .pref-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
            }
            
            .pref-item label {
                color: var(--terminal-text);
                font-size: 12px;
            }
            
            .pref-item input,
            .pref-item select {
                background: var(--terminal-bg);
                border: 1px solid var(--border-color);
                color: var(--terminal-text);
                padding: 4px 8px;
                font-family: var(--font-mono);
                font-size: 12px;
                border-radius: var(--border-radius);
                min-width: 120px;
            }
            
            .pref-actions {
                display: flex;
                gap: 12px;
                justify-content: flex-end;
                margin-top: 24px;
                padding-top: 16px;
                border-top: 1px solid var(--border-color);
            }
        `;
        document.head.appendChild(style);
    }

    // Load preferences on startup
    loadPreferences() {
        const saved = localStorage.getItem('retro-ai-preferences');
        if (saved) {
            try {
                const preferences = JSON.parse(saved);
                this.applyTheme(preferences.theme || 'green');
                this.applyFontSize(preferences.fontSize || '14');
            } catch (error) {
                console.error('Failed to load preferences:', error);
            }
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new RetroAIApp();
    window.app.loadPreferences();
});
