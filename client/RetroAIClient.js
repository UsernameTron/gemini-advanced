/**
 * Client-side Retro AI Agent
 * Communicates with the server-side Gemini API
 */

export class RetroAIClient {
    constructor(serverUrl = '') {
        this.serverUrl = serverUrl;
        this.sessionId = this.generateSessionId();
        this.conversationHistory = [];
        this.currentMission = null;
        this.sessionStartTime = Date.now();
        
        // User profile and preferences
        this.userProfile = {
            expertise: 'novice',
            preferences: {},
            projectContext: null,
            conversationStyle: 'collaborative'
        };
        
        // System personality configuration
        this.systemPersonality = {
            name: "NEXUS_CREATIVE_AI",
            style: "retro_terminal",
            tone: "collaborative_expert",
            responseStyle: "engaging_technical"
        };
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Test connection to the AI service
     */
    async testConnection() {
        try {
            const response = await fetch(`${this.serverUrl}/api/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sessionId: this.sessionId,
                    test: true
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Connection test failed:', error);
            throw new Error(`Connection failed: ${error.message}`);
        }
    }

    /**
     * Send a message to the AI and get a response
     */
    async sendMessage(message, options = {}) {
        try {
            const requestData = {
                sessionId: this.sessionId,
                message: message,
                conversationHistory: this.conversationHistory,
                userProfile: this.userProfile,
                currentMission: this.currentMission,
                options: options
            };

            const response = await fetch(`${this.serverUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            // Update conversation history
            this.conversationHistory.push({
                role: 'user',
                content: message,
                timestamp: Date.now()
            });
            
            this.conversationHistory.push({
                role: 'assistant',
                content: result.response,
                timestamp: Date.now(),
                metadata: result.metadata || {}
            });

            return result;
        } catch (error) {
            console.error('Message sending failed:', error);
            throw new Error(`Failed to send message: ${error.message}`);
        }
    }

    /**
     * Analyze brand materials (images, documents)
     */
    async analyzeBrandMaterials(files, context = {}) {
        try {
            const formData = new FormData();
            formData.append('sessionId', this.sessionId);
            formData.append('context', JSON.stringify(context));
            formData.append('mission', 'brand_analysis');

            // Add files to form data
            for (let i = 0; i < files.length; i++) {
                formData.append('files', files[i]);
            }

            const response = await fetch(`${this.serverUrl}/api/analyze`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            this.currentMission = 'brand_analysis';
            
            return result;
        } catch (error) {
            console.error('Brand analysis failed:', error);
            throw new Error(`Failed to analyze brand materials: ${error.message}`);
        }
    }

    /**
     * Generate creative assets based on prompts and brand profile
     */
    async generateCreativeAssets(prompt, brandProfile = {}, options = {}) {
        try {
            const requestData = {
                sessionId: this.sessionId,
                prompt: prompt,
                brandProfile: brandProfile,
                mission: 'creative_generation',
                options: options
            };

            const response = await fetch(`${this.serverUrl}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            this.currentMission = 'creative_generation';
            
            return result;
        } catch (error) {
            console.error('Creative generation failed:', error);
            throw new Error(`Failed to generate creative assets: ${error.message}`);
        }
    }

    /**
     * Start a specific mission
     */
    async startMission(missionType, context = {}) {
        try {
            const requestData = {
                sessionId: this.sessionId,
                missionType: missionType,
                context: context
            };

            const response = await fetch(`${this.serverUrl}/api/mission/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            this.currentMission = missionType;
            
            return result;
        } catch (error) {
            console.error('Mission start failed:', error);
            throw new Error(`Failed to start mission: ${error.message}`);
        }
    }

    /**
     * Get session summary and export data
     */
    async exportSession() {
        try {
            const sessionData = {
                sessionId: this.sessionId,
                startTime: this.sessionStartTime,
                endTime: Date.now(),
                conversationHistory: this.conversationHistory,
                userProfile: this.userProfile,
                currentMission: this.currentMission
            };

            return {
                sessionData: sessionData,
                summary: `Session ${this.sessionId} - ${this.conversationHistory.length} interactions`,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error('Session export failed:', error);
            throw new Error(`Failed to export session: ${error.message}`);
        }
    }

    /**
     * Update user preferences
     */
    updateUserProfile(updates) {
        this.userProfile = { ...this.userProfile, ...updates };
    }

    /**
     * Clear conversation history
     */
    clearHistory() {
        this.conversationHistory = [];
        this.currentMission = null;
    }
}
