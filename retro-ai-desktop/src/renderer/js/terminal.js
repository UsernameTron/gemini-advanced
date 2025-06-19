class RetroTerminal {
    constructor() {
        this.output = document.getElementById('terminal-output');
        this.input = document.getElementById('command-input');
        this.prompt = document.getElementById('command-prompt');
        this.cursor = document.getElementById('cursor');
        this.bootSequence = document.getElementById('boot-sequence');
        
        this.commandHistory = [];
        this.historyIndex = -1;
        this.currentSessionId = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startBootSequence();
        this.updateTimestamp();
        setInterval(() => this.updateTimestamp(), 1000);
    }

    setupEventListeners() {
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.input.addEventListener('input', () => this.updateCursor());
        this.input.addEventListener('focus', () => this.showCursor());
        this.input.addEventListener('blur', () => this.hideCursor());
        
        // Focus input when clicking on terminal
        document.getElementById('terminal-content').addEventListener('click', () => {
            this.input.focus();
        });
    }

    startBootSequence() {
        setTimeout(() => {
            this.bootSequence.style.display = 'none';
            this.addWelcomeMessage();
            this.input.focus();
        }, 4000);
    }

    addWelcomeMessage() {
        const welcome = `
╔══════════════════════════════════════════════════════════════════╗
║              UNIFIED AI COMMAND CENTER v2.0                     ║
║                    ENHANCED IMAGE GENERATION                     ║
╠══════════════════════════════════════════════════════════════════╣
║                        SYSTEM READY                             ║
║                                                                  ║
║ Available Commands:                                              ║
║ • GEN [prompt] - Gemini conversational generation               ║
║ • IMAGEN [prompt] - High-quality Imagen generation              ║
║ • EDIT [session] [prompt] - Edit uploaded images                ║
║ • PHOTO [subject] - Professional photography                    ║
║ • ART [subject] [style] - Artistic styles                       ║
║ • LOGO [company] [style] [industry] - Logo design               ║
║ • CODE/DEBUG/TEST - Technical agents                            ║
║ • HELP - Show full command reference                            ║
║                                                                  ║
║ Press Ctrl+Space for quick command palette                      ║
║ Upload images using the UPLOAD button →                         ║
╚══════════════════════════════════════════════════════════════════╝

retro-ai-desktop $ `;
        
        this.addOutput(welcome, 'system');
    }

    handleKeydown(e) {
        switch (e.key) {
            case 'Enter':
                e.preventDefault();
                this.executeCommand();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.navigateHistory(-1);
                break;
                
            case 'ArrowDown':
                e.preventDefault();
                this.navigateHistory(1);
                break;
                
            case 'Tab':
                e.preventDefault();
                this.autoComplete();
                break;
                
            case ' ':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.showCommandPalette();
                }
                break;
                
            case 'c':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.clearInput();
                }
                break;
                
            case 'l':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.clearTerminal();
                }
                break;
        }
    }

    async executeCommand() {
        const command = this.input.value.trim();
        if (!command) return;

        // Add command to history
        this.commandHistory.unshift(command);
        this.historyIndex = -1;

        // Display command in terminal
        this.addOutput(`retro-ai-desktop $ ${command}`, 'command');
        this.clearInput();

        // Show loading
        this.showLoading();

        try {
            // Send command to backend
            const response = await fetch('/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command })
            });

            const result = await response.json();
            
            if (result.success) {
                this.addOutput(result.result.output, result.result.type);
                
                // Handle image results
                if (result.result.type === 'image' && result.result.data) {
                    this.handleImageResult(result.result.data);
                }
            } else {
                this.addOutput(`ERROR: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Command execution error:', error);
            this.addOutput(`NETWORK ERROR: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    addOutput(text, type = 'result') {
        const line = document.createElement('div');
        line.className = `output-line output-${type}`;
        
        if (type === 'command') {
            line.innerHTML = `<span class="output-command">${text}</span>`;
        } else {
            line.textContent = text;
        }
        
        this.output.appendChild(line);
        this.scrollToBottom();
    }

    handleImageResult(data) {
        if (data.sessionId) {
            this.currentSessionId = data.sessionId;
        }
        
        // Update gallery
        if (window.gallery && data.images) {
            data.images.forEach(imagePath => {
                window.gallery.addImage(imagePath, data.sessionId);
            });
        }
    }

    navigateHistory(direction) {
        if (this.commandHistory.length === 0) return;

        this.historyIndex += direction;
        
        if (this.historyIndex < -1) {
            this.historyIndex = -1;
            this.input.value = '';
        } else if (this.historyIndex >= this.commandHistory.length) {
            this.historyIndex = this.commandHistory.length - 1;
        }
        
        if (this.historyIndex >= 0) {
            this.input.value = this.commandHistory[this.historyIndex];
        }
        
        this.updateCursor();
    }

    autoComplete() {
        const commands = [
            'GEN', 'IMAGEN', 'EDIT', 'CHAT', 'PHOTO', 'ART', 'LOGO',
            'STYLE', 'TEXT', 'BATCH', 'PARAM', 'UPLOAD', 'GALLERY',
            'HELP', 'STATUS', 'CLEAR', 'HISTORY',
            'CEO', 'EXEC', 'TRIAGE', 'RESEARCH', 'CODE', 'DEBUG', 'FIX', 'TEST', 'PERF', 'AUDIO'
        ];
        
        const input = this.input.value.toUpperCase();
        const matches = commands.filter(cmd => cmd.startsWith(input));
        
        if (matches.length === 1) {
            this.input.value = matches[0] + ' ';
            this.updateCursor();
        } else if (matches.length > 1) {
            this.addOutput(`Available commands: ${matches.join(', ')}`, 'system');
        }
    }

    showCommandPalette() {
        const palette = document.getElementById('command-palette');
        palette.classList.remove('hidden');
        
        // Close on click outside
        const closeHandler = (e) => {
            if (!palette.contains(e.target)) {
                palette.classList.add('hidden');
                document.removeEventListener('click', closeHandler);
            }
        };
        
        setTimeout(() => {
            document.addEventListener('click', closeHandler);
        }, 100);
    }

    clearInput() {
        this.input.value = '';
        this.updateCursor();
    }

    clearTerminal() {
        this.output.innerHTML = '';
        this.addWelcomeMessage();
    }

    updateCursor() {
        const inputRect = this.input.getBoundingClientRect();
        const textWidth = this.getTextWidth(this.input.value);
        this.cursor.style.left = `${textWidth + 8}px`;
    }

    showCursor() {
        this.cursor.style.display = 'inline';
    }

    hideCursor() {
        this.cursor.style.display = 'none';
    }

    getTextWidth(text) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        context.font = '14px "Source Code Pro", "Courier New", monospace';
        return context.measureText(text).width;
    }

    scrollToBottom() {
        this.output.scrollTop = this.output.scrollHeight;
    }

    showLoading() {
        document.getElementById('loading-overlay').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.add('hidden');
    }

    updateTimestamp() {
        const timestamp = document.getElementById('timestamp');
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        timestamp.textContent = timeString;
    }

    // Public API for external access
    executeCommandProgrammatically(command) {
        this.input.value = command;
        this.executeCommand();
    }

    getCurrentSessionId() {
        return this.currentSessionId;
    }

    setSessionId(sessionId) {
        this.currentSessionId = sessionId;
    }
}

// Initialize terminal when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.terminal = new RetroTerminal();
});
