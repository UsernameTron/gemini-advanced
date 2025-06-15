/**
 * Analytics Dashboard for Brand Deconstruction Platform
 * Advanced data visualization and performance monitoring
 */

class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.analyticsData = {};
        this.refreshInterval = null;
        this.currentTimeRange = '24h';
        this.currentMetricType = 'all';
        this.realTimeConnection = null;
        this.isConnected = false;
        
        // Enhanced chart configurations with real-time capabilities
        this.chartConfigs = {
            usageTrends: {
                type: 'line',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 750,
                        easing: 'easeInOutQuart'
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Platform Usage Trends',
                            color: '#ffffff',
                            font: {
                                size: 16,
                                weight: 'bold'
                            }
                        },
                        legend: {
                            labels: {
                                color: '#ffffff',
                                usePointStyle: true,
                                padding: 20
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#4f46e5',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        x: {
                            ticks: { 
                                color: '#ffffff',
                                font: {
                                    size: 12
                                }
                            },
                            grid: { 
                                color: '#333333',
                                drawBorder: false
                            }
                        },
                        y: {
                            ticks: { 
                                color: '#ffffff',
                                font: {
                                    size: 12
                                }
                            },
                            grid: { 
                                color: '#333333',
                                drawBorder: false
                            }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    }
                }
            },
            performanceMetrics: {
                type: 'bar',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 1000,
                        easing: 'easeOutBounce'
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Performance Metrics',
                            color: '#ffffff'
                        },
                        legend: {
                            labels: {
                                color: '#ffffff'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#ffffff' },
                            grid: { color: '#333333' }
                        },
                        y: {
                            ticks: { color: '#ffffff' },
                            grid: { color: '#333333' }
                        }
                    }
                }
            },
            agentActivity: {
                type: 'doughnut',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Agent Activity Distribution',
                            color: '#ffffff'
                        },
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#ffffff'
                            }
                        }
                    }
                }
            },
            errorRates: {
                type: 'line',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Error Rates Over Time',
                            color: '#ffffff'
                        },
                        legend: {
                            labels: {
                                color: '#ffffff'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#ffffff' },
                            grid: { color: '#333333' }
                        },
                        y: {
                            ticks: { color: '#ffffff' },
                            grid: { color: '#333333' },
                            beginAtZero: true
                        }
                    }
                }
            }
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.startRealTimeUpdates(); // Use real-time updates instead of basic load
        this.startAutoRefresh();
    }
    
    setupEventListeners() {
        // Time range selector
        const timeRangeSelect = document.getElementById('timeRange');
        if (timeRangeSelect) {
            timeRangeSelect.addEventListener('change', (e) => {
                this.currentTimeRange = e.target.value;
                this.loadAnalyticsData();
            });
        }
        
        // Metric type selector
        const metricTypeSelect = document.getElementById('metricType');
        if (metricTypeSelect) {
            metricTypeSelect.addEventListener('change', (e) => {
                this.currentMetricType = e.target.value;
                this.filterAnalyticsData();
            });
        }
        
        // Refresh button
        const refreshBtn = document.getElementById('refreshAnalytics');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadAnalyticsData());
        }
        
        // Export button
        const exportBtn = document.getElementById('exportAnalytics');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportAnalytics());
        }
    }
    
    initializeCharts() {
        // Usage trends chart
        const usageTrendsCanvas = document.getElementById('usageTrendsChart');
        if (usageTrendsCanvas) {
            this.charts.usageTrends = new Chart(usageTrendsCanvas, {
                type: this.chartConfigs.usageTrends.type,
                data: this.getEmptyChartData('line'),
                options: this.chartConfigs.usageTrends.options
            });
        }
        
        // Performance metrics chart
        const performanceCanvas = document.getElementById('performanceMetricsChart');
        if (performanceCanvas) {
            this.charts.performanceMetrics = new Chart(performanceCanvas, {
                type: this.chartConfigs.performanceMetrics.type,
                data: this.getEmptyChartData('bar'),
                options: this.chartConfigs.performanceMetrics.options
            });
        }
        
        // Agent activity chart
        const agentActivityCanvas = document.getElementById('agentActivityChart');
        if (agentActivityCanvas) {
            this.charts.agentActivity = new Chart(agentActivityCanvas, {
                type: this.chartConfigs.agentActivity.type,
                data: this.getEmptyChartData('doughnut'),
                options: this.chartConfigs.agentActivity.options
            });
        }
        
        // Error rates chart
        const errorRatesCanvas = document.getElementById('errorRatesChart');
        if (errorRatesCanvas) {
            this.charts.errorRates = new Chart(errorRatesCanvas, {
                type: this.chartConfigs.errorRates.type,
                data: this.getEmptyChartData('line'),
                options: this.chartConfigs.errorRates.options
            });
        }
    }
    
    getEmptyChartData(type) {
        switch (type) {
            case 'line':
                return {
                    labels: [],
                    datasets: [{
                        label: 'Loading...',
                        data: [],
                        borderColor: '#00BCD4',
                        backgroundColor: 'rgba(0, 188, 212, 0.1)',
                        tension: 0.4
                    }]
                };
            case 'bar':
                return {
                    labels: [],
                    datasets: [{
                        label: 'Loading...',
                        data: [],
                        backgroundColor: [
                            'rgba(76, 175, 80, 0.8)',
                            'rgba(33, 150, 243, 0.8)',
                            'rgba(255, 152, 0, 0.8)',
                            'rgba(156, 39, 176, 0.8)',
                            'rgba(244, 67, 54, 0.8)'
                        ],
                        borderColor: [
                            '#4CAF50',
                            '#2196F3',
                            '#FF9800',
                            '#9C27B0',
                            '#F44336'
                        ],
                        borderWidth: 1
                    }]
                };
            case 'doughnut':
                return {
                    labels: [],
                    datasets: [{
                        label: 'Activity',
                        data: [],
                        backgroundColor: [
                            'rgba(76, 175, 80, 0.8)',
                            'rgba(33, 150, 243, 0.8)',
                            'rgba(255, 152, 0, 0.8)',
                            'rgba(156, 39, 176, 0.8)',
                            'rgba(244, 67, 54, 0.8)',
                            'rgba(96, 125, 139, 0.8)'
                        ],
                        borderColor: [
                            '#4CAF50',
                            '#2196F3',
                            '#FF9800',
                            '#9C27B0',
                            '#F44336',
                            '#607D8B'
                        ],
                        borderWidth: 2
                    }]
                };
            default:
                return { labels: [], datasets: [] };
        }
    }
    
    async loadAnalyticsData() {
        try {
            // Show loading state
            this.updateLoadingState(true);
            
            // Try to load real-time data first
            await this.loadRealTimeData();
            
            this.updateLoadingState(false);
            
            console.log('Analytics data loaded successfully');
            
        } catch (error) {
            console.error('Error loading analytics data:', error);
            this.updateLoadingState(false);
            
            // Load fallback/mock data
            this.loadMockData();
        }
    }
    
    loadMockData() {
        console.log('Loading mock analytics data...');
        
        const mockData = this.generateMockData();
        this.analyticsData = mockData;
        
        this.updateKPIs(mockData.kpis);
        this.updateCharts(mockData.charts);
        this.updateActivityTimeline(mockData.activities);
        this.updateSystemHealth(mockData.systemHealth);
    }
    
    generateMockData() {
        const now = new Date();
        const timePoints = this.getTimePoints(this.currentTimeRange);
        
        return {
            kpis: {
                totalAnalyses: Math.floor(Math.random() * 1000) + 500,
                totalImages: Math.floor(Math.random() * 5000) + 2000,
                totalCampaigns: Math.floor(Math.random() * 50) + 20,
                avgResponseTime: Math.floor(Math.random() * 500) + 200,
                analysesChange: (Math.random() * 40 - 20).toFixed(1),
                imagesChange: (Math.random() * 60 - 10).toFixed(1),
                campaignsChange: (Math.random() * 30 - 5).toFixed(1),
                responseTimeChange: (Math.random() * 20 - 10).toFixed(1)
            },
            charts: {
                usageTrends: {
                    labels: timePoints,
                    datasets: [
                        {
                            label: 'Brand Analyses',
                            data: timePoints.map(() => Math.floor(Math.random() * 100) + 20),
                            borderColor: '#4CAF50',
                            backgroundColor: 'rgba(76, 175, 80, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Image Generation',
                            data: timePoints.map(() => Math.floor(Math.random() * 200) + 50),
                            borderColor: '#2196F3',
                            backgroundColor: 'rgba(33, 150, 243, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Campaign Activities',
                            data: timePoints.map(() => Math.floor(Math.random() * 50) + 10),
                            borderColor: '#FF9800',
                            backgroundColor: 'rgba(255, 152, 0, 0.1)',
                            tension: 0.4
                        }
                    ]
                },
                performanceMetrics: {
                    labels: ['Response Time', 'Throughput', 'Success Rate', 'Agent Efficiency', 'Resource Usage'],
                    datasets: [{
                        label: 'Performance Score',
                        data: [85, 92, 98, 88, 76],
                        backgroundColor: [
                            'rgba(76, 175, 80, 0.8)',
                            'rgba(33, 150, 243, 0.8)',
                            'rgba(255, 152, 0, 0.8)',
                            'rgba(156, 39, 176, 0.8)',
                            'rgba(244, 67, 54, 0.8)'
                        ],
                        borderColor: [
                            '#4CAF50',
                            '#2196F3',
                            '#FF9800',
                            '#9C27B0',
                            '#F44336'
                        ],
                        borderWidth: 1
                    }]
                },
                agentActivity: {
                    labels: ['Brand Agent', 'Image Agent', 'Analytics Agent', 'Campaign Agent', 'Monitoring Agent', 'Other'],
                    datasets: [{
                        label: 'Agent Usage',
                        data: [
                            Math.floor(Math.random() * 100) + 50,
                            Math.floor(Math.random() * 150) + 100,
                            Math.floor(Math.random() * 80) + 30,
                            Math.floor(Math.random() * 60) + 20,
                            Math.floor(Math.random() * 40) + 10,
                            Math.floor(Math.random() * 30) + 5
                        ],
                        backgroundColor: [
                            'rgba(76, 175, 80, 0.8)',
                            'rgba(33, 150, 243, 0.8)',
                            'rgba(255, 152, 0, 0.8)',
                            'rgba(156, 39, 176, 0.8)',
                            'rgba(244, 67, 54, 0.8)',
                            'rgba(96, 125, 139, 0.8)'
                        ],
                        borderColor: [
                            '#4CAF50',
                            '#2196F3',
                            '#FF9800',
                            '#9C27B0',
                            '#F44336',
                            '#607D8B'
                        ],
                        borderWidth: 2
                    }]
                },
                errorRates: {
                    labels: timePoints,
                    datasets: [
                        {
                            label: 'API Errors',
                            data: timePoints.map(() => Math.floor(Math.random() * 10)),
                            borderColor: '#F44336',
                            backgroundColor: 'rgba(244, 67, 54, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Agent Errors',
                            data: timePoints.map(() => Math.floor(Math.random() * 5)),
                            borderColor: '#FF9800',
                            backgroundColor: 'rgba(255, 152, 0, 0.1)',
                            tension: 0.4
                        }
                    ]
                }
            },
            activities: [
                {
                    time: new Date(now - 5 * 60000).toISOString(),
                    title: 'Brand Analysis Completed',
                    description: 'Tesla brand analysis finished with 98% accuracy',
                    type: 'success'
                },
                {
                    time: new Date(now - 15 * 60000).toISOString(),
                    title: 'Image Generation Started',
                    description: 'Generating 5 satirical images for Apple campaign',
                    type: 'info'
                },
                {
                    time: new Date(now - 30 * 60000).toISOString(),
                    title: 'New Campaign Created',
                    description: 'Tech Disruption campaign initialized',
                    type: 'success'
                },
                {
                    time: new Date(now - 45 * 60000).toISOString(),
                    title: 'System Health Check',
                    description: 'All systems operational, performance optimal',
                    type: 'info'
                },
                {
                    time: new Date(now - 60 * 60000).toISOString(),
                    title: 'Analytics Report Generated',
                    description: 'Weekly performance report completed',
                    type: 'success'
                }
            ],
            systemHealth: {
                apiHealth: 'Healthy',
                agentHealth: 'Active',
                databaseHealth: 'Connected',
                networkHealth: 'Stable'
            }
        };
    }
    
    getTimePoints(timeRange) {
        const now = new Date();
        const points = [];
        
        switch (timeRange) {
            case '1h':
                for (let i = 11; i >= 0; i--) {
                    const time = new Date(now - i * 5 * 60000);
                    points.push(time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
                }
                break;
            case '24h':
                for (let i = 23; i >= 0; i--) {
                    const time = new Date(now - i * 60 * 60000);
                    points.push(time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
                }
                break;
            case '7d':
                for (let i = 6; i >= 0; i--) {
                    const time = new Date(now - i * 24 * 60 * 60000);
                    points.push(time.toLocaleDateString([], { weekday: 'short' }));
                }
                break;
            case '30d':
                for (let i = 29; i >= 0; i--) {
                    const time = new Date(now - i * 24 * 60 * 60000);
                    points.push(time.toLocaleDateString([], { month: 'short', day: 'numeric' }));
                }
                break;
            case '90d':
                for (let i = 11; i >= 0; i--) {
                    const time = new Date(now - i * 7 * 24 * 60 * 60000);
                    points.push(time.toLocaleDateString([], { month: 'short', day: 'numeric' }));
                }
                break;
            default:
                return [];
        }
        
        return points;
    }
    
    // Real-time data integration methods
    async loadRealTimeData() {
        try {
            console.log('Loading real-time analytics data...');
            
            // Fetch data from enhanced analytics API
            const response = await fetch('/api/enhanced/analytics', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`Analytics API error: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.analyticsData = this.transformAPIData(result.analytics);
                this.updateDashboardFromRealData();
                this.showConnectionStatus(true);
                console.log('Real-time data loaded successfully');
            } else {
                console.warn('Analytics API returned error:', result.message);
                this.fallbackToMockData();
            }
            
        } catch (error) {
            console.error('Failed to load real-time data:', error);
            this.showConnectionStatus(false);
            this.fallbackToMockData();
        }
    }
    
    transformAPIData(apiData) {
        // Transform API response to dashboard format
        const transformed = {
            kpis: {
                totalAnalyses: apiData.total_campaigns || 0,
                totalImages: apiData.total_generated_images || 0,
                totalCampaigns: apiData.unique_brands || 0,
                avgResponseTime: apiData.average_generation_time || 0,
                analysesChange: this.calculateChange(apiData.recent_campaigns || 0, apiData.total_campaigns || 0),
                imagesChange: this.calculateChange(apiData.recent_images || 0, apiData.total_generated_images || 0),
                campaignsChange: this.calculateChange(apiData.recent_brands || 0, apiData.unique_brands || 0),
                responseTimeChange: this.calculatePerformanceChange(apiData.average_generation_time || 0)
            },
            charts: this.generateChartsFromAPIData(apiData),
            activities: this.generateActivitiesFromAPIData(apiData),
            systemHealth: {
                status: 'healthy',
                uptime: apiData.platform_uptime || '99.9%',
                responseTime: apiData.average_response_time || 150,
                errorRate: apiData.error_rate || 0.1
            }
        };
        
        return transformed;
    }
    
    calculateChange(recent, total) {
        if (total === 0) return 0;
        const recentRatio = recent / total;
        return ((recentRatio - 0.1) * 100).toFixed(1); // Assuming 10% baseline
    }
    
    calculatePerformanceChange(currentTime) {
        const baseline = 500; // 500ms baseline
        const change = ((baseline - currentTime) / baseline * 100);
        return change.toFixed(1);
    }
    
    generateChartsFromAPIData(apiData) {
        const timePoints = this.getTimePoints(this.currentTimeRange);
        
        return {
            usageTrends: {
                labels: timePoints,
                datasets: [
                    {
                        label: 'Brand Analyses',
                        data: this.generateTrendData(apiData.total_campaigns || 0, timePoints.length),
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Image Generation',
                        data: this.generateTrendData(apiData.total_generated_images || 0, timePoints.length),
                        borderColor: '#2196F3',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Campaign Activities',
                        data: this.generateTrendData(apiData.unique_brands || 0, timePoints.length),
                        borderColor: '#FF9800',
                        backgroundColor: 'rgba(255, 152, 0, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            performanceMetrics: {
                labels: ['Generation Time', 'Processing Speed', 'Success Rate', 'Quality Score'],
                datasets: [{
                    label: 'Performance Metrics',
                    data: [
                        apiData.average_generation_time || 0,
                        apiData.average_processing_speed || 85,
                        apiData.success_rate || 95,
                        apiData.quality_score || 88
                    ],
                    backgroundColor: [
                        'rgba(76, 175, 80, 0.8)',
                        'rgba(33, 150, 243, 0.8)',
                        'rgba(255, 152, 0, 0.8)',
                        'rgba(156, 39, 176, 0.8)'
                    ],
                    borderColor: [
                        '#4CAF50',
                        '#2196F3',
                        '#FF9800',
                        '#9C27B0'
                    ],
                    borderWidth: 2
                }]
            }
        };
    }
    
    generateTrendData(total, points) {
        // Generate realistic trend data based on total
        const baseValue = Math.floor(total / points);
        return Array.from({ length: points }, (_, i) => {
            const variation = Math.random() * 0.3 - 0.15; // ±15% variation
            return Math.max(0, Math.floor(baseValue * (1 + variation) + Math.random() * 10));
        });
    }
    
    generateActivitiesFromAPIData(apiData) {
        const activities = [];
        const now = new Date();
        
        // Generate recent activities based on API data
        if (apiData.recent_campaigns > 0) {
            activities.push({
                time: new Date(now - Math.random() * 3600000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                action: 'Campaign Created',
                details: `New brand analysis campaign started`,
                type: 'campaign'
            });
        }
        
        if (apiData.recent_images > 0) {
            activities.push({
                time: new Date(now - Math.random() * 1800000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                action: 'Images Generated',
                details: `${apiData.recent_images} images created successfully`,
                type: 'generation'
            });
        }
        
        return activities.slice(0, 5); // Limit to 5 recent activities
    }
    
    updateDashboardFromRealData() {
        this.updateKPIs(this.analyticsData.kpis);
        this.updateCharts(this.analyticsData.charts);
        this.updateActivityTimeline(this.analyticsData.activities);
        this.updateSystemHealth(this.analyticsData.systemHealth);
    }
    
    showConnectionStatus(isConnected) {
        this.isConnected = isConnected;
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            statusElement.className = `connection-status ${isConnected ? 'connected' : 'disconnected'}`;
            statusElement.textContent = isConnected ? 'Live Data' : 'Offline Mode';
        }
    }
    
    fallbackToMockData() {
        console.log('Falling back to mock data...');
        this.loadMockData();
    }
    
    startRealTimeUpdates() {
        // Start real-time updates every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadRealTimeData();
        }, 30000);
        
        // Initial load
        this.loadRealTimeData();
    }
    
    // Enhanced analytics tracking
    async trackEvent(eventType, eventData) {
        try {
            const response = await fetch('/api/enhanced/analytics/track', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    event_type: eventType,
                    event_data: eventData,
                    session_id: this.getSessionId(),
                    timestamp: new Date().toISOString()
                })
            });
            
            const result = await response.json();
            if (result.success) {
                console.log('Event tracked:', eventType, result.tracking_id);
            }
        } catch (error) {
            console.error('Failed to track event:', error);
        }
    }
    
    getSessionId() {
        // Generate or retrieve session ID
        let sessionId = sessionStorage.getItem('analytics_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('analytics_session_id', sessionId);
        }
        return sessionId;
    }
    
    updateKPIs(kpis) {
        // Update KPI values
        const kpiElements = {
            totalAnalyses: document.getElementById('totalAnalyses'),
            totalImages: document.getElementById('totalImages'),
            totalCampaigns: document.getElementById('totalCampaigns'),
            avgResponseTime: document.getElementById('avgResponseTime')
        };
        
        const changeElements = {
            analysesChange: document.getElementById('analysesChange'),
            imagesChange: document.getElementById('imagesChange'),
            campaignsChange: document.getElementById('campaignsChange'),
            responseTimeChange: document.getElementById('responseTimeChange')
        };
        
        // Update values with animation
        Object.entries(kpiElements).forEach(([key, element]) => {
            if (element && kpis[key] !== undefined) {
                this.animateValue(element, 0, kpis[key], 1000, key === 'avgResponseTime' ? 'ms' : '');
            }
        });
        
        // Update change indicators
        Object.entries(changeElements).forEach(([key, element]) => {
            if (element && kpis[key] !== undefined) {
                const value = parseFloat(kpis[key]);
                element.textContent = `${value >= 0 ? '+' : ''}${value}%`;
                element.className = `kpi-change ${value >= 0 ? 'positive' : 'negative'}`;
            }
        });
    }
    
    animateValue(element, start, end, duration, suffix = '') {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            
            if (suffix === 'ms') {
                element.textContent = Math.floor(current) + suffix;
            } else {
                element.textContent = Math.floor(current).toLocaleString() + suffix;
            }
        }, 16);
    }
    
    updateCharts(chartData) {
        // Update usage trends chart
        if (this.charts.usageTrends && chartData.usageTrends) {
            this.charts.usageTrends.data = chartData.usageTrends;
            this.charts.usageTrends.update('active');
        }
        
        // Update performance metrics chart
        if (this.charts.performanceMetrics && chartData.performanceMetrics) {
            this.charts.performanceMetrics.data = chartData.performanceMetrics;
            this.charts.performanceMetrics.update('active');
        }
        
        // Update agent activity chart
        if (this.charts.agentActivity && chartData.agentActivity) {
            this.charts.agentActivity.data = chartData.agentActivity;
            this.charts.agentActivity.update('active');
        }
        
        // Update error rates chart
        if (this.charts.errorRates && chartData.errorRates) {
            this.charts.errorRates.data = chartData.errorRates;
            this.charts.errorRates.update('active');
        }
    }
    
    updateActivityTimeline(activities) {
        const timelineElement = document.getElementById('activityTimeline');
        if (!timelineElement || !activities) return;
        
        const timelineHTML = activities.map(activity => {
            const time = new Date(activity.time);
            const timeString = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const typeIcon = this.getActivityIcon(activity.type);
            
            return `
                <div class="timeline-item ${activity.type}">
                    <div class="timeline-time">
                        <span class="activity-icon">${typeIcon}</span>
                        ${timeString}
                    </div>
                    <div class="timeline-content">
                        <div class="timeline-title">${activity.title}</div>
                        <div class="timeline-description">${activity.description}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        timelineElement.innerHTML = timelineHTML;
    }
    
    getActivityIcon(type) {
        switch (type) {
            case 'success': return '✅';
            case 'warning': return '⚠️';
            case 'error': return '❌';
            case 'info': return 'ℹ️';
            default: return '📋';
        }
    }
    
    updateSystemHealth(healthData) {
        const healthElements = {
            apiHealth: document.getElementById('apiHealth'),
            agentHealth: document.getElementById('agentHealth'),
            databaseHealth: document.getElementById('databaseHealth'),
            networkHealth: document.getElementById('networkHealth')
        };
        
        Object.entries(healthElements).forEach(([key, element]) => {
            if (element && healthData[key]) {
                element.textContent = healthData[key];
                element.className = `health-value ${this.getHealthStatusClass(healthData[key])}`;
            }
        });
        
        // Update health icons
        const healthIcons = {
            apiHealth: document.querySelector('.health-metric:nth-child(1) .health-icon'),
            agentHealth: document.querySelector('.health-metric:nth-child(2) .health-icon'),
            databaseHealth: document.querySelector('.health-metric:nth-child(3) .health-icon'),
            networkHealth: document.querySelector('.health-metric:nth-child(4) .health-icon')
        };
        
        Object.entries(healthIcons).forEach(([key, element]) => {
            if (element && healthData[key.replace('Health', '')]) {
                element.textContent = this.getHealthIcon(healthData[key.replace('Health', '')]);
            }
        });
    }
    
    getHealthStatusClass(status) {
        const lowerStatus = status.toLowerCase();
        if (lowerStatus.includes('healthy') || lowerStatus.includes('active') || lowerStatus.includes('connected') || lowerStatus.includes('stable')) {
            return 'status-healthy';
        } else if (lowerStatus.includes('warning') || lowerStatus.includes('degraded')) {
            return 'status-warning';
        } else if (lowerStatus.includes('error') || lowerStatus.includes('failed') || lowerStatus.includes('down')) {
            return 'status-error';
        }
        return 'status-unknown';
    }
    
    getHealthIcon(status) {
        const lowerStatus = status.toLowerCase();
        if (lowerStatus.includes('healthy') || lowerStatus.includes('active') || lowerStatus.includes('connected') || lowerStatus.includes('stable')) {
            return '💚';
        } else if (lowerStatus.includes('warning') || lowerStatus.includes('degraded')) {
            return '🟡';
        } else if (lowerStatus.includes('error') || lowerStatus.includes('failed') || lowerStatus.includes('down')) {
            return '🔴';
        }
        return '⚪';
    }
    
    filterAnalyticsData() {
        // Filter current data based on metric type
        if (!this.analyticsData) return;
        
        // This would filter the existing data based on the selected metric type
        // For now, we'll just reload the data
        this.loadAnalyticsData();
    }
    
    exportAnalytics() {
        if (!this.analyticsData) {
            alert('No analytics data to export!');
            return;
        }
        
        try {
            // Create comprehensive export data
            const exportData = {
                timestamp: new Date().toISOString(),
                timeRange: this.currentTimeRange,
                metricType: this.currentMetricType,
                summary: {
                    totalAnalyses: this.analyticsData.kpis?.totalAnalyses || 0,
                    totalImages: this.analyticsData.kpis?.totalImages || 0,
                    totalCampaigns: this.analyticsData.kpis?.totalCampaigns || 0,
                    avgResponseTime: this.analyticsData.kpis?.avgResponseTime || 0
                },
                trends: this.analyticsData.charts?.usageTrends || {},
                performance: this.analyticsData.charts?.performanceMetrics || {},
                agentActivity: this.analyticsData.charts?.agentActivity || {},
                errorRates: this.analyticsData.charts?.errorRates || {},
                recentActivities: this.analyticsData.activities || [],
                systemHealth: this.analyticsData.systemHealth || {}
            };
            
            // Convert to JSON and download
            const jsonString = JSON.stringify(exportData, null, 2);
            const blob = new Blob([jsonString], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = `brand-platform-analytics-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            URL.revokeObjectURL(url);
            
            // Also offer CSV export for charts data
            this.exportChartsAsCSV(exportData);
            
            console.log('Analytics data exported successfully');
            
        } catch (error) {
            console.error('Error exporting analytics:', error);
            alert('Error exporting analytics data. Check console for details.');
        }
    }
    
    exportChartsAsCSV(exportData) {
        try {
            let csvContent = 'Analytics Export - Brand Deconstruction Platform\n';
            csvContent += `Generated: ${new Date().toLocaleString()}\n`;
            csvContent += `Time Range: ${this.currentTimeRange}\n`;
            csvContent += `Metric Type: ${this.currentMetricType}\n\n`;
            
            // KPIs section
            csvContent += 'Key Performance Indicators\n';
            csvContent += 'Metric,Value\n';
            csvContent += `Total Analyses,${exportData.summary.totalAnalyses}\n`;
            csvContent += `Total Images,${exportData.summary.totalImages}\n`;
            csvContent += `Total Campaigns,${exportData.summary.totalCampaigns}\n`;
            csvContent += `Average Response Time,${exportData.summary.avgResponseTime}ms\n\n`;
            
            // Usage trends
            if (exportData.trends.labels && exportData.trends.datasets) {
                csvContent += 'Usage Trends\n';
                csvContent += 'Time,' + exportData.trends.datasets.map(d => d.label).join(',') + '\n';
                
                exportData.trends.labels.forEach((label, index) => {
                    csvContent += label + ',';
                    csvContent += exportData.trends.datasets.map(d => d.data[index] || 0).join(',');
                    csvContent += '\n';
                });
                csvContent += '\n';
            }
            
            // Performance metrics
            if (exportData.performance.labels && exportData.performance.datasets) {
                csvContent += 'Performance Metrics\n';
                csvContent += 'Metric,Score\n';
                exportData.performance.labels.forEach((label, index) => {
                    const score = exportData.performance.datasets[0]?.data[index] || 0;
                    csvContent += `${label},${score}\n`;
                });
                csvContent += '\n';
            }
            
            // Agent activity
            if (exportData.agentActivity.labels && exportData.agentActivity.datasets) {
                csvContent += 'Agent Activity\n';
                csvContent += 'Agent,Usage\n';
                exportData.agentActivity.labels.forEach((label, index) => {
                    const usage = exportData.agentActivity.datasets[0]?.data[index] || 0;
                    csvContent += `${label},${usage}\n`;
                });
                csvContent += '\n';
            }
            
            // Recent activities
            if (exportData.recentActivities.length > 0) {
                csvContent += 'Recent Activities\n';
                csvContent += 'Time,Title,Description,Type\n';
                exportData.recentActivities.forEach(activity => {
                    const time = new Date(activity.time).toLocaleString();
                    csvContent += `"${time}","${activity.title}","${activity.description}","${activity.type}"\n`;
                });
                csvContent += '\n';
            }
            
            // System health
            csvContent += 'System Health\n';
            csvContent += 'Component,Status\n';
            Object.entries(exportData.systemHealth).forEach(([component, status]) => {
                csvContent += `${component},${status}\n`;
            });
            
            // Download CSV
            const csvBlob = new Blob([csvContent], { type: 'text/csv' });
            const csvUrl = URL.createObjectURL(csvBlob);
            
            const csvLink = document.createElement('a');
            csvLink.href = csvUrl;
            csvLink.download = `brand-platform-analytics-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(csvLink);
            csvLink.click();
            document.body.removeChild(csvLink);
            
            URL.revokeObjectURL(csvUrl);
            
        } catch (error) {
            console.error('Error exporting CSV:', error);
        }
    }
    
    updateLoadingState(isLoading) {
        const loadingIndicators = document.querySelectorAll('.analytics-section .chart-container');
        
        loadingIndicators.forEach(container => {
            if (isLoading) {
                container.classList.add('loading');
                if (!container.querySelector('.loading-spinner')) {
                    const spinner = document.createElement('div');
                    spinner.className = 'loading-spinner';
                    spinner.innerHTML = '<div class="spinner"></div><p>Loading analytics...</p>';
                    container.appendChild(spinner);
                }
            } else {
                container.classList.remove('loading');
                const spinner = container.querySelector('.loading-spinner');
                if (spinner) {
                    spinner.remove();
                }
            }
        });
    }
    
    startAutoRefresh() {
        // Refresh every 5 minutes
        this.refreshInterval = setInterval(() => {
            this.loadAnalyticsData();
        }, 5 * 60000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    destroy() {
        this.stopAutoRefresh();
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        this.charts = {};
        this.analyticsData = {};
    }
}

// Initialize analytics dashboard when the page loads
let analyticsDashboard;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize only if we're on the analytics dashboard tab
    if (document.getElementById('usageTrendsChart')) {
        analyticsDashboard = new AnalyticsDashboard();
    }
});

// Initialize when tab becomes active
document.addEventListener('tabActivated', function(e) {
    if (e.detail === 'analytics-dashboard' && !analyticsDashboard) {
        analyticsDashboard = new AnalyticsDashboard();
    }
});

// Clean up when tab becomes inactive
document.addEventListener('tabDeactivated', function(e) {
    if (e.detail === 'analytics-dashboard' && analyticsDashboard) {
        analyticsDashboard.stopAutoRefresh();
    }
});
