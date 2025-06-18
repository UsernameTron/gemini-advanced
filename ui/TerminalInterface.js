/**
 * Retro Terminal Interface
 * Creates the authentic retro terminal experience with typing effects,
 * sound effects, and classic computer aesthetics
 */

export class RetroTerminalInterface {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.messageQueue = [];
        this.isTyping = false;
        this.cursor = null;
        this.soundEnabled = true;
        this.typingSpeed = 30; // milliseconds per character
        
        this.setupTerminalStructure();
        this.initializeAudioEffects();
        this.initializeEventListeners();
    }

    setupTerminalStructure() {
        // Create the retro terminal visual structure
        this.container.innerHTML = `
            <div class="terminal-frame">
                <div class="terminal-header">
                    <div class="terminal-controls">
                        <div class="control-button close"></div>
                        <div class="control-button minimize"></div>
                        <div class="control-button maximize"></div>
                    </div>
                    <div class="terminal-title">NEXUS CREATIVE AI SYSTEM v2.0</div>
                    <div class="terminal-status" id="terminal-status">
                        <span class="status-indicator"></span>
                        <span class="status-text">ONLINE</span>
                    </div>
                </div>
                <div class="terminal-screen" id="terminal-screen">
                    <div class="boot-sequence" id="boot-sequence"></div>
                    <div class="conversation-area" id="conversation-area"></div>
                    <div class="input-area" id="input-area">
                        <span class="prompt">NEXUS></span>
                        <input type="text" id="user-input" class="terminal-input" autocomplete="off" spellcheck="false" />
                        <span class="cursor-blink" id="terminal-cursor">█</span>
                    </div>
                </div>
                <div class="terminal-footer">
                    <div class="system-info">
                        <span id="session-timer">00:00:00</span>
                        <span class="separator">|</span>
                        <span id="message-count">0 messages</span>
                        <span class="separator">|</span>
                        <span id="connection-status">CONNECTED</span>
                    </div>
                    <div class="controls">
                        <button id="sound-toggle" class="control-btn">🔊</button>
                        <button id="clear-screen" class="control-btn">CLEAR</button>
                        <button id="export-session" class="control-btn">EXPORT</button>
                    </div>
                </div>
            </div>
        `;
        
        this.applyRetroStyling();
    }

    applyRetroStyling() {
        // Inject the CSS that creates the authentic retro terminal feel
        if (!document.getElementById('retro-terminal-styles')) {
            const style = document.createElement('style');
            style.id = 'retro-terminal-styles';
            style.textContent = `
                @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&family=Share+Tech+Mono&display=swap');
                
                body {
                    margin: 0;
                    padding: 20px;
                    background: #000000;
                    font-family: 'Share Tech Mono', 'Courier Prime', monospace;
                    color: #00ff41;
                    overflow: hidden;
                }

                .terminal-frame {
                    background: #000000;
                    border: 2px solid #00ff41;
                    border-radius: 8px;
                    width: 100vw;
                    height: 100vh;
                    max-width: calc(100vw - 40px);
                    max-height: calc(100vh - 40px);
                    box-shadow: 
                        0 0 30px #00ff41,
                        inset 0 0 30px rgba(0, 255, 65, 0.1),
                        0 0 0 1px rgba(0, 255, 65, 0.5);
                    position: relative;
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                }

                .terminal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 1px solid #00ff41;
                    padding: 10px 20px;
                    background: linear-gradient(90deg, rgba(0, 255, 65, 0.1), transparent);
                }

                .terminal-controls {
                    display: flex;
                    gap: 8px;
                }

                .control-button {
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    border: 1px solid #00ff41;
                }

                .control-button.close { background: #ff0040; }
                .control-button.minimize { background: #ffff00; }
                .control-button.maximize { background: #00ff41; }

                .terminal-title {
                    font-weight: bold;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    color: #ffffff;
                    text-shadow: 0 0 10px #00ff41;
                    flex: 1;
                    text-align: center;
                }

                .terminal-status {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 0.9em;
                }

                .status-indicator {
                    width: 8px;
                    height: 8px;
                    background: #00ff41;
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                    box-shadow: 0 0 10px #00ff41;
                }

                .terminal-screen {
                    flex: 1;
                    overflow-y: auto;
                    scroll-behavior: smooth;
                    padding: 20px;
                    position: relative;
                    background: 
                        radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.15) 0%, transparent 50%),
                        radial-gradient(circle at 40% 40%, rgba(120, 200, 255, 0.1) 0%, transparent 50%);
                }

                .terminal-screen::-webkit-scrollbar {
                    width: 8px;
                }

                .terminal-screen::-webkit-scrollbar-track {
                    background: rgba(0, 255, 65, 0.1);
                }

                .terminal-screen::-webkit-scrollbar-thumb {
                    background: #00ff41;
                    border-radius: 4px;
                }

                .message-line {
                    margin: 12px 0;
                    white-space: pre-wrap;
                    opacity: 0;
                    animation: fadeIn 0.5s ease-in forwards;
                    line-height: 1.4;
                }

                .message-user {
                    color: #ffffff;
                    text-shadow: 0 0 5px #ffffff;
                }

                .message-system {
                    color: #ff6600;
                    font-weight: bold;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }

                .message-assistant {
                    color: #00ff41;
                }

                .message-highlight {
                    color: #ffffff;
                    text-shadow: 0 0 15px #00ff41;
                    font-weight: bold;
                    font-size: 1.1em;
                    letter-spacing: 1px;
                    animation: glow 2s ease-in-out infinite alternate;
                }

                .message-error {
                    color: #ff0040;
                    background: rgba(255, 0, 64, 0.1);
                    padding: 10px;
                    border-left: 3px solid #ff0040;
                }

                .typing-effect {
                    overflow: hidden;
                    white-space: nowrap;
                    border-right: 2px solid #00ff41;
                    animation: typing 0.1s steps(1) infinite;
                }

                .input-area {
                    display: flex;
                    align-items: center;
                    padding: 15px 20px;
                    border-top: 1px solid #00ff41;
                    background: rgba(0, 255, 65, 0.05);
                }

                .prompt {
                    color: #ffffff;
                    font-weight: bold;
                    margin-right: 10px;
                    text-shadow: 0 0 10px #00ff41;
                }

                .terminal-input {
                    background: transparent;
                    border: none;
                    color: #00ff41;
                    font-family: inherit;
                    font-size: inherit;
                    outline: none;
                    flex: 1;
                    margin-right: 10px;
                }

                .terminal-input::placeholder {
                    color: rgba(0, 255, 65, 0.5);
                }

                .cursor-blink {
                    animation: blink 1s infinite;
                    color: #00ff41;
                }

                .terminal-footer {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 8px 20px;
                    border-top: 1px solid #00ff41;
                    background: rgba(0, 255, 65, 0.05);
                    font-size: 0.85em;
                }

                .system-info {
                    display: flex;
                    gap: 10px;
                    color: rgba(0, 255, 65, 0.8);
                }

                .separator {
                    color: rgba(0, 255, 65, 0.5);
                }

                .controls {
                    display: flex;
                    gap: 10px;
                }

                .control-btn {
                    background: transparent;
                    border: 1px solid #00ff41;
                    color: #00ff41;
                    padding: 4px 8px;
                    font-family: inherit;
                    font-size: 0.8em;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }

                .control-btn:hover {
                    background: rgba(0, 255, 65, 0.2);
                    box-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
                }

                .glitch-effect {
                    animation: glitch 0.3s ease-in-out;
                }

                .scan-line {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 2px;
                    background: linear-gradient(90deg, transparent, #00ff41, transparent);
                    animation: scan 2s linear infinite;
                    opacity: 0.6;
                }

                /* Animations */
                @keyframes fadeIn {
                    from { 
                        opacity: 0; 
                        transform: translateY(10px); 
                    }
                    to { 
                        opacity: 1; 
                        transform: translateY(0); 
                    }
                }

                @keyframes pulse {
                    0%, 100% { 
                        opacity: 1; 
                        transform: scale(1);
                    }
                    50% { 
                        opacity: 0.5; 
                        transform: scale(0.8);
                    }
                }

                @keyframes blink {
                    0%, 50% { opacity: 1; }
                    51%, 100% { opacity: 0; }
                }

                @keyframes typing {
                    from { border-color: #00ff41; }
                    to { border-color: transparent; }
                }

                @keyframes glow {
                    from { text-shadow: 0 0 10px #00ff41; }
                    to { text-shadow: 0 0 20px #00ff41, 0 0 30px #00ff41; }
                }

                @keyframes glitch {
                    0% { transform: translate(0); }
                    20% { transform: translate(-2px, 2px); }
                    40% { transform: translate(-2px, -2px); }
                    60% { transform: translate(2px, 2px); }
                    80% { transform: translate(2px, -2px); }
                    100% { transform: translate(0); }
                }

                @keyframes scan {
                    0% { top: 0%; }
                    100% { top: 100%; }
                }

                /* Mobile responsiveness */
                @media (max-width: 768px) {
                    body {
                        padding: 10px;
                    }
                    
                    .terminal-frame {
                        max-width: calc(100vw - 20px);
                        max-height: calc(100vh - 20px);
                    }
                    
                    .terminal-title {
                        font-size: 0.9em;
                    }
                    
                    .terminal-footer {
                        flex-direction: column;
                        gap: 10px;
                        text-align: center;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    initializeEventListeners() {
        // Input handling
        const input = document.getElementById('user-input');
        input.addEventListener('keydown', (e) => this.handleKeydown(e));
        input.addEventListener('input', () => this.updateInputWidth());

        // Control buttons
        document.getElementById('sound-toggle').addEventListener('click', () => this.toggleSound());
        document.getElementById('clear-screen').addEventListener('click', () => this.clearScreen());
        document.getElementById('export-session').addEventListener('click', () => this.exportSession());

        // Focus management
        input.focus();
        this.container.addEventListener('click', () => input.focus());
    }

    initializeAudioEffects() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.soundEffects = {
                keystroke: () => this.createKeystrokeSound(),
                notification: () => this.createNotificationSound(),
                error: () => this.createErrorSound(),
                boot: () => this.createBootSound()
            };
        } catch (error) {
            console.warn('Audio not available:', error);
            this.soundEnabled = false;
        }
    }

    createKeystrokeSound() {
        if (!this.soundEnabled || !this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800 + Math.random() * 200, this.audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.05, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1);
        
        oscillator.start();
        oscillator.stop(this.audioContext.currentTime + 0.1);
    }

    createNotificationSound() {
        if (!this.soundEnabled || !this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(600, this.audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(1200, this.audioContext.currentTime + 0.1);
        gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2);
        
        oscillator.start();
        oscillator.stop(this.audioContext.currentTime + 0.2);
    }

    createBootSound() {
        if (!this.soundEnabled || !this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        // Create a classic boot-up sound sequence
        oscillator.frequency.setValueAtTime(220, this.audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(440, this.audioContext.currentTime + 0.3);
        oscillator.frequency.exponentialRampToValueAtTime(880, this.audioContext.currentTime + 0.6);
        
        gainNode.gain.setValueAtTime(0.15, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.2, this.audioContext.currentTime + 0.3);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 1.0);
        
        oscillator.start();
        oscillator.stop(this.audioContext.currentTime + 1.0);
    }

    createErrorSound() {
        if (!this.soundEnabled || !this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        // Create a harsh error sound with dissonant frequencies
        oscillator.frequency.setValueAtTime(400, this.audioContext.currentTime);
        oscillator.frequency.setValueAtTime(300, this.audioContext.currentTime + 0.1);
        oscillator.frequency.setValueAtTime(200, this.audioContext.currentTime + 0.2);
        
        gainNode.gain.setValueAtTime(0.2, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
        
        oscillator.start();
        oscillator.stop(this.audioContext.currentTime + 0.3);
    }

    async displayMessage(message, options = {}) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message-line';
        
        // Apply message type styling
        if (options.type === 'user') {
            messageElement.classList.add('message-user');
        } else if (options.type === 'system') {
            messageElement.classList.add('message-system');
        } else if (options.type === 'error') {
            messageElement.classList.add('message-error');
        } else {
            messageElement.classList.add('message-assistant');
        }
        
        if (options.highlight) {
            messageElement.classList.add('message-highlight');
        }
        
        // Handle typing effect
        if (options.typewriter && !options.instant) {
            await this.typewriterEffect(messageElement, message, options.delay || this.typingSpeed);
        } else {
            messageElement.textContent = message;
            document.getElementById('conversation-area').appendChild(messageElement);
        }
        
        this.scrollToBottom();
        
        // Play sound effect
        if (options.sound) {
            this.playSound(options.sound);
        }

        // Update message count
        this.updateMessageCount();
    }

    async typewriterEffect(element, text, delay) {
        element.textContent = '';
        element.classList.add('typing-effect');
        document.getElementById('conversation-area').appendChild(element);
        
        for (let i = 0; i < text.length; i++) {
            element.textContent += text[i];
            
            // Play keystroke sound occasionally
            if (Math.random() > 0.8) {
                this.soundEffects.keystroke();
            }
            
            await this.delay(delay);
        }
        
        element.classList.remove('typing-effect');
    }

    async displaySequence(messages) {
        for (const message of messages) {
            await this.displayMessage(message.text, {
                typewriter: message.typewriter !== false,
                highlight: message.highlight,
                type: message.type || 'system',
                delay: message.delay || this.typingSpeed,
                sound: message.sound
            });
            
            if (message.pause) {
                await this.delay(message.pause);
            }
        }
    }

    async displayWelcomeSequence() {
        const welcomeMessages = [
            { text: 'NEXUS CREATIVE AI SYSTEM INITIALIZING...', delay: 20, pause: 800, sound: 'boot' },
            { text: 'LOADING GEMINI NEURAL NETWORKS...', delay: 20, pause: 600 },
            { text: 'ESTABLISHING SECURE CONNECTION...', delay: 20, pause: 500 },
            { text: 'CREATIVE MATRIX ONLINE...', delay: 20, pause: 700 },
            { text: 'MISSION PROTOCOLS LOADED...', delay: 20, pause: 1000 },
            { text: '', pause: 500 },
            { text: 'SHALL WE PLAY A GAME?', delay: 60, highlight: true, pause: 1200, sound: 'notification' },
            { text: '', pause: 300 },
            { text: 'AVAILABLE CREATIVE MISSIONS:', delay: 30, type: 'system' },
            { text: '█ BRAND VISUAL ANALYSIS', delay: 25 },
            { text: '█ CREATIVE ASSET GENERATION', delay: 25 },
            { text: '█ CAMPAIGN STRATEGY DEVELOPMENT', delay: 25 },
            { text: '█ CODE CREATION & ANALYSIS', delay: 25 },
            { text: '█ DOCUMENT PROCESSING & INSIGHTS', delay: 25 },
            { text: '', pause: 500 },
            { text: 'DESCRIBE YOUR CREATIVE CHALLENGE OR SELECT A MISSION...', delay: 20, highlight: true }
        ];

        await this.displaySequence(welcomeMessages);
        this.addScanLine();
    }

    addScanLine() {
        const scanLine = document.createElement('div');
        scanLine.className = 'scan-line';
        document.getElementById('terminal-screen').appendChild(scanLine);
        
        setTimeout(() => {
            if (scanLine.parentNode) {
                scanLine.parentNode.removeChild(scanLine);
            }
        }, 2000);
    }

    handleKeydown(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.processUserInput();
        } else if (e.key === 'Tab') {
            e.preventDefault();
            this.handleTabCompletion();
        } else if (e.ctrlKey && e.key === 'l') {
            e.preventDefault();
            this.clearScreen();
        }
        
        // Play keystroke sound
        this.soundEffects.keystroke();
    }

    async processUserInput() {
        const input = document.getElementById('user-input');
        const userMessage = input.value.trim();
        
        if (!userMessage) return;
        
        // Display user message
        await this.displayMessage(`NEXUS> ${userMessage}`, { 
            type: 'user',
            instant: true
        });
        
        // Clear input
        input.value = '';
        
        // Show processing indicator
        await this.displayMessage('PROCESSING...', { 
            type: 'system',
            typewriter: true,
            delay: 50
        });
        
        // Trigger user input event
        this.onUserInput?.(userMessage);
    }

    handleTabCompletion() {
        const input = document.getElementById('user-input');
        const currentValue = input.value.toLowerCase();
        
        const commands = [
            'brand analysis',
            'create campaign',
            'generate content',
            'analyze code',
            'help',
            'clear',
            'status',
            'export'
        ];
        
        const matches = commands.filter(cmd => cmd.startsWith(currentValue));
        
        if (matches.length === 1) {
            input.value = matches[0];
        } else if (matches.length > 1) {
            this.displayMessage(`Available: ${matches.join(', ')}`, { 
                type: 'system',
                instant: true 
            });
        }
    }

    playSound(soundType) {
        if (this.soundEffects[soundType]) {
            this.soundEffects[soundType]();
        }
    }

    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        const button = document.getElementById('sound-toggle');
        button.textContent = this.soundEnabled ? '🔊' : '🔇';
        
        this.displayMessage(`SOUND ${this.soundEnabled ? 'ENABLED' : 'DISABLED'}`, {
            type: 'system',
            instant: true
        });
    }

    clearScreen() {
        const conversationArea = document.getElementById('conversation-area');
        conversationArea.innerHTML = '';
        this.updateMessageCount();
        
        this.displayMessage('SCREEN CLEARED', {
            type: 'system',
            instant: true
        });
    }

    updateInputWidth() {
        // Auto-resize functionality could be added here
    }

    updateMessageCount() {
        const messageCount = document.querySelectorAll('.message-line').length;
        document.getElementById('message-count').textContent = `${messageCount} messages`;
    }

    updateSessionTimer(startTime) {
        const updateTimer = () => {
            const elapsed = Date.now() - startTime;
            const hours = Math.floor(elapsed / 3600000);
            const minutes = Math.floor((elapsed % 3600000) / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            
            document.getElementById('session-timer').textContent = 
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        };
        
        updateTimer();
        setInterval(updateTimer, 1000);
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        statusElement.textContent = status;
        
        const indicator = document.querySelector('.status-indicator');
        if (status === 'CONNECTED') {
            indicator.style.background = '#00ff41';
        } else if (status === 'CONNECTING') {
            indicator.style.background = '#ffff00';
        } else {
            indicator.style.background = '#ff0040';
        }
    }

    exportSession() {
        // This will be called by the main application
        this.onExportSession?.();
    }

    scrollToBottom() {
        const screen = document.getElementById('terminal-screen');
        screen.scrollTop = screen.scrollHeight;
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Event handlers (to be set by main application)
    onUserInput = null;
    onExportSession = null;
}
