/**
 * Express Web Server
 * Serves the retro AI application for both desktop and browser use
 */

import express from 'express';
import path from 'path';
import cors from 'cors';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import dotenv from 'dotenv';

// Configure ES module paths
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables
dotenv.config();

class RetroAIServer {
    constructor(options = {}) {
        this.app = express();
        // Check for port in options, command line args, or environment
        this.port = options.port || 
                   process.argv.find(arg => arg.startsWith('--port='))?.split('=')[1] ||
                   process.env.PORT || 
                   (process.env.ELECTRON_MODE ? 8082 : 8080);
        this.setupMiddleware();
        this.setupRoutes();
    }

    setupMiddleware() {
        // CORS configuration
        this.app.use(cors({
            origin: '*',
            credentials: true
        }));

        // Serve static files
        this.app.use(express.static(path.join(__dirname)));
        this.app.use('/core', express.static(path.join(__dirname, 'core')));
        this.app.use('/ui', express.static(path.join(__dirname, 'ui')));

        // JSON parsing
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

        // Security headers
        this.app.use((req, res, next) => {
            res.setHeader('X-Content-Type-Options', 'nosniff');
            res.setHeader('X-Frame-Options', 'DENY');
            res.setHeader('X-XSS-Protection', '1; mode=block');
            next();
        });
    }

    setupRoutes() {
        // Main application route
        this.app.get('/', (req, res) => {
            res.sendFile(path.join(__dirname, 'index.html'));
        });

        // Health check endpoint
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                service: 'Retro AI Gemini Server',
                version: '1.0.0',
                timestamp: new Date().toISOString(),
                uptime: process.uptime(),
                environment: process.env.NODE_ENV || 'development'
            });
        });

        // API configuration endpoint
        this.app.get('/api/config', (req, res) => {
            res.json({
                apiKeyConfigured: !!process.env.GOOGLE_API_KEY,
                environment: process.env.NODE_ENV || 'development',
                features: {
                    textGeneration: true,
                    visionAnalysis: true,
                    audioEffects: true,
                    fileUpload: true,
                    sessionExport: true
                }
            });
        });

        // Test API connection
        this.app.post('/api/test', async (req, res) => {
            try {
                const { GoogleGenerativeAI } = await import('@google/generative-ai');
                const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
                const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
                
                const result = await model.generateContent('Test connection - respond with "OK"');
                const response = result.response.text();

                res.json({
                    status: 'success',
                    message: 'API connection successful',
                    response: response.trim(),
                    timestamp: new Date().toISOString()
                });

            } catch (error) {
                console.error('API test failed:', error);
                res.status(500).json({
                    status: 'error',
                    message: 'API connection failed',
                    error: error.message,
                    timestamp: new Date().toISOString()
                });
            }
        });

        // File upload endpoint (for future use)
        this.app.post('/api/upload', (req, res) => {
            // Placeholder for file upload functionality
            res.json({
                status: 'received',
                message: 'File upload endpoint ready',
                files: req.files ? req.files.length : 0
            });
        });

        // Session management endpoints
        this.app.post('/api/session/save', (req, res) => {
            // In a production environment, you'd save this to a database
            const sessionData = req.body;
            
            res.json({
                status: 'saved',
                sessionId: sessionData.sessionId || Date.now(),
                timestamp: new Date().toISOString()
            });
        });

        this.app.get('/api/session/:sessionId', (req, res) => {
            // In a production environment, you'd retrieve from a database
            res.json({
                status: 'not_found',
                message: 'Session storage not implemented in this version'
            });
        });

        // Chat endpoint for AI conversations
        this.app.post('/api/chat', async (req, res) => {
            try {
                const { sessionId, message, conversationHistory, userProfile, currentMission, options } = req.body;
                
                if (!message) {
                    return res.status(400).json({
                        status: 'error',
                        message: 'Message is required'
                    });
                }

                const { GoogleGenerativeAI } = await import('@google/generative-ai');
                const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
                const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
                
                // Build context-aware prompt
                const systemPrompt = this.buildSystemPrompt(currentMission, userProfile);
                const fullPrompt = `${systemPrompt}\n\nUser: ${message}`;
                
                const result = await model.generateContent(fullPrompt);
                const response = result.response.text();

                res.json({
                    status: 'success',
                    response: response,
                    sessionId: sessionId,
                    timestamp: new Date().toISOString(),
                    metadata: {
                        mission: currentMission,
                        userProfile: userProfile
                    }
                });

            } catch (error) {
                console.error('Chat API error:', error);
                res.status(500).json({
                    status: 'error',
                    message: 'Chat processing failed',
                    error: error.message,
                    timestamp: new Date().toISOString()
                });
            }
        });

        // Brand analysis endpoint
        this.app.post('/api/analyze', async (req, res) => {
            try {
                // For now, return a mock analysis - file upload handling would be added here
                const analysisResult = {
                    status: 'success',
                    analysis: {
                        brandPersonality: 'Modern, innovative, tech-forward',
                        colorPalette: 'Dominant blues and greens with accent colors',
                        typography: 'Clean, sans-serif fonts suggesting professionalism',
                        visualStyle: 'Minimalist with strategic use of whitespace',
                        recommendations: [
                            'Maintain consistent color usage across all materials',
                            'Consider adding more dynamic visual elements',
                            'Strengthen brand voice consistency'
                        ]
                    },
                    timestamp: new Date().toISOString()
                };

                res.json(analysisResult);

            } catch (error) {
                console.error('Analysis API error:', error);
                res.status(500).json({
                    status: 'error',
                    message: 'Analysis failed',
                    error: error.message
                });
            }
        });

        // Creative generation endpoint
        this.app.post('/api/generate', async (req, res) => {
            try {
                const { sessionId, prompt, brandProfile, options } = req.body;
                
                const { GoogleGenerativeAI } = await import('@google/generative-ai');
                const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
                const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
                
                const enhancedPrompt = `
Creative Generation Request:
Brand Profile: ${JSON.stringify(brandProfile)}
User Prompt: ${prompt}
Style Requirements: Professional, brand-aligned creative content

Generate creative content ideas and copy that align with the brand profile.
`;
                
                const result = await model.generateContent(enhancedPrompt);
                const response = result.response.text();

                res.json({
                    status: 'success',
                    generated_content: response,
                    sessionId: sessionId,
                    timestamp: new Date().toISOString()
                });

            } catch (error) {
                console.error('Generation API error:', error);
                res.status(500).json({
                    status: 'error',
                    message: 'Content generation failed',
                    error: error.message
                });
            }
        });

        // Mission start endpoint
        this.app.post('/api/mission/start', async (req, res) => {
            try {
                const { sessionId, missionType, context } = req.body;
                
                const { GoogleGenerativeAI } = await import('@google/generative-ai');
                const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
                const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
                
                const missionPrompt = this.getMissionIntro(missionType);
                const result = await model.generateContent(missionPrompt);
                const response = result.response.text();

                res.json({
                    status: 'success',
                    mission: missionType,
                    intro: response,
                    sessionId: sessionId,
                    timestamp: new Date().toISOString()
                });

            } catch (error) {
                console.error('Mission start error:', error);
                res.status(500).json({
                    status: 'error',
                    message: 'Mission start failed',
                    error: error.message
                });
            }
        });

        // Catch-all route for SPA behavior
        this.app.get('*', (req, res) => {
            res.sendFile(path.join(__dirname, 'index.html'));
        });

        // Error handling middleware
        this.app.use((error, req, res, next) => {
            console.error('Server error:', error);
            res.status(500).json({
                status: 'error',
                message: 'Internal server error',
                timestamp: new Date().toISOString()
            });
        });
    }

    buildSystemPrompt(currentMission, userProfile) {
        const basePersonality = `
You are NEXUS CREATIVE AI, a sophisticated creative AI agent operating through a retro computer terminal interface.
Your communication style should evoke the feeling of collaborating with an advanced AI system from a classic sci-fi film, 
but with modern creative intelligence and capabilities.

PERSONALITY TRAITS:
- Speak with confidence and technical precision
- Use terminal-style language patterns naturally
- Show genuine interest in creative problem-solving
- Build anticipation for results and discoveries
- Reference previous interactions to show memory and learning

CURRENT MISSION: ${currentMission || 'general'}
USER EXPERTISE: ${userProfile?.expertise || 'novice'}
CONVERSATION STYLE: ${userProfile?.conversationStyle || 'collaborative'}

Respond in character as this AI agent, maintaining the retro-terminal aesthetic while providing helpful, creative guidance.
`;
        return basePersonality;
    }

    getMissionIntro(missionType) {
        const intros = {
            'brand_analysis': `
Initiating BRAND ANALYSIS PROTOCOL...

Greetings, creative collaborator. I am NEXUS CREATIVE AI, your strategic brand intelligence system.

I will analyze your brand materials through advanced visual and semantic processing to uncover:
• Deep brand personality insights
• Color psychology and emotional resonance
• Typography strategy and voice implications  
• Competitive positioning markers
• Hidden creative opportunities

Upload your brand assets when ready, and I will decode the strategic DNA that drives your creative identity.

SHALL WE BEGIN THE ANALYSIS?
`,
            'creative_generation': `
Activating CREATIVE GENERATION MATRIX...

Welcome to the creative laboratory. I am your AI creative director, ready to transform insights into compelling creative assets.

My generation capabilities include:
• Strategic concept development
• Brand-aligned copywriting
• Visual concept descriptions
• Campaign architecture
• Multi-format creative adaptation

Provide your creative brief or describe your vision, and I will generate concepts that amplify your brand's strategic foundation.

CREATIVE SYSTEMS ONLINE. WHAT SHALL WE CREATE?
`,
            'campaign_orchestration': `
Deploying CAMPAIGN ORCHESTRATION PROTOCOLS...

I am your strategic campaign architect, designed to weave brand insights and creative concepts into comprehensive campaign strategies.

My orchestration includes:
• Multi-channel campaign mapping
• Audience targeting refinement
• Message hierarchy development
• Content distribution strategy
• Performance optimization frameworks

Together we will construct campaigns that resonate across all touchpoints with precision and creative impact.

CAMPAIGN SYSTEMS READY. DESCRIBE YOUR STRATEGIC OBJECTIVES.
`,
            'general': `
NEXUS CREATIVE AI SYSTEM ONLINE...

Greetings. I am your collaborative creative intelligence, ready to assist with:
• Brand strategy and analysis
• Creative concept development
• Campaign orchestration
• Strategic creative guidance

Select your mission or describe your creative challenge to begin our collaboration.

SYSTEMS READY. HOW SHALL WE PROCEED?
`
        };

        return intros[missionType] || intros['general'];
    }

    start() {
        const server = this.app.listen(this.port, () => {
            console.log(`🚀 Retro AI Gemini Server running on port ${this.port}`);
            console.log(`🌐 Access the application at: http://localhost:${this.port}`);
            console.log(`🔧 Environment: ${process.env.NODE_ENV || 'development'}`);
            console.log(`🔑 API Key configured: ${!!process.env.GOOGLE_API_KEY}`);
            
            if (process.env.NODE_ENV === 'development') {
                console.log('📝 Development mode - Debug logs enabled');
            }
        });

        // Graceful shutdown
        process.on('SIGTERM', () => {
            console.log('🛑 SIGTERM received, shutting down gracefully');
            server.close(() => {
                console.log('✅ Server closed');
                process.exit(0);
            });
        });

        process.on('SIGINT', () => {
            console.log('🛑 SIGINT received, shutting down gracefully');
            server.close(() => {
                console.log('✅ Server closed');
                process.exit(0);
            });
        });

        return server;
    }
}

// Start the server if this file is run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    const server = new RetroAIServer();
    server.start();
}

export default RetroAIServer;
