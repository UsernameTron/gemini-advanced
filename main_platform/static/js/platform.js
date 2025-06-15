/**
 * Brand Deconstruction Platform - Main JavaScript
 * Handles UI interactions, API calls, and real-time updates
 */

class BrandPlatform {
    constructor() {
        this.currentAnalysis = null;
        this.generatedImages = [];
        this.campaigns = [];
        this.socket = null;
        this.platformConfig = null;
        this.currentCampaignId = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeSocket();
        this.loadAgentStatus();
        this.loadPlatformConfig();
        this.updateTimestamp();
        
        // Update timestamp every 30 seconds
        setInterval(() => this.updateTimestamp(), 30000);
    }
    
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // Brand analysis form
        const startAnalysisBtn = document.getElementById('startAnalysis');
        if (startAnalysisBtn) {
            startAnalysisBtn.addEventListener('click', () => this.startBrandAnalysis());
        }
        
        // Image generation
        const generateImageBtn = document.getElementById('generateImage');
        if (generateImageBtn) {
            generateImageBtn.addEventListener('click', () => this.generateImage());
        }
        
        // Satirical intensity slider
        const intensitySlider = document.getElementById('satiricalIntensity');
        const intensityValue = document.getElementById('intensityValue');
        if (intensitySlider && intensityValue) {
            intensitySlider.addEventListener('input', (e) => {
                intensityValue.textContent = e.target.value;
            });
        }
        
        // Campaign management
        const newCampaignBtn = document.getElementById('newCampaign');
        if (newCampaignBtn) {
            newCampaignBtn.addEventListener('click', () => this.createNewCampaign());
        }
        
        const refreshDataBtn = document.getElementById('refreshData');
        if (refreshDataBtn) {
            refreshDataBtn.addEventListener('click', () => this.refreshDashboardData());
        }
        
        // Export functionality
        const exportResultsBtn = document.getElementById('exportResults');
        if (exportResultsBtn) {
            exportResultsBtn.addEventListener('click', () => this.exportResults());
        }
    }
    
    initializeSocket() {
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('Connected to Brand Platform');
                this.updateConnectionStatus(true);
            });
            
            this.socket.on('disconnect', () => {
                console.log('Disconnected from Brand Platform');
                this.updateConnectionStatus(false);
            });
            
            this.socket.on('analysis_status', (data) => {
                this.updateAnalysisProgress(data);
            });
            
            this.socket.on('agent_status', (data) => {
                this.updateAgentStatus(data);
            });
        }
    }
    
    switchTab(tabId) {
        // Emit deactivation event for current tab
        const currentActiveTab = document.querySelector('.tab-button.active');
        if (currentActiveTab) {
            const currentTabId = currentActiveTab.dataset.tab;
            if (currentTabId !== tabId) {
                document.dispatchEvent(new CustomEvent('tabDeactivated', { detail: currentTabId }));
            }
        }
        
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabId).classList.add('active');
        
        // Emit activation event for new tab
        document.dispatchEvent(new CustomEvent('tabActivated', { detail: tabId }));
        
        // Load tab-specific data
        this.loadTabData(tabId);
    }
    
    loadTabData(tabId) {
        switch (tabId) {
            case 'agent-console':
                this.loadAgentConsoleData();
                break;
            case 'campaign-manager':
                this.loadCampaignData();
                break;
            case 'workflow-builder':
                // Workflow builder initialization is handled by its own event listener
                console.log('Workflow builder tab activated');
                break;
            case 'analytics-dashboard':
                // Analytics dashboard initialization is handled by its own event listener
                console.log('Analytics dashboard tab activated');
                break;
        }
    }
    
    async startBrandAnalysis() {
        const brandName = document.getElementById('brandName').value.trim();
        const analysisDepth = document.getElementById('analysisDepth').value;
        
        if (!brandName) {
            this.showNotification('Please enter a brand name', 'error');
            return;
        }
        
        // Get selected vectors
        const vectors = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
            .map(cb => cb.value);
        
        if (vectors.length === 0) {
            this.showNotification('Please select at least one analysis vector', 'error');
            return;
        }
        
        const analysisData = {
            brand_name: brandName,
            depth: analysisDepth,
            vectors: vectors
        };
        
        this.showLoading('Analyzing brand...', `Processing ${brandName} with ${analysisDepth} analysis`);
        
        // Emit real-time start event
        if (this.socket) {
            this.socket.emit('start_analysis', { brand_name: brandName });
        }
        
        try {
            const response = await fetch('/api/brand/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(analysisData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentAnalysis = result.data;
                this.displayAnalysisResults(result);
                this.showNotification(`Analysis complete for ${brandName}`, 'success');
                this.updateStats('brandsAnalyzed', 1);
            } else {
                this.showNotification(`Analysis failed: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.showNotification('Analysis failed due to network error', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    displayAnalysisResults(result) {
        const resultsContainer = document.getElementById('analysisResults');
        const data = result.data;
        
        // Display intelligence data
        const intelligenceData = document.getElementById('intelligenceData');
        if (intelligenceData && data.positioning_analysis) {
            intelligenceData.innerHTML = this.formatResultData(data.positioning_analysis);
        }
        
        // Display vulnerability data
        const vulnerabilityData = document.getElementById('vulnerabilityData');
        if (vulnerabilityData && data.satirical_vulnerabilities) {
            vulnerabilityData.innerHTML = this.formatResultData(data.satirical_vulnerabilities);
        }
        
        // Display satirical concepts
        const satiricalConcepts = document.getElementById('satiricalConcepts');
        if (satiricalConcepts && data.satirical_vulnerabilities) {
            const concepts = data.satirical_vulnerabilities.map((vuln, index) => 
                `<div class="concept-item">
                    <strong>Concept ${index + 1}:</strong> ${vuln.vulnerability || vuln.ai_generated_vulnerabilities || 'Satirical opportunity identified'}
                </div>`
            ).join('');
            satiricalConcepts.innerHTML = concepts;
        }
        
        // Display campaign strategy
        const campaignStrategy = document.getElementById('campaignStrategy');
        if (campaignStrategy && data.recommendations) {
            const strategies = data.recommendations.map(rec => 
                `<div class="strategy-item">• ${rec}</div>`
            ).join('');
            campaignStrategy.innerHTML = strategies;
        }
        
        // Show results container
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
        
        // Enable image generation
        this.enableImageGeneration();
    }
    
    enableImageGeneration() {
        // Populate concepts in image generation tab
        if (this.currentAnalysis && this.currentAnalysis.satirical_vulnerabilities) {
            const conceptPreviews = document.getElementById('conceptPreviews');
            const concepts = this.currentAnalysis.satirical_vulnerabilities.map((vuln, index) => {
                return `
                    <div class="concept-card" data-concept-id="${index}">
                        <h4>Concept ${index + 1}</h4>
                        <p>${vuln.vulnerability || vuln.ai_generated_vulnerabilities || 'Satirical concept available'}</p>
                        <button class="secondary-button select-concept" data-concept="${index}">
                            Select for Generation
                        </button>
                    </div>
                `;
            }).join('');
            
            conceptPreviews.innerHTML = concepts;
            
            // Add click handlers for concept selection
            document.querySelectorAll('.select-concept').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const conceptIndex = e.target.dataset.concept;
                    this.selectConcept(conceptIndex);
                });
            });
        }
        
        // Update generate images button
        const generateImagesBtn = document.getElementById('generateImages');
        if (generateImagesBtn) {
            generateImagesBtn.disabled = false;
            generateImagesBtn.onclick = () => this.switchTab('image-generation');
        }
    }
    
    selectConcept(conceptIndex) {
        const concept = this.currentAnalysis.satirical_vulnerabilities[conceptIndex];
        const prompt = concept.vulnerability || concept.ai_generated_vulnerabilities || 'Generate satirical image';
        
        // Fill image generation form
        document.getElementById('imagePrompt').value = `Satirical corporate image: ${prompt}`;
        document.getElementById('brandContext').value = this.currentAnalysis.brand_name;
        
        // Switch to image step
        document.getElementById('conceptStep').classList.remove('active');
        document.getElementById('imageStep').classList.add('active');
        
        this.showNotification('Concept selected for image generation', 'success');
    }
    
    async generateImage() {
        const prompt = document.getElementById('imagePrompt').value.trim();
        const brandContext = document.getElementById('brandContext').value.trim();
        const satiricalIntensity = parseFloat(document.getElementById('satiricalIntensity').value);
        
        if (!prompt) {
            this.showNotification('Please enter an image prompt', 'error');
            return;
        }
        
        if (!brandContext) {
            this.showNotification('Please enter brand context', 'error');
            return;
        }
        
        const imageData = {
            enhanced_prompt: prompt,
            brand_context: {
                brand_name: brandContext,
                industry: 'Technology'
            },
            satirical_intensity: satiricalIntensity
        };
        
        this.showLoading('Generating image...', 'Creating high-quality satirical image with AI');
        
        try {
            const response = await fetch('/api/image/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(imageData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayGeneratedImage(result);
                this.generatedImages.push(result.data);
                this.showNotification('Image generated successfully!', 'success');
                this.updateStats('imagesGenerated', 1);
            } else {
                this.showNotification(`Image generation failed: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('Image generation error:', error);
            this.showNotification('Image generation failed due to network error', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    displayGeneratedImage(result) {
        const imageResult = document.getElementById('generatedImage');
        const data = result.data;
        
        let imageHtml = `
            <div class="generated-image-container">
                <h4>Generated Image</h4>
                <div class="image-metadata">
                    <span>Processing Time: ${result.processing_time?.toFixed(2)}s</span>
                    <span>Resolution: ${result.resolution || '1536x1024'}</span>
                    <span>Cost: $${result.cost || '0.08'}</span>
                </div>
        `;
        
        if (data.image_url) {
            imageHtml += `
                <div class="image-display">
                    <img src="${data.image_url}" alt="Generated satirical image" />
                    <div class="image-actions">
                        <button class="secondary-button" onclick="window.open('${data.image_url}', '_blank')">
                            View Full Size
                        </button>
                        <button class="primary-button" onclick="platform.downloadImage('${data.image_url}')">
                            Download Image
                        </button>
                    </div>
                </div>
            `;
        }
        
        imageHtml += '</div>';
        
        imageResult.innerHTML = imageHtml;
        imageResult.style.display = 'block';
        imageResult.scrollIntoView({ behavior: 'smooth' });
    }
    
    async loadAgentStatus() {
        try {
            const response = await fetch('/api/agents/available');
            const result = await response.json();
            
            if (result.success) {
                this.updateAgentStatus(result);
            }
        } catch (error) {
            console.error('Failed to load agent status:', error);
        }
    }
    
    async loadAgentConsoleData() {
        const activeAgents = document.getElementById('activeAgents');
        const agentCapabilities = document.getElementById('agentCapabilities');
        
        try {
            const response = await fetch('/api/agents/available');
            const result = await response.json();
            
            if (result.success) {
                // Display active agents
                const agentList = Object.keys(result.agents.available || {}).map(agentType => 
                    `<div class="agent-item">
                        <span class="agent-name">${agentType}</span>
                        <span class="agent-status active">Active</span>
                    </div>`
                ).join('');
                
                activeAgents.innerHTML = agentList || '<div class="no-data">No agents available</div>';
                
                // Display capabilities
                const capabilityList = (result.capabilities || []).map(cap => 
                    `<div class="capability-item">${cap}</div>`
                ).join('');
                
                agentCapabilities.innerHTML = capabilityList || '<div class="no-data">No capabilities loaded</div>';
            }
        } catch (error) {
            console.error('Failed to load agent console data:', error);
            activeAgents.innerHTML = '<div class="error">Failed to load agent data</div>';
            agentCapabilities.innerHTML = '<div class="error">Failed to load capabilities</div>';
        }
    }
    
    loadCampaignData() {
        // Mock campaign data for now
        const campaignList = document.getElementById('campaignList');
        campaignList.innerHTML = `
            <div class="campaign-placeholder">
                <p>Campaign management feature coming soon!</p>
                <p>This will allow you to save, organize, and manage multiple brand analysis campaigns.</p>
            </div>
        `;
    }
    
    updateAgentStatus(data) {
        const statusIndicator = document.getElementById('agentStatus');
        const statusDot = statusIndicator?.querySelector('.status-dot');
        const statusText = statusIndicator?.querySelector('.status-text');
        const agentCount = document.getElementById('agentCount');
        
        if (data.agents_available && data.agents_available > 0) {
            statusDot?.classList.add('active');
            statusText.textContent = `${data.agents_available} Agents Ready`;
            agentCount.textContent = `${data.agents_available} Available`;
        } else {
            statusDot?.classList.remove('active');
            statusText.textContent = 'Agents Unavailable';
            agentCount.textContent = 'Unavailable';
        }
    }
    
    updateAnalysisProgress(data) {
        if (data.status === 'progress') {
            this.updateLoadingProgress(data.step, data.progress);
        }
    }
    
    updateConnectionStatus(connected) {
        const activeConnections = document.getElementById('activeConnections');
        if (activeConnections) {
            activeConnections.textContent = connected ? '1' : '0';
        }
    }
    
    updateStats(statName, increment = 1) {
        const statElement = document.getElementById(statName);
        if (statElement) {
            const currentValue = parseInt(statElement.textContent) || 0;
            statElement.textContent = currentValue + increment;
        }
    }
    
    updateTimestamp() {
        const lastUpdate = document.getElementById('lastUpdate');
        if (lastUpdate) {
            lastUpdate.textContent = new Date().toISOString();
        }
    }
    
    showLoading(title, details) {
        const overlay = document.getElementById('loadingOverlay');
        const message = document.getElementById('loadingMessage');
        const detailsEl = document.getElementById('loadingDetails');
        
        if (overlay) {
            message.textContent = title;
            detailsEl.textContent = details;
            overlay.style.display = 'flex';
        }
    }
    
    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    updateLoadingProgress(step, progress) {
        const detailsEl = document.getElementById('loadingDetails');
        if (detailsEl) {
            detailsEl.textContent = `${step} (${progress}%)`;
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        `;
        
        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#16a085' : type === 'error' ? '#e74c3c' : '#007acc'};
            color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 1001;
            display: flex;
            align-items: center;
            gap: 1rem;
            max-width: 400px;
            animation: slideIn 0.3s ease;
        `;
        
        // Add close handler
        notification.querySelector('.notification-close').onclick = () => {
            notification.remove();
        };
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    formatResultData(data) {
        if (typeof data === 'object') {
            return '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
        return String(data);
    }
    
    async exportResults() {
        if (!this.currentAnalysis) {
            this.showNotification('No analysis results to export', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/campaign/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    campaign_data: {
                        analysis: this.currentAnalysis,
                        images: this.generatedImages,
                        timestamp: new Date().toISOString()
                    },
                    format: 'json'
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Create download link
                const blob = new Blob([JSON.stringify(result.data, null, 2)], {
                    type: 'application/json'
                });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `brand_analysis_${this.currentAnalysis.brand_name}_${new Date().getTime()}.json`;
                a.click();
                URL.revokeObjectURL(url);
                
                this.showNotification('Results exported successfully', 'success');
            } else {
                this.showNotification(`Export failed: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showNotification('Export failed due to network error', 'error');
        }
    }
    
    downloadImage(imageUrl) {
        const a = document.createElement('a');
        a.href = imageUrl;
        a.download = `brand_image_${new Date().getTime()}.png`;
        a.target = '_blank';
        a.click();
        
        this.showNotification('Image download started', 'success');
    }
    
    createNewCampaign() {
        this.showNotification('Campaign creation feature coming soon!', 'info');
    }
    
    refreshDashboardData() {
        this.loadAgentStatus();
        this.updateTimestamp();
        
        // Request agent status via socket
        if (this.socket) {
            this.socket.emit('request_agent_status');
        }
        
        this.showNotification('Dashboard data refreshed', 'success');
    }
    
    // Enhanced API methods using new configuration system
    async loadPlatformConfig() {
        try {
            const response = await fetch('/api/enhanced/config');
            const result = await response.json();
            
            if (result.success) {
                this.platformConfig = result.config;
                console.log('✅ Platform configuration loaded:', result.environment);
                this.updateConfigDisplay(result.config);
            }
        } catch (error) {
            console.error('Failed to load platform configuration:', error);
        }
    }
    
    updateConfigDisplay(config) {
        // Update UI elements with configuration info
        const configElements = document.querySelectorAll('[data-config]');
        configElements.forEach(element => {
            const configPath = element.dataset.config;
            const value = this.getNestedValue(config, configPath);
            if (value !== undefined) {
                element.textContent = value;
            }
        });
    }
    
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => current?.[key], obj);
    }
    
    async generateEnhancedConceptPreviews(satiricalConcepts, brandCategory = 'general') {
        try {
            const response = await fetch('/api/enhanced/image/concepts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    satirical_concepts: satiricalConcepts,
                    brand_category: brandCategory
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayEnhancedConceptPreviews(result.concept_previews);
                this.showNotification(
                    `Generated ${result.total_concepts} concept previews (Est. cost: $${result.estimated_total_cost.toFixed(2)})`,
                    'success'
                );
            } else {
                this.showNotification(`Failed to generate concepts: ${result.message}`, 'error');
            }
            
            return result;
        } catch (error) {
            console.error('Enhanced concept generation error:', error);
            this.showNotification('Concept generation failed due to network error', 'error');
            throw error;
        }
    }
    
    displayEnhancedConceptPreviews(conceptPreviews) {
        const previewContainer = document.getElementById('enhancedConceptPreviews');
        if (!previewContainer) return;
        
        const previewsHtml = conceptPreviews.map((preview, index) => {
            const optimizationBadge = preview.optimization_applied 
                ? '<span class="optimization-badge success">✓ Optimized</span>'
                : '<span class="optimization-badge warning">⚠ Basic</span>';
                
            return `
                <div class="enhanced-concept-card" data-concept-id="${preview.concept_id}">
                    <div class="concept-header">
                        <h4>Enhanced Concept ${index + 1}</h4>
                        ${optimizationBadge}
                    </div>
                    <div class="concept-details">
                        <p><strong>Category:</strong> ${preview.brand_category}</p>
                        <p><strong>Est. Cost:</strong> $${preview.estimated_cost.toFixed(3)}</p>
                        <p><strong>Est. Time:</strong> ${preview.estimated_time}s</p>
                    </div>
                    <div class="optimized-prompt">
                        <strong>Optimized Prompt:</strong>
                        <div class="prompt-preview">${preview.optimized_prompt.substring(0, 200)}...</div>
                    </div>
                    <div class="concept-actions">
                        <button class="primary-button generate-enhanced-image" 
                                data-concept="${JSON.stringify(preview).replace(/"/g, '&quot;')}">
                            Generate Enhanced Image
                        </button>
                        <button class="secondary-button view-full-prompt" 
                                data-prompt="${preview.optimized_prompt.replace(/"/g, '&quot;')}">
                            View Full Prompt
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
        previewContainer.innerHTML = previewsHtml;
        
        // Add event listeners for enhanced concept actions
        document.querySelectorAll('.generate-enhanced-image').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const conceptData = JSON.parse(e.target.dataset.concept.replace(/&quot;/g, '"'));
                this.generateEnhancedImage(conceptData);
            });
        });
        
        document.querySelectorAll('.view-full-prompt').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const prompt = e.target.dataset.prompt.replace(/&quot;/g, '"');
                this.showPromptModal(prompt);
            });
        });
    }
    
    async generateEnhancedImage(conceptData) {
        try {
            this.showLoading('Generating Enhanced Image...', 
                `Using optimized prompt with ${conceptData.brand_category} styling`);
            
            const response = await fetch('/api/enhanced/image/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    optimized_prompt: conceptData.optimized_prompt,
                    concept_metadata: conceptData.original_concept
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayEnhancedImageResult(result);
                this.showNotification('Enhanced image generated successfully!', 'success');
                
                // Update statistics
                this.updateStats('imagesGenerated', 1);
                
                // Add to current campaign if active
                if (this.currentCampaignId) {
                    await this.addImageToCampaign(this.currentCampaignId, result);
                }
            } else {
                this.showNotification(`Enhanced image generation failed: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('Enhanced image generation error:', error);
            this.showNotification('Enhanced image generation failed due to network error', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    displayEnhancedImageResult(result) {
        const resultContainer = document.getElementById('enhancedImageResult');
        if (!resultContainer) return;
        
        const metadata = result.generation_metadata || {};
        const validation = metadata.quality_validation || {};
        
        const resultHtml = `
            <div class="enhanced-image-result">
                <div class="result-header">
                    <h4>Enhanced Image Generated</h4>
                    <div class="quality-indicators">
                        <span class="quality-score">Quality: ${validation.quality_score?.toFixed(1) || 'N/A'}/100</span>
                        <span class="generation-time">Time: ${metadata.generation_time?.toFixed(2) || 'N/A'}s</span>
                        <span class="cost">Cost: $${metadata.cost?.toFixed(3) || 'N/A'}</span>
                    </div>
                </div>
                
                <div class="image-display">
                    <img src="${result.image_url}" alt="Enhanced generated image" class="generated-image" />
                </div>
                
                <div class="image-metadata">
                    <div class="metadata-section">
                        <h5>Image Specifications</h5>
                        <ul>
                            <li>Model: ${result.image_specs?.model || 'N/A'}</li>
                            <li>Size: ${result.image_specs?.size || 'N/A'}</li>
                            <li>Quality: ${result.image_specs?.quality || 'N/A'}</li>
                            <li>Style: ${result.image_specs?.style || 'N/A'}</li>
                        </ul>
                    </div>
                    
                    ${validation.validation_passed ? `
                    <div class="metadata-section">
                        <h5>Quality Validation</h5>
                        <ul>
                            <li>Resolution: ${validation.resolution?.[0]}x${validation.resolution?.[1]}</li>
                            <li>File Size: ${validation.file_size_kb?.toFixed(1) || 'N/A'} KB</li>
                            <li>Color Mode: ${validation.mode || 'N/A'}</li>
                            <li>Aspect Ratio: ${validation.aspect_ratio?.toFixed(2) || 'N/A'}</li>
                        </ul>
                    </div>
                    ` : ''}
                </div>
                
                <div class="image-actions">
                    <button class="primary-button" onclick="platform.downloadEnhancedImage('${result.image_url}')">
                        Download Image
                    </button>
                    <button class="secondary-button" onclick="platform.shareImageResult('${result.image_url}')">
                        Share Result
                    </button>
                    <button class="secondary-button" onclick="platform.viewImageMetadata(${JSON.stringify(result).replace(/"/g, '&quot;')})">
                        View Metadata
                    </button>
                </div>
            </div>
        `;
        
        resultContainer.innerHTML = resultHtml;
        resultContainer.style.display = 'block';
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }
    
    async createEnhancedCampaign(brandName, analysisData, metadata = {}) {
        try {
            const response = await fetch('/api/enhanced/campaigns', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    brand_name: brandName,
                    analysis_data: analysisData,
                    metadata: {
                        ...metadata,
                        created_via: 'enhanced_ui',
                        platform_version: '1.0',
                        timestamp: new Date().toISOString()
                    }
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentCampaignId = result.campaign_id;
                this.showNotification(`Campaign created: ${result.campaign_id}`, 'success');
                return result.campaign_id;
            } else {
                this.showNotification(`Campaign creation failed: ${result.message}`, 'error');
                return null;
            }
        } catch (error) {
            console.error('Enhanced campaign creation error:', error);
            this.showNotification('Campaign creation failed due to network error', 'error');
            return null;
        }
    }
    
    async loadPlatformAnalytics() {
        try {
            const response = await fetch('/api/enhanced/analytics');
            const result = await response.json();
            
            if (result.success) {
                this.updateAnalyticsDisplay(result.analytics);
                return result.analytics;
            } else {
                console.error('Failed to load analytics:', result.message);
                return null;
            }
        } catch (error) {
            console.error('Analytics loading error:', error);
            return null;
        }
    }
    
    updateAnalyticsDisplay(analytics) {
        // Update dashboard analytics display
        const analyticsElements = {
            'totalCampaigns': analytics.total_campaigns,
            'totalImages': analytics.total_images_generated,
            'uniqueBrands': analytics.unique_brands_analyzed,
            'totalCost': `$${analytics.total_generation_cost?.toFixed(2) || '0.00'}`,
            'avgCostPerCampaign': `$${analytics.average_cost_per_campaign?.toFixed(2) || '0.00'}`
        };
        
        Object.entries(analyticsElements).forEach(([elementId, value]) => {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = value;
            }
        });
        
        // Update image generation stats if available
        if (analytics.image_generation) {
            const imageStats = analytics.image_generation;
            const imageStatsElements = {
                'generationSuccessRate': `${imageStats.success_rate?.toFixed(1) || '0'}%`,
                'avgGenerationTime': `${imageStats.average_generation_time?.toFixed(1) || '0'}s`
            };
            
            Object.entries(imageStatsElements).forEach(([elementId, value]) => {
                const element = document.getElementById(elementId);
                if (element) {
                    element.textContent = value;
                }
            });
        }
    }
    
    downloadEnhancedImage(imageUrl) {
        const a = document.createElement('a');
        a.href = imageUrl;
        a.download = `enhanced_brand_image_${new Date().getTime()}.png`;
        a.target = '_blank';
        a.click();
        
        this.showNotification('Enhanced image download started', 'success');
    }
    
    showPromptModal(prompt) {
        // Create modal for viewing full prompt
        const modal = document.createElement('div');
        modal.className = 'prompt-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Optimized Prompt</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <pre class="prompt-text">${prompt}</pre>
                </div>
                <div class="modal-footer">
                    <button class="secondary-button copy-prompt">Copy Prompt</button>
                    <button class="primary-button modal-close">Close</button>
                </div>
            </div>
        `;
        
        // Add modal styles
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        `;
        
        // Add close handlers
        modal.querySelectorAll('.modal-close').forEach(btn => {
            btn.onclick = () => modal.remove();
        });
        
        // Add copy handler
        modal.querySelector('.copy-prompt').onclick = () => {
            navigator.clipboard.writeText(prompt);
            this.showNotification('Prompt copied to clipboard', 'success');
        };
        
        document.body.appendChild(modal);
    }

    // ...existing methods...
}

// CSS for notifications
const notificationCSS = `
@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.notification-close {
    background: none;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}
`;

// Add notification CSS to page
const style = document.createElement('style');
style.textContent = notificationCSS;
document.head.appendChild(style);

// Initialize platform when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.platform = new BrandPlatform();
    console.log('Brand Deconstruction Platform initialized');
});
