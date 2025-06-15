/*
Real-time Brand Deconstruction Platform
Advanced WebSocket integration and real-time functionality
*/

class RealTimePlatform {
    constructor() {
        this.ws = null;
        this.connectionStatus = 'disconnected';
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.listeners = new Map();
        this.messageQueue = [];
        
        this.init();
    }

    init() {
        this.connectWebSocket();
        this.setupEventListeners();
        this.setupActivityFeed();
        this.setupProgressTracking();
    }

    // WebSocket Connection Management
    connectWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.connectionStatus = 'connected';
                this.reconnectAttempts = 0;
                this.updateConnectionStatus('connected');
                this.processMessageQueue();
                this.emit('connection', { status: 'connected' });
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.connectionStatus = 'disconnected';
                this.updateConnectionStatus('disconnected');
                this.emit('connection', { status: 'disconnected' });
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.connectionStatus = 'error';
                this.updateConnectionStatus('error');
                this.emit('connection', { status: 'error', error });
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.connectionStatus = 'error';
            this.updateConnectionStatus('error');
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
            this.showToast('Connection lost. Please refresh the page.', 'error');
        }
    }

    // Message Handling
    handleMessage(data) {
        console.log('Received WebSocket message:', data);
        
        switch (data.type) {
            case 'analysis_update':
                this.handleAnalysisUpdate(data);
                break;
            case 'image_generation_update':
                this.handleImageGenerationUpdate(data);
                break;
            case 'agent_status':
                this.handleAgentStatus(data);
                break;
            case 'error':
                this.handleError(data);
                break;
            case 'activity':
                this.handleActivity(data);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
        
        this.emit(data.type, data);
    }

    handleAnalysisUpdate(data) {
        const { brand, stage, progress, results } = data;
        
        // Update progress indicator
        this.updateProgress(stage, progress);
        
        // Update results if available
        if (results) {
            this.updateAnalysisResults(results);
        }
        
        // Add to activity feed
        this.addActivity(`Brand analysis update: ${stage} (${progress}%)`);
    }

    handleImageGenerationUpdate(data) {
        const { stage, progress, concept, image_url, error } = data;
        
        // Update image generation workflow
        this.updateImageWorkflow(stage, progress, concept, image_url, error);
        
        // Add to activity feed
        if (image_url) {
            this.addActivity('Image generation completed');
        } else if (error) {
            this.addActivity(`Image generation error: ${error}`);
        } else {
            this.addActivity(`Image generation: ${stage} (${progress}%)`);
        }
    }

    handleAgentStatus(data) {
        const { agent, status, capabilities } = data;
        this.updateAgentStatus(agent, status, capabilities);
        this.addActivity(`Agent ${agent}: ${status}`);
    }

    handleError(data) {
        const { message, code } = data;
        this.showToast(message, 'error');
        this.addActivity(`Error: ${message}`);
    }

    handleActivity(data) {
        const { message, timestamp } = data;
        this.addActivity(message, timestamp);
    }

    // Send Message with Queue Support
    send(message) {
        if (this.connectionStatus === 'connected' && this.ws) {
            try {
                this.ws.send(JSON.stringify(message));
                return true;
            } catch (error) {
                console.error('Error sending message:', error);
                this.messageQueue.push(message);
                return false;
            }
        } else {
            this.messageQueue.push(message);
            return false;
        }
    }

    processMessageQueue() {
        while (this.messageQueue.length > 0 && this.connectionStatus === 'connected') {
            const message = this.messageQueue.shift();
            this.send(message);
        }
    }

    // Event System
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    off(event, callback) {
        if (this.listeners.has(event)) {
            const callbacks = this.listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in event callback:', error);
                }
            });
        }
    }

    // UI Update Methods
    updateConnectionStatus(status) {
        const statusElement = document.querySelector('.connection-status');
        if (statusElement) {
            statusElement.className = `connection-status ${status}`;
            statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        }
    }

    updateProgress(stage, progress) {
        const progressBar = document.querySelector('.progress-bar');
        const progressText = document.querySelector('.progress-text');
        
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        
        if (progressText) {
            progressText.textContent = `${stage}: ${progress}%`;
        }
    }

    updateAnalysisResults(results) {
        const resultsContainer = document.querySelector('.results-container');
        if (resultsContainer) {
            resultsContainer.innerHTML = this.renderAnalysisResults(results);
            resultsContainer.classList.add('fade-in');
        }
    }

    renderAnalysisResults(results) {
        return `
            <div class="results-header">
                <h3>Brand Analysis Results</h3>
                <div class="results-actions">
                    <button class="secondary-button" onclick="exportResults()">
                        <span class="button-icon">📊</span>
                        Export
                    </button>
                </div>
            </div>
            <div class="results-grid">
                ${Object.entries(results).map(([key, value]) => `
                    <div class="result-card">
                        <h4>${this.formatKey(key)}</h4>
                        <div class="result-content">${this.formatValue(value)}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    updateImageWorkflow(stage, progress, concept, imageUrl, error) {
        const workflowContainer = document.querySelector('.image-generation-workflow');
        if (!workflowContainer) return;

        // Update workflow steps
        const steps = workflowContainer.querySelectorAll('.workflow-step');
        steps.forEach((step, index) => {
            if (index < stage) {
                step.classList.add('completed');
                step.classList.remove('active');
            } else if (index === stage) {
                step.classList.add('active');
                step.classList.remove('completed');
            } else {
                step.classList.remove('active', 'completed');
            }
        });

        // Update image result
        if (imageUrl) {
            const imageResult = document.querySelector('.image-result');
            if (imageResult) {
                imageResult.innerHTML = `
                    <img src="${imageUrl}" alt="Generated satirical image" 
                         style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                `;
            }
        }

        // Handle errors
        if (error) {
            this.showToast(`Image generation error: ${error}`, 'error');
        }
    }

    updateAgentStatus(agent, status, capabilities) {
        const agentList = document.querySelector('.agent-list');
        if (!agentList) return;

        let agentItem = document.querySelector(`[data-agent="${agent}"]`);
        if (!agentItem) {
            agentItem = document.createElement('div');
            agentItem.className = 'agent-item';
            agentItem.setAttribute('data-agent', agent);
            agentList.appendChild(agentItem);
        }

        agentItem.innerHTML = `
            <div class="agent-name">${agent}</div>
            <div class="agent-status">${status}</div>
            ${capabilities ? `
                <div class="capability-list">
                    ${capabilities.map(cap => `<span class="capability-tag">${cap}</span>`).join('')}
                </div>
            ` : ''}
        `;
    }

    // Activity Feed Management
    setupActivityFeed() {
        this.activityFeed = document.querySelector('.activity-feed');
        this.maxActivityItems = 50;
    }

    addActivity(message, timestamp = null) {
        if (!this.activityFeed) return;

        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item fade-in';
        
        const time = timestamp ? new Date(timestamp) : new Date();
        const timeString = time.toLocaleTimeString();
        
        activityItem.innerHTML = `
            <div>${message}</div>
            <div class="activity-timestamp">${timeString}</div>
        `;

        this.activityFeed.insertBefore(activityItem, this.activityFeed.firstChild);

        // Limit activity items
        while (this.activityFeed.children.length > this.maxActivityItems) {
            this.activityFeed.removeChild(this.activityFeed.lastChild);
        }
    }

    // Progress Tracking
    setupProgressTracking() {
        this.progressStates = new Map();
    }

    trackProgress(id, stage, progress) {
        this.progressStates.set(id, { stage, progress, timestamp: Date.now() });
        this.emit('progress', { id, stage, progress });
    }

    getProgress(id) {
        return this.progressStates.get(id);
    }

    // Toast Notifications
    showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Auto remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, duration);
    }

    // Utility Methods
    formatKey(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    formatValue(value) {
        if (typeof value === 'object') {
            return `<pre>${JSON.stringify(value, null, 2)}</pre>`;
        }
        return String(value);
    }

    // Event Listeners Setup
    setupEventListeners() {
        // Handle form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.matches('.brand-analysis-form')) {
                e.preventDefault();
                this.handleBrandAnalysis(e.target);
            } else if (e.target.matches('.image-generation-form')) {
                e.preventDefault();
                this.handleImageGeneration(e.target);
            }
        });

        // Handle real-time updates
        this.on('analysis_update', (data) => {
            console.log('Real-time analysis update:', data);
        });

        this.on('image_generation_update', (data) => {
            console.log('Real-time image generation update:', data);
        });
    }

    // Brand Analysis Handler
    async handleBrandAnalysis(form) {
        const formData = new FormData(form);
        const brandName = formData.get('brand_name');
        const analysisType = formData.get('analysis_type');

        if (!brandName) {
            this.showToast('Please enter a brand name', 'warning');
            return;
        }

        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.innerHTML = '<span class="loading-spinner"></span> Analyzing...';
        submitButton.disabled = true;

        try {
            // Send real-time request
            this.send({
                type: 'start_analysis',
                brand: brandName,
                analysis_type: analysisType,
                timestamp: Date.now()
            });

            // Also send HTTP request
            const response = await fetch('/api/analyze_brand', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    brand_name: brandName,
                    analysis_type: analysisType
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.updateAnalysisResults(result);
            this.showToast('Brand analysis completed successfully!', 'success');

        } catch (error) {
            console.error('Brand analysis error:', error);
            this.showToast('Analysis failed. Please try again.', 'error');
        } finally {
            // Restore button state
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    }

    // Image Generation Handler
    async handleImageGeneration(form) {
        const formData = new FormData(form);
        const concept = formData.get('concept');
        const style = formData.get('style');

        if (!concept) {
            this.showToast('Please select a concept', 'warning');
            return;
        }

        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.innerHTML = '<span class="loading-spinner"></span> Generating...';
        submitButton.disabled = true;

        try {
            // Send real-time request
            this.send({
                type: 'start_image_generation',
                concept: concept,
                style: style,
                timestamp: Date.now()
            });

            // Also send HTTP request
            const response = await fetch('/api/generate_image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    concept: concept,
                    style: style
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            if (result.image_url) {
                this.updateImageWorkflow(3, 100, concept, result.image_url);
                this.showToast('Image generated successfully!', 'success');
            }

        } catch (error) {
            console.error('Image generation error:', error);
            this.showToast('Image generation failed. Please try again.', 'error');
        } finally {
            // Restore button state
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    }

    // Cleanup
    destroy() {
        if (this.ws) {
            this.ws.close();
        }
        this.listeners.clear();
        this.messageQueue = [];
    }
}

// Initialize real-time platform when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.realTimePlatform = new RealTimePlatform();
    console.log('Real-time platform initialized');
});

// Export utility functions for global access
window.exportResults = function() {
    const results = document.querySelector('.results-container');
    if (results) {
        const data = results.textContent;
        const blob = new Blob([data], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'brand-analysis-results.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
};

window.downloadImage = function(url, filename = 'satirical-brand-image.png') {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
};

// Handle visibility change for connection management
document.addEventListener('visibilitychange', () => {
    if (window.realTimePlatform) {
        if (document.hidden) {
            // Page is hidden, consider reducing activity
            console.log('Page hidden, reducing WebSocket activity');
        } else {
            // Page is visible, ensure connection is active
            console.log('Page visible, ensuring WebSocket connection');
            if (window.realTimePlatform.connectionStatus !== 'connected') {
                window.realTimePlatform.connectWebSocket();
            }
        }
    }
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.realTimePlatform) {
        window.realTimePlatform.destroy();
    }
});
