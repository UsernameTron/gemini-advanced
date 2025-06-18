/**
 * Main Application Controller
 * Orchestrates the retro AI experience with server-side Google Gemini integration
 */

import { RetroAIClient } from './client/RetroAIClient.js';
import { RetroTerminalInterface } from './ui/TerminalInterface.js';

class RetroAIApplication {
    constructor(containerId) {
        // Initialize core systems with client-server architecture
        this.client = new RetroAIClient();
        this.terminal = new RetroTerminalInterface(containerId);
        this.sessionStartTime = Date.now();
        
        // Bind event handlers
        this.terminal.onUserInput = this.handleUserInput.bind(this);
        this.terminal.onExportSession = this.handleExportSession.bind(this);
        
        // Application state
        this.isProcessing = false;
        this.currentMission = null;
        
        // Initialize the application
        this.initialize();
    }

    async initialize() {
        try {
            // Update connection status
            this.terminal.updateConnectionStatus('CONNECTING');
            
            // Start session timer
            this.terminal.updateSessionTimer(this.sessionStartTime);
            
            // Test AI connection
            await this.testConnection();
            
            // Display welcome sequence
            await this.displayWelcome();
            
            // Update status to connected
            this.terminal.updateConnectionStatus('CONNECTED');
            
        } catch (error) {
            console.error('Initialization error:', error);
            this.terminal.updateConnectionStatus('ERROR');
            await this.terminal.displayMessage(
                'SYSTEM INITIALIZATION ERROR: Unable to connect to AI services. Please check your configuration.',
                { type: 'error', instant: true }
            );
        }
    }

    async testConnection() {
        try {
            const result = await this.client.testConnection();
            console.log('✅ Connection test successful:', result);
            return result;
        } catch (error) {
            console.error('❌ Connection test failed:', error);
            throw error;
        }
    }

    async displayWelcome() {
        // Use the terminal's built-in welcome sequence for now
        await this.terminal.displayWelcomeSequence();
    }

    async handleUserInput(userMessage) {
        if (this.isProcessing) {
            await this.terminal.displayMessage(
                'PROCESSING PREVIOUS REQUEST... PLEASE WAIT',
                { type: 'system', instant: true }
            );
            return;
        }

        this.isProcessing = true;

        try {
            // Handle special commands
            if (this.handleSpecialCommands(userMessage)) {
                this.isProcessing = false;
                return;
            }

            // Process through AI client
            const response = await this.client.sendMessage(userMessage);
            
            if (response.status === 'error') {
                await this.terminal.displayMessage(
                    `AI PROCESSING ERROR: ${response.message}`,
                    { type: 'error', typewriter: true }
                );
            } else {
                // Display AI response with typing effect
                await this.terminal.displayMessage(
                    response.response,
                    { 
                        type: 'assistant',
                        typewriter: true,
                        delay: 20
                    }
                );
                
                // Update current mission if detected
                if (response.metadata && response.metadata.mission) {
                    this.currentMission = response.metadata.mission;
                    await this.displayMissionStatus();
                }
            }

        } catch (error) {
            console.error('User input processing error:', error);
            await this.terminal.displayMessage(
                `SYSTEM ERROR: ${error.message}`,
                { type: 'error', typewriter: true }
            );
        } finally {
            this.isProcessing = false;
        }
    }

    handleSpecialCommands(input) {
        const command = input.toLowerCase().trim();

        switch (command) {
            case 'clear':
            case 'cls':
                this.terminal.clearScreen();
                return true;

            case 'status':
            case 'system status':
                this.displaySystemStatus();
                return true;

            case 'help':
            case '?':
                this.displayHelp();
                return true;

            case 'export':
            case 'save':
                this.handleExportSession();
                return true;

            case 'new session':
            case 'reset':
                this.resetSession();
                return true;

            case 'sound on':
                this.terminal.soundEnabled = true;
                this.terminal.displayMessage('SOUND ENABLED', { type: 'system', instant: true });
                return true;

            case 'sound off':
                this.terminal.soundEnabled = false;
                this.terminal.displayMessage('SOUND DISABLED', { type: 'system', instant: true });
                return true;

            default:
                return false;
        }
    }

    async displaySystemStatus() {
        const status = this.agent.getSystemStatus();
        const sessionDuration = Math.floor((Date.now() - this.sessionStartTime) / 1000);
        
        const statusMessage = `
NEXUS CREATIVE AI - SYSTEM STATUS
===============================
STATUS: ${status.status}
SESSION DURATION: ${this.formatDuration(sessionDuration)}
MESSAGES EXCHANGED: ${status.conversationLength}
CURRENT MISSION: ${this.currentMission || 'NONE'}
AI CAPABILITIES: ${status.capabilities.join(', ')}
SOUND: ${this.terminal.soundEnabled ? 'ENABLED' : 'DISABLED'}
CONNECTION: STABLE
===============================`;

        await this.terminal.displayMessage(statusMessage, {
            type: 'system',
            typewriter: true,
            delay: 15
        });
    }

    async displayHelp() {
        const helpMessage = `
NEXUS CREATIVE AI - COMMAND REFERENCE
===================================
GENERAL COMMANDS:
  help, ?          - Show this help
  status           - Display system status
  clear, cls       - Clear the screen
  export, save     - Export conversation
  new session      - Start fresh session
  sound on/off     - Toggle sound effects

CREATIVE MISSIONS:
  "brand analysis" - Analyze brand materials
  "create [type]"  - Generate creative content
  "campaign [goal]"- Develop campaign strategy
  "code [request]" - Programming assistance
  "analyze [item]" - Deep analysis of content

INTERACTION TIPS:
  - Use natural language to describe your needs
  - Ask for specific creative challenges
  - Upload images for visual analysis
  - Request step-by-step guidance
  - Combine multiple requests for complex projects

TYPE YOUR REQUEST TO BEGIN A CREATIVE MISSION
===========================================`;

        await this.terminal.displayMessage(helpMessage, {
            type: 'system',
            typewriter: true,
            delay: 10
        });
    }

    async displayMissionStatus() {
        const missionNames = {
            'brand_analysis': 'BRAND VISUAL ANALYSIS',
            'creative_generation': 'CREATIVE ASSET GENERATION',
            'campaign_orchestration': 'CAMPAIGN STRATEGY DEVELOPMENT',
            'code_development': 'CODE CREATION & ANALYSIS',
            'analysis': 'CONTENT ANALYSIS',
            'guidance': 'MISSION GUIDANCE'
        };

        const missionName = missionNames[this.currentMission] || this.currentMission.toUpperCase();
        
        await this.terminal.displayMessage(
            `MISSION ACTIVATED: ${missionName}`,
            { 
                type: 'system', 
                highlight: true, 
                instant: true,
                sound: 'notification'
            }
        );
    }

    async resetSession() {
        await this.terminal.displayMessage(
            'INITIATING NEW SESSION...',
            { type: 'system', typewriter: true }
        );

        // Reset AI agent
        this.agent.resetSession();
        
        // Reset application state
        this.currentMission = null;
        this.sessionStartTime = Date.now();
        
        // Update UI
        this.terminal.updateSessionTimer(this.sessionStartTime);
        
        // Clear screen and show welcome
        setTimeout(async () => {
            this.terminal.clearScreen();
            await this.displayWelcome();
        }, 1000);
    }

    async handleExportSession() {
        try {
            const sessionData = this.agent.exportConversation();
            
            // Create downloadable file
            const dataStr = JSON.stringify(sessionData, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = `nexus-session-${new Date().toISOString().split('T')[0]}.json`;
            
            // Trigger download
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            await this.terminal.displayMessage(
                'SESSION EXPORTED SUCCESSFULLY',
                { type: 'system', instant: true, sound: 'notification' }
            );

        } catch (error) {
            console.error('Export error:', error);
            await this.terminal.displayMessage(
                'EXPORT FAILED: Unable to save session data',
                { type: 'error', instant: true }
            );
        }
    }

    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }

    // File upload handling (for future image analysis features)
    async handleFileUpload(files) {
        if (!files || files.length === 0) return;

        await this.terminal.displayMessage(
            `PROCESSING ${files.length} FILE(S)...`,
            { type: 'system', typewriter: true }
        );

        for (const file of files) {
            if (file.type.startsWith('image/')) {
                // Handle image analysis
                const reader = new FileReader();
                reader.onload = async (e) => {
                    const imageData = e.target.result.split(',')[1]; // Remove data URL prefix
                    const analysis = await this.agent.analyzeVisualContent(
                        imageData, 
                        `Analyze this uploaded image: ${file.name}`
                    );
                    
                    await this.terminal.displayMessage(
                        `IMAGE ANALYSIS COMPLETE: ${file.name}`,
                        { type: 'system', highlight: true }
                    );
                    
                    await this.terminal.displayMessage(
                        analysis.response,
                        { type: 'assistant', typewriter: true, delay: 20 }
                    );
                };
                reader.readAsDataURL(file);
            } else {
                await this.terminal.displayMessage(
                    `UNSUPPORTED FILE TYPE: ${file.name}`,
                    { type: 'error', instant: true }
                );
            }
        }
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the application (no API key needed on client side)
    try {
        const app = new RetroAIApplication('app-container');
        
        // Make app globally available for debugging
        window.retroAI = app;
        
        console.log('🚀 Retro AI Gemini Application initialized successfully');
        
    } catch (error) {
        console.error('Application initialization failed:', error);
        document.body.innerHTML = `
            <div style="color: #ff0040; font-family: monospace; padding: 20px; text-align: center;">
                <h1>INITIALIZATION ERROR</h1>
                <p>Failed to start Retro AI application.</p>
                <p>Error: ${error.message}</p>
                <p>Check the console for more details.</p>
            </div>
        `;
    }
});

// File drop handling
document.addEventListener('dragover', (e) => {
    e.preventDefault();
});

document.addEventListener('drop', (e) => {
    e.preventDefault();
    if (window.retroAI) {
        window.retroAI.handleFileUpload(e.dataTransfer.files);
    }
});

export { RetroAIApplication };
