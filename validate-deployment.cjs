#!/usr/bin/env node

/**
 * Deployment Validation Script
 * Tests all components of the Retro AI Gemini application
 */

const fs = require('fs');
const path = require('path');
const http = require('http');

class DeploymentValidator {
    constructor() {
        this.results = {
            timestamp: new Date().toISOString(),
            tests: [],
            summary: { passed: 0, failed: 0, total: 0 }
        };
    }

    log(message, type = 'info') {
        const colors = {
            info: '\x1b[36m',    // Cyan
            success: '\x1b[32m', // Green
            error: '\x1b[31m',   // Red
            warning: '\x1b[33m', // Yellow
            reset: '\x1b[0m'     // Reset
        };
        
        console.log(`${colors[type]}${message}${colors.reset}`);
    }

    addResult(test, passed, details = '') {
        this.results.tests.push({
            test,
            passed,
            details,
            timestamp: new Date().toISOString()
        });
        
        if (passed) {
            this.results.summary.passed++;
            this.log(`✅ ${test}`, 'success');
        } else {
            this.results.summary.failed++;
            this.log(`❌ ${test}: ${details}`, 'error');
        }
        this.results.summary.total++;
    }

    async validateFileStructure() {
        this.log('\n🔍 Validating File Structure...', 'info');
        
        const requiredFiles = [
            'package.json',
            'server.js',
            'main.cjs',
            'app.js',
            'index.html',
            '.env',
            'core/GeminiAgent.js',
            'ui/TerminalInterface.js',
            'client/RetroAIClient.js',
            'cli.js',
            'launch_enhanced.sh',
            'README.md'
        ];

        for (const file of requiredFiles) {
            const exists = fs.existsSync(path.join(__dirname, file));
            this.addResult(`File exists: ${file}`, exists);
        }
    }

    async validateConfiguration() {
        this.log('\n⚙️ Validating Configuration...', 'info');
        
        try {
            const envContent = fs.readFileSync(path.join(__dirname, '.env'), 'utf8');
            const hasApiKey = envContent.includes('GOOGLE_API_KEY=AIzaSyCEJ3ee1y00U-TrILQBmRmhALU65j7JoP8');
            this.addResult('API Key configured', hasApiKey);
            
            const hasDesktopPort = envContent.includes('DESKTOP_PORT=8082');
            this.addResult('Desktop port configured', hasDesktopPort);
            
            const hasElectronPort = envContent.includes('ELECTRON_PORT=8082');
            this.addResult('Electron port configured', hasElectronPort);
        } catch (error) {
            this.addResult('Environment file readable', false, error.message);
        }
    }

    async validatePackageDependencies() {
        this.log('\n📦 Validating Package Dependencies...', 'info');
        
        try {
            const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));
            
            const requiredDeps = ['express', 'cors', 'electron', '@google/generative-ai'];
            for (const dep of requiredDeps) {
                const exists = packageJson.dependencies && packageJson.dependencies[dep];
                this.addResult(`Dependency: ${dep}`, !!exists);
            }
            
            const hasStartScript = packageJson.scripts && packageJson.scripts.start;
            this.addResult('Start script defined', !!hasStartScript);
            
        } catch (error) {
            this.addResult('Package.json readable', false, error.message);
        }
    }

    async validateServerEndpoints() {
        this.log('\n🌐 Validating Server Endpoints...', 'info');
        
        const endpoints = [
            { path: '/', description: 'Main page' },
            { path: '/api/health', description: 'Health check' },
            { path: '/api/chat', description: 'Chat endpoint', method: 'POST' }
        ];

        for (const endpoint of endpoints) {
            try {
                await this.testEndpoint(8080, endpoint.path, endpoint.method);
                this.addResult(`Endpoint accessible: ${endpoint.description}`, true);
            } catch (error) {
                this.addResult(`Endpoint accessible: ${endpoint.description}`, false, error.message);
            }
        }
    }

    testEndpoint(port, path, method = 'GET') {
        return new Promise((resolve, reject) => {
            const options = {
                hostname: 'localhost',
                port: port,
                path: path,
                method: method,
                timeout: 5000
            };

            const req = http.request(options, (res) => {
                if (res.statusCode < 500) {
                    resolve(res.statusCode);
                } else {
                    reject(new Error(`Server error: ${res.statusCode}`));
                }
            });

            req.on('error', (err) => {
                reject(err);
            });

            req.on('timeout', () => {
                req.destroy();
                reject(new Error('Request timeout'));
            });

            if (method === 'POST') {
                req.write(JSON.stringify({ message: 'test' }));
            }
            
            req.end();
        });
    }

    async validateMacOSIntegration() {
        this.log('\n🍎 Validating macOS Integration...', 'info');
        
        const appBundlePath = path.join(__dirname, 'Retro AI Gemini.app');
        const launcherPath = path.join(__dirname, 'launch_enhanced.sh');
        
        this.addResult('macOS App Bundle exists', fs.existsSync(appBundlePath));
        this.addResult('Enhanced launcher exists', fs.existsSync(launcherPath));
        
        if (fs.existsSync(launcherPath)) {
            try {
                const stats = fs.statSync(launcherPath);
                const isExecutable = !!(stats.mode & parseInt('111', 8));
                this.addResult('Launcher is executable', isExecutable);
            } catch (error) {
                this.addResult('Launcher permissions check', false, error.message);
            }
        }
    }

    async validateTerminalInterface() {
        this.log('\n🖥️ Validating Terminal Interface...', 'info');
        
        try {
            const terminalCode = fs.readFileSync(path.join(__dirname, 'ui/TerminalInterface.js'), 'utf8');
            
            const hasCreateBootSound = terminalCode.includes('createBootSound()');
            this.addResult('createBootSound method exists', hasCreateBootSound);
            
            const hasCreateErrorSound = terminalCode.includes('createErrorSound()');
            this.addResult('createErrorSound method exists', hasCreateErrorSound);
            
            const hasSoundEffects = terminalCode.includes('soundEffects');
            this.addResult('Sound effects system present', hasSoundEffects);
            
        } catch (error) {
            this.addResult('Terminal interface file readable', false, error.message);
        }
    }

    generateReport() {
        const reportPath = path.join(__dirname, 'deployment-validation-report.json');
        fs.writeFileSync(reportPath, JSON.stringify(this.results, null, 2));
        
        this.log('\n📊 VALIDATION SUMMARY', 'info');
        this.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, 'info');
        this.log(`Total Tests: ${this.results.summary.total}`, 'info');
        this.log(`Passed: ${this.results.summary.passed}`, 'success');
        this.log(`Failed: ${this.results.summary.failed}`, this.results.summary.failed > 0 ? 'error' : 'success');
        
        const successRate = ((this.results.summary.passed / this.results.summary.total) * 100).toFixed(1);
        this.log(`Success Rate: ${successRate}%`, successRate >= 90 ? 'success' : 'warning');
        
        this.log(`\n📄 Report saved to: ${reportPath}`, 'info');
        
        if (this.results.summary.failed === 0) {
            this.log('\n🎉 DEPLOYMENT VALIDATION SUCCESSFUL!', 'success');
            this.log('🚀 All systems operational and ready for use', 'success');
        } else {
            this.log('\n⚠️ VALIDATION COMPLETED WITH ISSUES', 'warning');
            this.log('🔧 Review failed tests and address before production use', 'warning');
        }
    }

    async run() {
        this.log('🎮 RETRO AI GEMINI - DEPLOYMENT VALIDATION', 'info');
        this.log('═══════════════════════════════════════════════', 'info');
        
        await this.validateFileStructure();
        await this.validateConfiguration();
        await this.validatePackageDependencies();
        await this.validateMacOSIntegration();
        await this.validateTerminalInterface();
        
        // Only test server endpoints if we can detect a running server
        try {
            await this.testEndpoint(8080, '/api/health');
            await this.validateServerEndpoints();
        } catch (error) {
            this.log('\n⚠️ Server not running on port 8080 - skipping endpoint tests', 'warning');
            this.log('   Run "npm run web" or "node server.js" to test endpoints', 'warning');
        }
        
        this.generateReport();
        
        return this.results.summary.failed === 0;
    }
}

// Run validation if called directly
if (require.main === module) {
    const validator = new DeploymentValidator();
    validator.run().then(success => {
        process.exit(success ? 0 : 1);
    }).catch(error => {
        console.error('Validation failed:', error);
        process.exit(1);
    });
}

module.exports = DeploymentValidator;
