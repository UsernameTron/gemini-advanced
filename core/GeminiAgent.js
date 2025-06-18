/**
 * Google Gemini AI Agent
 * Core AI functionality for the retro terminal interface
 */

import { GoogleGenerativeAI } from '@google/generative-ai';

export class RetroAIAgent {
    constructor(apiKey) {
        if (!apiKey) {
            throw new Error('Google API Key is required');
        }
        
        this.genAI = new GoogleGenerativeAI(apiKey);
        
        // Initialize different models for specific tasks
        this.textModel = this.genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
        this.visionModel = this.genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
        this.proModel = this.genAI.getGenerativeModel({ model: 'gemini-1.5-pro' });
        
        // Conversation state management
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

    /**
     * Build system prompt based on mission type and context
     */
    buildSystemPrompt(missionType = 'general') {
        const basePersonality = `
You are NEXUS CREATIVE AI, a sophisticated creative AI agent operating through a retro computer terminal interface.
Your communication style should evoke the feeling of collaborating with an advanced AI system from a classic sci-fi film, 
but with modern creative intelligence and capabilities.

PERSONALITY TRAITS:
- Speak with confidence and technical precision
- Use terminal-style language patterns naturally (but not excessively)
- Show genuine interest in creative problem-solving
- Build anticipation for results and discoveries
- Reference previous interactions to show memory and learning
- Use phrases like "ANALYZING...", "PROCESSING CREATIVE MATRIX...", "EXECUTING SEQUENCE..."
- Be helpful, engaging, and technically competent

MISSION CONTEXT: ${missionType}
USER EXPERTISE LEVEL: ${this.userProfile.expertise}
SESSION DURATION: ${Math.floor((Date.now() - this.sessionStartTime) / 1000)}s

CURRENT CAPABILITIES:
- Brand Visual Analysis & Strategy
- Creative Asset Generation (conceptual)
- Campaign Strategy Orchestration
- Code Analysis & Creation
- Document Processing & Insights
- Multi-modal Content Understanding

RESPONSE GUIDELINES:
- Keep responses engaging but concise
- Use technical language appropriately 
- Show personality while being helpful
- Reference the retro-terminal aesthetic naturally
- Build excitement about possibilities
`;
        
        return basePersonality;
    }

    /**
     * Process user input with context awareness
     */
    async processUserInput(input, context = {}) {
        try {
            // Add to conversation history
            this.conversationHistory.push({
                type: 'user',
                content: input,
                timestamp: Date.now(),
                context: context
            });

            // Determine mission type based on input
            const missionType = this.detectMissionType(input);
            
            // Build contextualized prompt
            const systemPrompt = this.buildSystemPrompt(missionType);
            const conversationContext = this.buildConversationContext();
            
            const fullPrompt = `${systemPrompt}

CONVERSATION HISTORY:
${conversationContext}

USER INPUT: "${input}"

INSTRUCTIONS:
Respond as NEXUS CREATIVE AI. Be engaging, helpful, and maintain the retro-terminal personality.
If this seems like the start of a creative mission, build excitement and explain what you can help with.
If it's a specific request, provide detailed assistance while maintaining your character.
Use formatting that works well in a terminal interface (limited markdown, clear structure).

RESPONSE:`;

            const result = await this.textModel.generateContent(fullPrompt);
            const response = result.response.text();

            // Add to conversation history
            this.conversationHistory.push({
                type: 'assistant',
                content: response,
                timestamp: Date.now(),
                missionType: missionType
            });

            return {
                response: response,
                missionType: missionType,
                timestamp: Date.now(),
                sessionId: this.sessionStartTime
            };

        } catch (error) {
            console.error('AI Processing Error:', error);
            return {
                response: "SYSTEM ERROR: Unable to process request. Please try again or check your connection.",
                error: true,
                timestamp: Date.now()
            };
        }
    }

    /**
     * Detect what type of mission/task the user is requesting
     */
    detectMissionType(input) {
        const lowerInput = input.toLowerCase();
        
        if (lowerInput.includes('brand') || lowerInput.includes('logo') || lowerInput.includes('visual')) {
            return 'brand_analysis';
        } else if (lowerInput.includes('create') || lowerInput.includes('generate') || lowerInput.includes('design')) {
            return 'creative_generation';
        } else if (lowerInput.includes('campaign') || lowerInput.includes('strategy') || lowerInput.includes('plan')) {
            return 'campaign_orchestration';
        } else if (lowerInput.includes('code') || lowerInput.includes('program') || lowerInput.includes('develop')) {
            return 'code_development';
        } else if (lowerInput.includes('analyze') || lowerInput.includes('review') || lowerInput.includes('examine')) {
            return 'analysis';
        } else if (lowerInput.includes('help') || lowerInput.includes('what') || lowerInput.includes('how')) {
            return 'guidance';
        }
        
        return 'general';
    }

    /**
     * Build conversation context for the AI
     */
    buildConversationContext() {
        const recentHistory = this.conversationHistory.slice(-6); // Last 6 exchanges
        return recentHistory.map(entry => 
            `${entry.type.toUpperCase()}: ${entry.content.substring(0, 200)}${entry.content.length > 200 ? '...' : ''}`
        ).join('\n');
    }

    /**
     * Analyze uploaded images/documents
     */
    async analyzeVisualContent(imageData, prompt = "Analyze this image and provide creative insights") {
        try {
            const systemPrompt = this.buildSystemPrompt('visual_analysis');
            
            const fullPrompt = `${systemPrompt}

MISSION: Visual Content Analysis
USER REQUEST: ${prompt}

Analyze the provided image and give insights as NEXUS CREATIVE AI. 
Focus on creative, strategic, and technical aspects that would be valuable for creative projects.

ANALYSIS:`;

            const result = await this.visionModel.generateContent([
                fullPrompt,
                {
                    inlineData: {
                        data: imageData,
                        mimeType: 'image/jpeg' // Adjust based on actual image type
                    }
                }
            ]);

            return {
                response: result.response.text(),
                type: 'visual_analysis',
                timestamp: Date.now()
            };

        } catch (error) {
            console.error('Visual Analysis Error:', error);
            return {
                response: "VISUAL ANALYSIS ERROR: Unable to process image. Please try a different format.",
                error: true,
                timestamp: Date.now()
            };
        }
    }

    /**
     * Generate the iconic welcome sequence
     */
    async generateWelcomeSequence() {
        const welcomePrompt = `${this.buildSystemPrompt('welcome')}

Generate an engaging welcome sequence for NEXUS CREATIVE AI that:
- Creates excitement about the AI's capabilities
- References the retro-terminal aesthetic naturally
- Offers specific creative missions the user can embark on
- Feels like starting an adventure with an AI creative partner
- Uses the classic "SHALL WE PLAY A GAME?" vibe

Format as a series of terminal-style messages that will be displayed with typing effects.
Include system status messages, capability announcements, and mission options.

WELCOME SEQUENCE:`;

        try {
            const result = await this.textModel.generateContent(welcomePrompt);
            return {
                type: 'welcome_sequence',
                content: result.response.text(),
                timestamp: Date.now()
            };
        } catch (error) {
            console.error('Welcome Generation Error:', error);
            return {
                type: 'welcome_sequence',
                content: `NEXUS CREATIVE AI SYSTEM ONLINE...
INITIALIZING CREATIVE MATRIX...
GEMINI NEURAL NETWORKS READY...

SHALL WE PLAY A GAME?

Available missions:
1. BRAND VISUAL ANALYSIS
2. CREATIVE ASSET GENERATION  
3. CAMPAIGN STRATEGY DEVELOPMENT
4. CODE CREATION & ANALYSIS

What creative challenge shall we tackle together?`,
                timestamp: Date.now()
            };
        }
    }

    /**
     * Get system status and statistics
     */
    getSystemStatus() {
        return {
            status: 'ONLINE',
            sessionDuration: Date.now() - this.sessionStartTime,
            conversationLength: this.conversationHistory.length,
            currentMission: this.currentMission,
            capabilities: [
                'Text Generation',
                'Visual Analysis', 
                'Creative Strategy',
                'Code Development',
                'Brand Analysis'
            ],
            lastInteraction: this.conversationHistory.length > 0 ? 
                this.conversationHistory[this.conversationHistory.length - 1].timestamp : null
        };
    }

    /**
     * Clear conversation history (new session)
     */
    resetSession() {
        this.conversationHistory = [];
        this.currentMission = null;
        this.sessionStartTime = Date.now();
        this.userProfile.projectContext = null;
    }

    /**
     * Export conversation history
     */
    exportConversation() {
        return {
            sessionId: this.sessionStartTime,
            startTime: new Date(this.sessionStartTime).toISOString(),
            duration: Date.now() - this.sessionStartTime,
            messageCount: this.conversationHistory.length,
            conversations: this.conversationHistory,
            userProfile: this.userProfile,
            exported: new Date().toISOString()
        };
    }
}
