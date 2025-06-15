/**
 * Enhanced Platform Integration
 * Connects Workflow Builder, Analytics Dashboard, and Real-time Platform
 */

class PlatformIntegration {
    constructor() {
        this.workflowBuilder = null;
        this.analyticsDashboard = null;
        this.platform = null;
        this.activeTab = 'brand-analysis';
        
        this.init();
    }
    
    init() {
        this.setupTabSwitching();
        this.setupPlatformIntegration();
        this.setupWorkflowAPI();
        this.setupAnalyticsAPI();
        this.initializeComponents();
    }
    
    setupTabSwitching() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const targetTab = button.dataset.tab;
                this.switchToTab(targetTab);
            });
        });
    }
    
    switchToTab(tabName) {
        // Update active tab
        this.activeTab = tabName;
        
        // Update button states
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update content visibility
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });
        
        const targetContent = document.getElementById(tabName);
        if (targetContent) {
            targetContent.style.display = 'block';
        }
        
        // Initialize tab-specific functionality
        this.initializeTabContent(tabName);
    }
    
    initializeTabContent(tabName) {
        switch (tabName) {
            case 'workflow-builder':
                this.initializeWorkflowBuilder();
                break;
            case 'analytics-dashboard':
                this.initializeAnalyticsDashboard();
                break;
            case 'campaign-manager':
                this.initializeCampaignManager();
                break;
            default:
                // Other tabs already handled by existing platform.js
                break;
        }
    }
    
    initializeWorkflowBuilder() {
        if (!this.workflowBuilder && window.WorkflowBuilder) {
            this.workflowBuilder = new WorkflowBuilder();
            this.setupWorkflowIntegration();
        }
    }
    
    initializeAnalyticsDashboard() {
        if (!this.analyticsDashboard && window.AnalyticsDashboard) {
            this.analyticsDashboard = new AnalyticsDashboard();
            this.setupAnalyticsIntegration();
            this.loadAnalyticsData();
        }
    }
    
    initializeCampaignManager() {
        this.loadCampaignData();
        this.setupCampaignEvents();
    }
    
    setupWorkflowIntegration() {
        // Connect workflow builder with platform
        if (this.workflowBuilder && window.platform) {
            // Add custom node execution handler
            this.workflowBuilder.onNodeExecute = (nodeType, nodeData) => {
                return this.executeWorkflowNode(nodeType, nodeData);
            };
            
            // Add workflow completion handler
            this.workflowBuilder.onWorkflowComplete = (result) => {
                this.handleWorkflowComplete(result);
            };
        }
    }
    
    setupAnalyticsIntegration() {
        // Connect analytics dashboard with platform data
        if (this.analyticsDashboard && window.platform) {
            // Set up real-time data updates
            this.analyticsDashboard.setDataSource(() => {
                return this.getAnalyticsData();
            });
            
            // Set up auto-refresh
            setInterval(() => {
                this.updateAnalyticsData();
            }, 30000); // Update every 30 seconds
        }
    }
    
    setupPlatformIntegration() {
        // Wait for platform to be available
        const waitForPlatform = () => {
            if (window.platform) {
                this.platform = window.platform;
                this.enhancePlatformFunctionality();
            } else {
                setTimeout(waitForPlatform, 100);
            }
        };
        waitForPlatform();
    }
    
    enhancePlatformFunctionality() {
        // Add enhanced image generation with workflow integration
        const originalGenerateImage = this.platform.generateSatiricalImage;
        this.platform.generateSatiricalImage = async (data) => {
            // Check if there's an active workflow for image generation
            if (this.workflowBuilder && this.hasImageWorkflow()) {
                return await this.executeImageWorkflow(data);
            } else {
                return await originalGenerateImage.call(this.platform, data);
            }
        };
        
        // Add analytics tracking to all platform operations
        this.addAnalyticsTracking();
    }
    
    addAnalyticsTracking() {
        // Track brand analysis
        const originalAnalyzeBrand = this.platform.analyzeBrand;
        this.platform.analyzeBrand = async (data) => {
            const startTime = Date.now();
            try {
                const result = await originalAnalyzeBrand.call(this.platform, data);
                this.trackAnalytics('brand_analysis', {
                    duration: Date.now() - startTime,
                    success: true,
                    brand: data.brand_name
                });
                return result;
            } catch (error) {
                this.trackAnalytics('brand_analysis', {
                    duration: Date.now() - startTime,
                    success: false,
                    error: error.message
                });
                throw error;
            }
        };
        
        // Track image generation
        const originalGenerateImage = this.platform.generateSatiricalImage;
        this.platform.generateSatiricalImage = async (data) => {
            const startTime = Date.now();
            try {
                const result = await originalGenerateImage.call(this.platform, data);
                this.trackAnalytics('image_generation', {
                    duration: Date.now() - startTime,
                    success: true,
                    concept: data.concept
                });
                return result;
            } catch (error) {
                this.trackAnalytics('image_generation', {
                    duration: Date.now() - startTime,
                    success: false,
                    error: error.message
                });
                throw error;
            }
        };
    }
    
    async executeWorkflowNode(nodeType, nodeData) {
        const startTime = Date.now();
        
        try {
            let result;
            
            switch (nodeType) {
                case 'brand-agent':
                    result = await this.platform.analyzeBrand({
                        brand_name: nodeData.properties.brand_name,
                        analysis_depth: nodeData.properties.analysis_depth,
                        include_vulnerabilities: nodeData.properties.include_vulnerabilities
                    });
                    break;
                    
                case 'image-agent':
                    result = await this.platform.generateSatiricalImage({
                        concept: nodeData.inputs.concepts,
                        style: nodeData.inputs.style,
                        image_count: nodeData.properties.image_count,
                        satirical_intensity: nodeData.properties.satirical_intensity
                    });
                    break;
                    
                case 'analytics-agent':
                    result = await this.generateAnalyticsReport(nodeData);
                    break;
                    
                default:
                    result = await this.executeCustomNode(nodeType, nodeData);
                    break;
            }
            
            this.trackAnalytics('workflow_node_execution', {
                nodeType,
                duration: Date.now() - startTime,
                success: true
            });
            
            return result;
            
        } catch (error) {
            this.trackAnalytics('workflow_node_execution', {
                nodeType,
                duration: Date.now() - startTime,
                success: false,
                error: error.message
            });
            throw error;
        }
    }
    
    async generateAnalyticsReport(nodeData) {
        const response = await fetch('/api/enhanced/analytics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: nodeData.inputs.data,
                query: nodeData.inputs.query,
                metric_types: nodeData.properties.metric_types,
                report_type: nodeData.properties.report_type
            })
        });
        
        if (!response.ok) {
            throw new Error('Analytics generation failed');
        }
        
        return await response.json();
    }
    
    async executeCustomNode(nodeType, nodeData) {
        // Handle custom node types
        switch (nodeType) {
            case 'decision':
                return this.executeDecisionNode(nodeData);
            case 'loop':
                return this.executeLoopNode(nodeData);
            case 'parallel':
                return this.executeParallelNode(nodeData);
            case 'transform':
                return this.executeTransformNode(nodeData);
            default:
                throw new Error(`Unknown node type: ${nodeType}`);
        }
    }
    
    executeDecisionNode(nodeData) {
        const condition = nodeData.inputs.condition;
        const operator = nodeData.properties.operator;
        const value = nodeData.properties.value;
        const caseSensitive = nodeData.properties.caseSensitive;
        
        let result = false;
        
        switch (operator) {
            case 'equals':
                result = caseSensitive ? 
                    condition === value : 
                    condition.toLowerCase() === value.toLowerCase();
                break;
            case 'contains':
                result = caseSensitive ? 
                    condition.includes(value) : 
                    condition.toLowerCase().includes(value.toLowerCase());
                break;
            case 'greater_than':
                result = parseFloat(condition) > parseFloat(value);
                break;
            case 'less_than':
                result = parseFloat(condition) < parseFloat(value);
                break;
        }
        
        return { result, output: result ? 'true' : 'false' };
    }
    
    async executeLoopNode(nodeData) {
        const input = nodeData.inputs.input;
        const maxIterations = nodeData.properties.maxIterations;
        const breakCondition = nodeData.properties.breakCondition;
        
        const results = [];
        let iteration = 0;
        
        while (iteration < maxIterations) {
            // Execute loop content (would need to be defined in workflow)
            const iterationResult = await this.processLoopIteration(input, iteration);
            results.push(iterationResult);
            
            // Check break condition
            if (this.shouldBreakLoop(iterationResult, breakCondition)) {
                break;
            }
            
            iteration++;
        }
        
        return { results, iterations: iteration + 1 };
    }
    
    async executeParallelNode(nodeData) {
        const input = nodeData.inputs.input;
        const waitForAll = nodeData.properties.waitForAll;
        const timeout = nodeData.properties.timeout * 1000; // Convert to ms
        
        // Create parallel execution tasks
        const tasks = [
            this.processParallelTask(input, 'task1'),
            this.processParallelTask(input, 'task2'),
            this.processParallelTask(input, 'task3')
        ];
        
        if (waitForAll) {
            const results = await Promise.allSettled(tasks);
            return {
                output1: results[0].status === 'fulfilled' ? results[0].value : null,
                output2: results[1].status === 'fulfilled' ? results[1].value : null,
                output3: results[2].status === 'fulfilled' ? results[2].value : null
            };
        } else {
            const firstResult = await Promise.race(tasks);
            return { output: firstResult };
        }
    }
    
    executeTransformNode(nodeData) {
        const input = nodeData.inputs.input;
        const operation = nodeData.properties.operation;
        const expression = nodeData.properties.expression;
        
        try {
            let result;
            
            switch (operation) {
                case 'map':
                    const mapFn = new Function('x', `return ${expression}`);
                    result = Array.isArray(input) ? input.map(mapFn) : mapFn(input);
                    break;
                    
                case 'filter':
                    const filterFn = new Function('x', `return ${expression}`);
                    result = Array.isArray(input) ? input.filter(filterFn) : (filterFn(input) ? input : null);
                    break;
                    
                case 'reduce':
                    const reduceFn = new Function('acc', 'x', `return ${expression}`);
                    result = Array.isArray(input) ? input.reduce(reduceFn, null) : input;
                    break;
                    
                default:
                    result = input;
                    break;
            }
            
            return { output: result };
            
        } catch (error) {
            throw new Error(`Transform operation failed: ${error.message}`);
        }
    }
    
    handleWorkflowComplete(result) {
        // Update analytics with workflow completion
        this.trackAnalytics('workflow_completion', {
            success: true,
            result_size: JSON.stringify(result).length,
            timestamp: Date.now()
        });
        
        // Update campaign if this is part of a campaign
        if (this.platform.currentCampaignId) {
            this.updateCampaignWithWorkflowResult(result);
        }
        
        // Show success notification
        this.showNotification('Workflow completed successfully!', 'success');
    }
    
    async updateCampaignWithWorkflowResult(result) {
        try {
            const response = await fetch(`/api/enhanced/campaigns/${this.platform.currentCampaignId}/workflow-result`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    workflow_result: result,
                    timestamp: Date.now()
                })
            });
            
            if (response.ok) {
                this.showNotification('Campaign updated with workflow results', 'success');
            }
        } catch (error) {
            console.error('Failed to update campaign:', error);
        }
    }
    
    trackAnalytics(event, data) {
        // Store analytics data for dashboard
        const analyticsEvent = {
            event,
            data,
            timestamp: Date.now(),
            session_id: this.getSessionId()
        };
        
        // Send to analytics service
        fetch('/api/enhanced/analytics/track', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(analyticsEvent)
        }).catch(error => {
            console.error('Analytics tracking failed:', error);
        });
        
        // Update real-time dashboard if visible
        if (this.activeTab === 'analytics-dashboard' && this.analyticsDashboard) {
            this.analyticsDashboard.addEvent(analyticsEvent);
        }
    }
    
    async getAnalyticsData() {
        try {
            const response = await fetch('/api/enhanced/analytics');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Failed to fetch analytics data:', error);
        }
        return null;
    }
    
    async updateAnalyticsData() {
        if (this.activeTab === 'analytics-dashboard' && this.analyticsDashboard) {
            const data = await this.getAnalyticsData();
            if (data) {
                this.analyticsDashboard.updateData(data);
            }
        }
    }
    
    hasImageWorkflow() {
        return this.workflowBuilder && 
               this.workflowBuilder.nodes && 
               Array.from(this.workflowBuilder.nodes.values()).some(node => 
                   node.type === 'image-agent'
               );
    }
    
    async executeImageWorkflow(data) {
        if (!this.workflowBuilder) return null;
        
        // Set input data in workflow
        const inputNodes = Array.from(this.workflowBuilder.nodes.values())
            .filter(node => node.type === 'input');
        
        if (inputNodes.length > 0) {
            inputNodes[0].properties.defaultValue = data.concept;
        }
        
        // Execute workflow
        return await this.workflowBuilder.runWorkflow();
    }
    
    async loadCampaignData() {
        try {
            const response = await fetch('/api/enhanced/campaigns');
            if (response.ok) {
                const campaigns = await response.json();
                this.updateCampaignUI(campaigns);
            }
        } catch (error) {
            console.error('Failed to load campaigns:', error);
        }
    }
    
    updateCampaignUI(campaigns) {
        const campaignList = document.querySelector('.campaign-list');
        if (!campaignList) return;
        
        campaignList.innerHTML = '';
        
        campaigns.forEach(campaign => {
            const campaignElement = this.createCampaignElement(campaign);
            campaignList.appendChild(campaignElement);
        });
    }
    
    createCampaignElement(campaign) {
        const element = document.createElement('div');
        element.className = 'campaign-item';
        element.innerHTML = `
            <div class="campaign-header">
                <h4>${campaign.name}</h4>
                <span class="campaign-status ${campaign.status}">${campaign.status}</span>
            </div>
            <div class="campaign-details">
                <p>Created: ${new Date(campaign.created_at).toLocaleDateString()}</p>
                <p>Images: ${campaign.images_count || 0}</p>
                <p>Analytics: ${campaign.analytics_count || 0}</p>
            </div>
            <div class="campaign-actions">
                <button onclick="platformIntegration.viewCampaign('${campaign.id}')" class="btn secondary-button">
                    View Details
                </button>
                <button onclick="platformIntegration.exportCampaign('${campaign.id}')" class="btn secondary-button">
                    Export
                </button>
            </div>
        `;
        return element;
    }
    
    async viewCampaign(campaignId) {
        try {
            const response = await fetch(`/api/enhanced/campaigns/${campaignId}`);
            if (response.ok) {
                const campaign = await response.json();
                this.showCampaignDetails(campaign);
            }
        } catch (error) {
            console.error('Failed to load campaign:', error);
            this.showNotification('Failed to load campaign details', 'error');
        }
    }
    
    async exportCampaign(campaignId) {
        try {
            const response = await fetch(`/api/enhanced/campaigns/${campaignId}/export`);
            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `campaign-${campaignId}.zip`;
                a.click();
                URL.revokeObjectURL(url);
                
                this.showNotification('Campaign exported successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to export campaign:', error);
            this.showNotification('Failed to export campaign', 'error');
        }
    }
    
    showCampaignDetails(campaign) {
        // Create modal with campaign details
        const modal = document.createElement('div');
        modal.className = 'campaign-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Campaign Details: ${campaign.name}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="campaign-overview">
                        <div class="campaign-stat">
                            <strong>Status:</strong> ${campaign.status}
                        </div>
                        <div class="campaign-stat">
                            <strong>Created:</strong> ${new Date(campaign.created_at).toLocaleString()}
                        </div>
                        <div class="campaign-stat">
                            <strong>Total Cost:</strong> $${campaign.total_cost || 0}
                        </div>
                    </div>
                    
                    <div class="campaign-section">
                        <h4>Generated Images</h4>
                        <div class="image-gallery" id="campaignImages">
                            Loading images...
                        </div>
                    </div>
                    
                    <div class="campaign-section">
                        <h4>Analytics Data</h4>
                        <div class="analytics-summary" id="campaignAnalytics">
                            Loading analytics...
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Setup modal events
        modal.querySelector('.modal-close').onclick = () => modal.remove();
        modal.onclick = (e) => {
            if (e.target === modal) modal.remove();
        };
        
        // Load campaign content
        this.loadCampaignImages(campaign.id);
        this.loadCampaignAnalytics(campaign.id);
    }
    
    async loadCampaignImages(campaignId) {
        // Load and display campaign images
        const container = document.getElementById('campaignImages');
        if (!container) return;
        
        try {
            const response = await fetch(`/api/enhanced/campaigns/${campaignId}/images`);
            if (response.ok) {
                const images = await response.json();
                container.innerHTML = images.map(img => `
                    <div class="campaign-image">
                        <img src="${img.url}" alt="Campaign Image" />
                        <div class="image-details">
                            <p><strong>Concept:</strong> ${img.concept}</p>
                            <p><strong>Created:</strong> ${new Date(img.created_at).toLocaleString()}</p>
                        </div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<p>No images found for this campaign.</p>';
            }
        } catch (error) {
            container.innerHTML = '<p>Failed to load images.</p>';
        }
    }
    
    async loadCampaignAnalytics(campaignId) {
        // Load and display campaign analytics
        const container = document.getElementById('campaignAnalytics');
        if (!container) return;
        
        try {
            const response = await fetch(`/api/enhanced/campaigns/${campaignId}/analytics`);
            if (response.ok) {
                const analytics = await response.json();
                container.innerHTML = `
                    <div class="analytics-grid">
                        <div class="metric">
                            <strong>Total Analyses:</strong> ${analytics.total_analyses || 0}
                        </div>
                        <div class="metric">
                            <strong>Average Quality:</strong> ${analytics.avg_quality || 'N/A'}
                        </div>
                        <div class="metric">
                            <strong>Success Rate:</strong> ${analytics.success_rate || 'N/A'}%
                        </div>
                        <div class="metric">
                            <strong>Total Cost:</strong> $${analytics.total_cost || 0}
                        </div>
                    </div>
                `;
            } else {
                container.innerHTML = '<p>No analytics data available.</p>';
            }
        } catch (error) {
            container.innerHTML = '<p>Failed to load analytics.</p>';
        }
    }
    
    setupCampaignEvents() {
        // Setup campaign creation form
        const createCampaignBtn = document.getElementById('createCampaign');
        if (createCampaignBtn) {
            createCampaignBtn.addEventListener('click', () => {
                this.showCreateCampaignModal();
            });
        }
    }
    
    showCreateCampaignModal() {
        const modal = document.createElement('div');
        modal.className = 'campaign-create-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Create New Campaign</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="createCampaignForm">
                        <div class="form-group">
                            <label for="campaignName">Campaign Name:</label>
                            <input type="text" id="campaignName" required />
                        </div>
                        <div class="form-group">
                            <label for="campaignDescription">Description:</label>
                            <textarea id="campaignDescription" rows="3"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="campaignBrand">Target Brand:</label>
                            <input type="text" id="campaignBrand" required />
                        </div>
                        <div class="form-actions">
                            <button type="submit" class="btn primary-button">Create Campaign</button>
                            <button type="button" class="btn secondary-button" onclick="this.closest('.campaign-create-modal').remove()">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Setup modal events
        modal.querySelector('.modal-close').onclick = () => modal.remove();
        modal.onclick = (e) => {
            if (e.target === modal) modal.remove();
        };
        
        // Setup form submission
        modal.querySelector('#createCampaignForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createCampaign(modal);
        });
    }
    
    async createCampaign(modal) {
        const formData = {
            name: modal.querySelector('#campaignName').value,
            description: modal.querySelector('#campaignDescription').value,
            target_brand: modal.querySelector('#campaignBrand').value
        };
        
        try {
            const response = await fetch('/api/enhanced/campaigns', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                const campaign = await response.json();
                this.showNotification('Campaign created successfully!', 'success');
                modal.remove();
                this.loadCampaignData(); // Refresh campaign list
                
                // Set as current campaign
                this.platform.currentCampaignId = campaign.id;
            } else {
                throw new Error('Failed to create campaign');
            }
        } catch (error) {
            console.error('Failed to create campaign:', error);
            this.showNotification('Failed to create campaign', 'error');
        }
    }
    
    getSessionId() {
        let sessionId = localStorage.getItem('platform_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('platform_session_id', sessionId);
        }
        return sessionId;
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    // Utility methods for workflow execution
    async processLoopIteration(input, iteration) {
        // Placeholder for loop iteration processing
        return { input, iteration, result: `processed_${iteration}` };
    }
    
    shouldBreakLoop(result, condition) {
        // Placeholder for loop break condition evaluation
        return false;
    }
    
    async processParallelTask(input, taskId) {
        // Placeholder for parallel task processing
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({ taskId, input, result: `processed_${taskId}` });
            }, Math.random() * 1000);
        });
    }
}

// Initialize platform integration when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.platformIntegration = new PlatformIntegration();
});
