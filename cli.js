#!/usr/bin/env node

/**
 * Retro AI Gemini CLI Tool
 * Quick command-line interface for power users
 */

import { GoogleGenerativeAI } from '@google/generative-ai';
import { createReadStream } from 'fs';
import { readFile } from 'fs/promises';
import dotenv from 'dotenv';
import readline from 'readline';

// Load environment variables
dotenv.config();

class RetroAICLI {
    constructor() {
        this.apiKey = process.env.GOOGLE_API_KEY;
        if (!this.apiKey) {
            console.error('❌ GOOGLE_API_KEY not found in environment');
            process.exit(1);
        }
        
        this.genAI = new GoogleGenerativeAI(this.apiKey);
        this.model = this.genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
        this.conversationHistory = [];
    }

    async executeCommand(command, args) {
        switch (command) {
            case 'chat':
            case 'ask':
                await this.chatMode(args.join(' '));
                break;
            case 'analyze':
                await this.analyzeFile(args[0]);
                break;
            case 'generate':
                await this.generateContent(args.join(' '));
                break;
            case 'interactive':
            case 'i':
                await this.interactiveMode();
                break;
            case 'version':
                console.log('Retro AI Gemini CLI v1.0.0');
                break;
            case 'help':
            default:
                this.showHelp();
                break;
        }
    }

    async chatMode(message) {
        if (!message) {
            console.error('❌ Please provide a message');
            return;
        }

        try {
            console.log('🤖 NEXUS AI Processing...\n');
            
            const prompt = `
You are NEXUS CREATIVE AI operating in CLI mode. Be concise but helpful.
Maintain the retro AI personality while being practical for command-line use.

User: ${message}
`;

            const result = await this.model.generateContent(prompt);
            const response = result.response.text();
            
            console.log('📝 Response:');
            console.log(response);
            console.log('\n✅ Complete\n');

        } catch (error) {
            console.error('❌ Error:', error.message);
        }
    }

    async analyzeFile(filePath) {
        if (!filePath) {
            console.error('❌ Please provide a file path');
            return;
        }

        try {
            console.log(`🔍 Analyzing file: ${filePath}...`);
            
            // For now, just analyze text files
            const content = await readFile(filePath, 'utf-8');
            
            const prompt = `
Analyze this file content from a creative and strategic perspective:

File: ${filePath}
Content:
${content.slice(0, 2000)}...

Provide insights on:
- Content quality and clarity
- Strategic messaging
- Improvement suggestions
- Creative opportunities
`;

            const result = await this.model.generateContent(prompt);
            const analysis = result.response.text();
            
            console.log('\n📊 Analysis Results:');
            console.log(analysis);
            console.log('\n✅ Analysis Complete\n');

        } catch (error) {
            console.error('❌ Error analyzing file:', error.message);
        }
    }

    async generateContent(prompt) {
        if (!prompt) {
            console.error('❌ Please provide a generation prompt');
            return;
        }

        try {
            console.log('🎨 Generating creative content...\n');
            
            const enhancedPrompt = `
You are NEXUS CREATIVE AI. Generate creative content based on this request:

Request: ${prompt}

Provide creative, professional content that's ready to use.
Include multiple variations or approaches when appropriate.
`;

            const result = await this.model.generateContent(enhancedPrompt);
            const generated = result.response.text();
            
            console.log('🎯 Generated Content:');
            console.log(generated);
            console.log('\n✅ Generation Complete\n');

        } catch (error) {
            console.error('❌ Error generating content:', error.message);
        }
    }

    async interactiveMode() {
        console.log(`
╔══════════════════════════════════════════════════════════════╗
║                    NEXUS CREATIVE AI                         ║
║                 Interactive CLI Mode                         ║
║              Type 'exit' to quit                             ║
╚══════════════════════════════════════════════════════════════╝
`);

        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
            prompt: 'NEXUS> '
        });

        rl.prompt();

        rl.on('line', async (input) => {
            const trimmed = input.trim();
            
            if (trimmed === 'exit' || trimmed === 'quit') {
                console.log('👋 Goodbye from NEXUS AI!');
                rl.close();
                return;
            }

            if (trimmed === 'clear') {
                console.clear();
                rl.prompt();
                return;
            }

            if (trimmed === 'history') {
                console.log('\n📝 Conversation History:');
                this.conversationHistory.forEach((item, index) => {
                    console.log(`${index + 1}. ${item.slice(0, 100)}...`);
                });
                console.log('');
                rl.prompt();
                return;
            }

            if (trimmed) {
                try {
                    console.log('\n🤖 Processing...');
                    
                    const result = await this.model.generateContent(`
You are NEXUS CREATIVE AI in interactive mode. Be helpful and engaging.

User: ${trimmed}
`);
                    
                    const response = result.response.text();
                    console.log('\n💡 NEXUS:', response);
                    
                    this.conversationHistory.push(trimmed);
                    
                } catch (error) {
                    console.error('\n❌ Error:', error.message);
                }
            }
            
            console.log('');
            rl.prompt();
        });

        rl.on('close', () => {
            process.exit(0);
        });
    }

    showHelp() {
        console.log(`
╔══════════════════════════════════════════════════════════════╗
║                    NEXUS CREATIVE AI CLI                     ║
║                   Command Reference                          ║
╚══════════════════════════════════════════════════════════════╝

Usage: retro-cli <command> [arguments]

Commands:
  chat <message>        Send a message to NEXUS AI
  ask <question>        Ask a question (alias for chat)
  generate <prompt>     Generate creative content
  analyze <file>        Analyze a file's content
  interactive, i        Enter interactive chat mode
  version               Show version information
  help                  Show this help message

Examples:
  retro-cli chat "Hello NEXUS, help me with my project"
  retro-cli generate "Write a tagline for a tech startup"
  retro-cli analyze ./my-document.txt
  retro-cli interactive

Interactive Mode Commands:
  exit, quit           Leave interactive mode
  clear               Clear the screen
  history             Show conversation history

Environment:
  GOOGLE_API_KEY      Your Google Gemini API key (required)

For more information, visit: https://github.com/UsernameTron/gemini
`);
    }
}

// Main execution
async function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    const commandArgs = args.slice(1);

    const cli = new RetroAICLI();
    await cli.executeCommand(command, commandArgs);
}

// Handle uncaught errors
process.on('uncaughtException', (error) => {
    console.error('❌ Fatal error:', error.message);
    process.exit(1);
});

process.on('unhandledRejection', (reason) => {
    console.error('❌ Unhandled rejection:', reason);
    process.exit(1);
});

// Run the CLI
main().catch(console.error);
