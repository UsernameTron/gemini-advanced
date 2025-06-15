/**
 * Visual Workflow Builder for Brand Deconstruction Platform
 * Advanced drag-and-drop workflow designer with real-time validation
 */

class WorkflowBuilder {
    constructor() {
        this.canvas = null;
        this.nodes = new Map();
        this.connections = new Map();
        this.selectedNode = null;
        this.draggedComponent = null;
        this.isConnecting = false;
        this.connectionStart = null;
        this.currentWorkflow = null;
        this.nodeIdCounter = 0;
        this.connectionIdCounter = 0;
        
        this.nodeTypes = {
            'brand-agent': {
                name: 'Brand Agent',
                icon: '🎯',
                color: '#4CAF50',
                inputs: ['trigger'],
                outputs: ['analysis', 'concepts'],
                properties: {
                    'brand_name': { type: 'text', label: 'Brand Name', required: true },
                    'analysis_depth': { type: 'select', label: 'Analysis Depth', options: ['quick', 'standard', 'comprehensive'], default: 'standard' },
                    'include_vulnerabilities': { type: 'boolean', label: 'Include Vulnerabilities', default: true }
                }
            },
            'image-agent': {
                name: 'Image Agent',
                icon: '🎨',
                color: '#2196F3',
                inputs: ['concepts', 'style'],
                outputs: ['images', 'metadata'],
                properties: {
                    'image_count': { type: 'number', label: 'Image Count', min: 1, max: 10, default: 3 },
                    'satirical_intensity': { type: 'slider', label: 'Satirical Intensity', min: 1, max: 10, default: 5 },
                    'style_prompt': { type: 'textarea', label: 'Style Prompt', placeholder: 'Additional style instructions...' }
                }
            },
            'analytics-agent': {
                name: 'Analytics Agent',
                icon: '📊',
                color: '#FF9800',
                inputs: ['data'],
                outputs: ['insights', 'metrics'],
                properties: {
                    'metric_types': { type: 'multiselect', label: 'Metric Types', options: ['performance', 'engagement', 'sentiment'], default: ['performance'] },
                    'analysis_period': { type: 'select', label: 'Analysis Period', options: ['1h', '24h', '7d', '30d'], default: '24h' }
                }
            },
            'decision': {
                name: 'Decision Node',
                icon: '🤔',
                color: '#9C27B0',
                inputs: ['input'],
                outputs: ['true', 'false'],
                properties: {
                    'condition': { type: 'text', label: 'Condition', required: true, placeholder: 'Enter condition logic...' },
                    'condition_type': { type: 'select', label: 'Condition Type', options: ['simple', 'complex', 'script'], default: 'simple' }
                }
            },
            'loop': {
                name: 'Loop Node',
                icon: '🔄',
                color: '#607D8B',
                inputs: ['input', 'iterator'],
                outputs: ['item', 'complete'],
                properties: {
                    'loop_type': { type: 'select', label: 'Loop Type', options: ['for_each', 'while', 'count'], default: 'for_each' },
                    'max_iterations': { type: 'number', label: 'Max Iterations', min: 1, max: 1000, default: 10 }
                }
            },
            'parallel': {
                name: 'Parallel Node',
                icon: '⚡',
                color: '#795548',
                inputs: ['input'],
                outputs: ['branch1', 'branch2', 'branch3'],
                properties: {
                    'branch_count': { type: 'number', label: 'Branch Count', min: 2, max: 5, default: 2 },
                    'wait_for_all': { type: 'boolean', label: 'Wait for All Branches', default: true }
                }
            },
            'input': {
                name: 'Input Node',
                icon: '📥',
                color: '#4CAF50',
                inputs: [],
                outputs: ['output'],
                properties: {
                    'input_name': { type: 'text', label: 'Input Name', required: true },
                    'input_type': { type: 'select', label: 'Input Type', options: ['text', 'number', 'boolean', 'json'], default: 'text' },
                    'default_value': { type: 'text', label: 'Default Value' }
                }
            },
            'output': {
                name: 'Output Node',
                icon: '📤',
                color: '#F44336',
                inputs: ['input'],
                outputs: [],
                properties: {
                    'output_name': { type: 'text', label: 'Output Name', required: true },
                    'output_format': { type: 'select', label: 'Output Format', options: ['json', 'text', 'html', 'csv'], default: 'json' }
                }
            },
            'transform': {
                name: 'Transform Node',
                icon: '🔧',
                color: '#3F51B5',
                inputs: ['input'],
                outputs: ['output'],
                properties: {
                    'transform_type': { type: 'select', label: 'Transform Type', options: ['map', 'filter', 'reduce', 'custom'], default: 'map' },
                    'transform_script': { type: 'textarea', label: 'Transform Script', placeholder: 'Enter transformation logic...' }
                }
            }
        };
        
        this.init();
    }
    
    init() {
        this.setupCanvas();
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.loadWorkflowTemplates();
    }
    
    setupCanvas() {
        this.canvas = document.getElementById('workflowCanvas');
        this.canvasContent = document.getElementById('canvasContent');
        this.connectionLayer = document.getElementById('connectionLayer');
        
        if (!this.canvas) return;
        
        // Set up canvas dimensions
        this.updateCanvasSize();
        window.addEventListener('resize', () => this.updateCanvasSize());
    }
    
    updateCanvasSize() {
        if (!this.canvas || !this.connectionLayer) return;
        
        const rect = this.canvas.getBoundingClientRect();
        this.connectionLayer.setAttribute('width', rect.width);
        this.connectionLayer.setAttribute('height', rect.height);
    }
    
    setupEventListeners() {
        // Toolbar buttons
        const newWorkflowBtn = document.getElementById('newWorkflow');
        if (newWorkflowBtn) {
            newWorkflowBtn.addEventListener('click', () => this.newWorkflow());
        }
        
        const saveWorkflowBtn = document.getElementById('saveWorkflow');
        if (saveWorkflowBtn) {
            saveWorkflowBtn.addEventListener('click', () => this.saveWorkflow());
        }
        
        const loadWorkflowBtn = document.getElementById('loadWorkflow');
        if (loadWorkflowBtn) {
            loadWorkflowBtn.addEventListener('click', () => this.loadWorkflow());
        }
        
        const runWorkflowBtn = document.getElementById('runWorkflow');
        if (runWorkflowBtn) {
            runWorkflowBtn.addEventListener('click', () => this.runWorkflow());
        }
        
        const validateWorkflowBtn = document.getElementById('validateWorkflow');
        if (validateWorkflowBtn) {
            validateWorkflowBtn.addEventListener('click', () => this.validateWorkflow());
        }
        
        // Template selector
        const templateSelector = document.getElementById('workflowTemplate');
        if (templateSelector) {
            templateSelector.addEventListener('change', (e) => this.loadTemplate(e.target.value));
        }
        
        // Canvas events
        if (this.canvas) {
            this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
            this.canvas.addEventListener('contextmenu', (e) => this.handleCanvasRightClick(e));
        }
        
        // Global key events
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
    }
    
    setupDragAndDrop() {
        // Make components draggable
        const components = document.querySelectorAll('.component-item');
        components.forEach(component => {
            component.addEventListener('dragstart', (e) => this.handleDragStart(e));
            component.addEventListener('dragend', (e) => this.handleDragEnd(e));
        });
        
        // Set up drop zone
        if (this.canvas) {
            this.canvas.addEventListener('dragover', (e) => this.handleDragOver(e));
            this.canvas.addEventListener('drop', (e) => this.handleDrop(e));
        }
    }
    
    handleDragStart(e) {
        this.draggedComponent = {
            type: e.target.dataset.type,
            name: e.target.querySelector('.component-name').textContent
        };
        e.dataTransfer.effectAllowed = 'copy';
    }
    
    handleDragEnd(e) {
        this.draggedComponent = null;
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    }
    
    handleDrop(e) {
        e.preventDefault();
        
        if (!this.draggedComponent) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        this.createNode(this.draggedComponent.type, x, y);
        this.draggedComponent = null;
    }
    
    createNode(type, x, y, properties = {}) {
        const nodeId = `node_${this.nodeIdCounter++}`;
        const nodeType = this.nodeTypes[type];
        
        if (!nodeType) {
            console.error('Unknown node type:', type);
            return null;
        }
        
        const node = {
            id: nodeId,
            type: type,
            name: nodeType.name,
            x: x,
            y: y,
            properties: { ...this.getDefaultProperties(type), ...properties },
            inputs: nodeType.inputs || [],
            outputs: nodeType.outputs || [],
            connections: {
                inputs: {},
                outputs: {}
            }
        };
        
        this.nodes.set(nodeId, node);
        this.renderNode(node);
        this.updateComponentCount();
        
        return node;
    }
    
    getDefaultProperties(type) {
        const nodeType = this.nodeTypes[type];
        if (!nodeType.properties) return {};
        
        const defaults = {};
        Object.entries(nodeType.properties).forEach(([key, prop]) => {
            if (prop.default !== undefined) {
                defaults[key] = prop.default;
            }
        });
        return defaults;
    }
    
    renderNode(node) {
        const nodeElement = document.createElement('div');
        nodeElement.className = 'workflow-node';
        nodeElement.dataset.nodeId = node.id;
        nodeElement.style.left = `${node.x}px`;
        nodeElement.style.top = `${node.y}px`;
        
        const nodeType = this.nodeTypes[node.type];
        nodeElement.style.borderColor = nodeType.color;
        
        nodeElement.innerHTML = `
            <div class="node-header" style="background-color: ${nodeType.color}">
                <span class="node-icon">${nodeType.icon}</span>
                <span class="node-title">${node.name}</span>
                <button class="node-delete" onclick="workflowBuilder.deleteNode('${node.id}')">×</button>
            </div>
            <div class="node-body">
                <div class="node-inputs">
                    ${node.inputs.map(input => `
                        <div class="node-port input-port" data-port="${input}" data-node="${node.id}">
                            <span class="port-label">${input}</span>
                            <div class="port-connector"></div>
                        </div>
                    `).join('')}
                </div>
                <div class="node-outputs">
                    ${node.outputs.map(output => `
                        <div class="node-port output-port" data-port="${output}" data-node="${node.id}">
                            <div class="port-connector"></div>
                            <span class="port-label">${output}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Add event listeners
        nodeElement.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectNode(node.id);
        });
        
        nodeElement.addEventListener('mousedown', (e) => this.startNodeDrag(e, node.id));
        
        // Port connection events
        const ports = nodeElement.querySelectorAll('.port-connector');
        ports.forEach(port => {
            port.addEventListener('mousedown', (e) => this.startConnection(e));
            port.addEventListener('mouseup', (e) => this.endConnection(e));
        });
        
        this.canvasContent.appendChild(nodeElement);
    }
    
    selectNode(nodeId) {
        // Clear previous selection
        document.querySelectorAll('.workflow-node.selected').forEach(node => {
            node.classList.remove('selected');
        });
        
        // Select new node
        const nodeElement = document.querySelector(`[data-node-id="${nodeId}"]`);
        if (nodeElement) {
            nodeElement.classList.add('selected');
            this.selectedNode = nodeId;
            this.showNodeProperties(nodeId);
        }
    }
    
    showNodeProperties(nodeId) {
        const node = this.nodes.get(nodeId);
        if (!node) return;
        
        const nodeType = this.nodeTypes[node.type];
        const propertiesPanel = document.getElementById('nodeProperties');
        
        if (!propertiesPanel) return;
        
        let propertiesHTML = `
            <div class="properties-header">
                <h4>${node.name}</h4>
                <small>ID: ${node.id}</small>
            </div>
            <div class="properties-form">
        `;
        
        if (nodeType.properties) {
            Object.entries(nodeType.properties).forEach(([key, prop]) => {
                const value = node.properties[key] || '';
                
                propertiesHTML += `<div class="property-group">`;
                propertiesHTML += `<label class="property-label">${prop.label}</label>`;
                
                switch (prop.type) {
                    case 'text':
                        propertiesHTML += `<input type="text" class="property-input" data-property="${key}" value="${value}" ${prop.required ? 'required' : ''} placeholder="${prop.placeholder || ''}">`;
                        break;
                    case 'textarea':
                        propertiesHTML += `<textarea class="property-input" data-property="${key}" ${prop.required ? 'required' : ''} placeholder="${prop.placeholder || ''}">${value}</textarea>`;
                        break;
                    case 'number':
                        propertiesHTML += `<input type="number" class="property-input" data-property="${key}" value="${value}" min="${prop.min || ''}" max="${prop.max || ''}">`;
                        break;
                    case 'boolean':
                        propertiesHTML += `<input type="checkbox" class="property-checkbox" data-property="${key}" ${value ? 'checked' : ''}>`;
                        break;
                    case 'select':
                        propertiesHTML += `<select class="property-select" data-property="${key}">`;
                        prop.options.forEach(option => {
                            propertiesHTML += `<option value="${option}" ${value === option ? 'selected' : ''}>${option}</option>`;
                        });
                        propertiesHTML += `</select>`;
                        break;
                    case 'slider':
                        propertiesHTML += `<input type="range" class="property-slider" data-property="${key}" value="${value}" min="${prop.min}" max="${prop.max}">`;
                        propertiesHTML += `<span class="slider-value">${value}</span>`;
                        break;
                }
                
                propertiesHTML += `</div>`;
            });
        }
        
        propertiesHTML += `
            </div>
            <div class="properties-actions">
                <button class="secondary-button" onclick="workflowBuilder.duplicateNode('${nodeId}')">Duplicate</button>
                <button class="danger-button" onclick="workflowBuilder.deleteNode('${nodeId}')">Delete</button>
            </div>
        `;
        
        propertiesPanel.innerHTML = propertiesHTML;
        
        // Add event listeners to property inputs
        propertiesPanel.querySelectorAll('.property-input, .property-checkbox, .property-select, .property-slider').forEach(input => {
            input.addEventListener('change', (e) => {
                const property = e.target.dataset.property;
                let value = e.target.value;
                
                if (e.target.type === 'checkbox') {
                    value = e.target.checked;
                } else if (e.target.type === 'number' || e.target.type === 'range') {
                    value = parseFloat(value);
                }
                
                node.properties[property] = value;
                
                // Update slider display
                if (e.target.type === 'range') {
                    const sliderValue = e.target.parentNode.querySelector('.slider-value');
                    if (sliderValue) {
                        sliderValue.textContent = value;
                    }
                }
            });
        });
    }
    
    startNodeDrag(e, nodeId) {
        if (e.target.closest('.port-connector') || e.target.closest('.node-delete')) {
            return; // Don't drag if clicking on ports or delete button
        }
        
        const node = this.nodes.get(nodeId);
        if (!node) return;
        
        const startX = e.clientX - node.x;
        const startY = e.clientY - node.y;
        
        const handleMouseMove = (e) => {
            node.x = e.clientX - startX;
            node.y = e.clientY - startY;
            
            const nodeElement = document.querySelector(`[data-node-id="${nodeId}"]`);
            if (nodeElement) {
                nodeElement.style.left = `${node.x}px`;
                nodeElement.style.top = `${node.y}px`;
            }
            
            this.updateConnections();
        };
        
        const handleMouseUp = () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
        
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    }
    
    startConnection(e) {
        e.stopPropagation();
        
        const port = e.target.closest('.node-port');
        if (!port) return;
        
        this.isConnecting = true;
        this.connectionStart = {
            nodeId: port.dataset.node,
            port: port.dataset.port,
            isOutput: port.classList.contains('output-port')
        };
        
        // Visual feedback
        port.classList.add('connecting');
    }
    
    endConnection(e) {
        if (!this.isConnecting || !this.connectionStart) return;
        
        e.stopPropagation();
        
        const port = e.target.closest('.node-port');
        if (!port) {
            this.cancelConnection();
            return;
        }
        
        const connectionEnd = {
            nodeId: port.dataset.node,
            port: port.dataset.port,
            isOutput: port.classList.contains('output-port')
        };
        
        // Validate connection
        if (this.validateConnection(this.connectionStart, connectionEnd)) {
            this.createConnection(this.connectionStart, connectionEnd);
        }
        
        this.cancelConnection();
    }
    
    validateConnection(start, end) {
        // Can't connect to same node
        if (start.nodeId === end.nodeId) return false;
        
        // Must connect output to input
        if (start.isOutput === end.isOutput) return false;
        
        // Ensure proper direction (output -> input)
        const output = start.isOutput ? start : end;
        const input = start.isOutput ? end : start;
        
        // Check if connection already exists
        const existingConnection = Array.from(this.connections.values()).find(conn => 
            conn.from.nodeId === output.nodeId && 
            conn.from.port === output.port && 
            conn.to.nodeId === input.nodeId && 
            conn.to.port === input.port
        );
        
        return !existingConnection;
    }
    
    createConnection(start, end) {
        const connectionId = `conn_${this.connectionIdCounter++}`;
        
        const output = start.isOutput ? start : end;
        const input = start.isOutput ? end : start;
        
        const connection = {
            id: connectionId,
            from: output,
            to: input
        };
        
        this.connections.set(connectionId, connection);
        
        // Update node connection data
        const fromNode = this.nodes.get(output.nodeId);
        const toNode = this.nodes.get(input.nodeId);
        
        if (!fromNode.connections.outputs[output.port]) {
            fromNode.connections.outputs[output.port] = [];
        }
        fromNode.connections.outputs[output.port].push(connectionId);
        
        toNode.connections.inputs[input.port] = connectionId;
        
        this.renderConnection(connection);
        this.updateConnectionCount();
    }
    
    renderConnection(connection) {
        const fromElement = document.querySelector(`[data-node="${connection.from.nodeId}"] [data-port="${connection.from.port}"] .port-connector`);
        const toElement = document.querySelector(`[data-node="${connection.to.nodeId}"] [data-port="${connection.to.port}"] .port-connector`);
        
        if (!fromElement || !toElement) return;
        
        this.updateConnections();
    }
    
    updateConnections() {
        // Clear existing connection lines
        this.connectionLayer.innerHTML = '';
        
        this.connections.forEach(connection => {
            this.drawConnection(connection);
        });
    }
    
    drawConnection(connection) {
        const fromElement = document.querySelector(`[data-node="${connection.from.nodeId}"] [data-port="${connection.from.port}"] .port-connector`);
        const toElement = document.querySelector(`[data-node="${connection.to.nodeId}"] [data-port="${connection.to.port}"] .port-connector`);
        
        if (!fromElement || !toElement) return;
        
        const canvasRect = this.canvas.getBoundingClientRect();
        const fromRect = fromElement.getBoundingClientRect();
        const toRect = toElement.getBoundingClientRect();
        
        const fromX = fromRect.left - canvasRect.left + fromRect.width / 2;
        const fromY = fromRect.top - canvasRect.top + fromRect.height / 2;
        const toX = toRect.left - canvasRect.left + toRect.width / 2;
        const toY = toRect.top - canvasRect.top + toRect.height / 2;
        
        // Create SVG path with bezier curve
        const controlPoint1X = fromX + (toX - fromX) * 0.5;
        const controlPoint1Y = fromY;
        const controlPoint2X = toX - (toX - fromX) * 0.5;
        const controlPoint2Y = toY;
        
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', `M ${fromX} ${fromY} C ${controlPoint1X} ${controlPoint1Y}, ${controlPoint2X} ${controlPoint2Y}, ${toX} ${toY}`);
        path.setAttribute('stroke', '#00BCD4');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');
        path.classList.add('connection-line');
        path.dataset.connectionId = connection.id;
        
        // Add click handler for connection deletion
        path.addEventListener('click', (e) => {
            e.stopPropagation();
            if (confirm('Delete this connection?')) {
                this.deleteConnection(connection.id);
            }
        });
        
        this.connectionLayer.appendChild(path);
    }
    
    cancelConnection() {
        this.isConnecting = false;
        this.connectionStart = null;
        
        // Remove visual feedback
        document.querySelectorAll('.port-connector.connecting').forEach(port => {
            port.classList.remove('connecting');
        });
    }
    
    deleteNode(nodeId) {
        if (!confirm('Delete this node and all its connections?')) return;
        
        // Remove all connections to/from this node
        const connectionsToDelete = [];
        this.connections.forEach((connection, id) => {
            if (connection.from.nodeId === nodeId || connection.to.nodeId === nodeId) {
                connectionsToDelete.push(id);
            }
        });
        
        connectionsToDelete.forEach(id => this.deleteConnection(id));
        
        // Remove node
        this.nodes.delete(nodeId);
        
        // Remove DOM element
        const nodeElement = document.querySelector(`[data-node-id="${nodeId}"]`);
        if (nodeElement) {
            nodeElement.remove();
        }
        
        // Clear properties if this node was selected
        if (this.selectedNode === nodeId) {
            this.selectedNode = null;
            document.getElementById('nodeProperties').innerHTML = '<div class="properties-placeholder">Select a component to view its properties</div>';
        }
        
        this.updateComponentCount();
    }
    
    deleteConnection(connectionId) {
        const connection = this.connections.get(connectionId);
        if (!connection) return;
        
        // Update node connection data
        const fromNode = this.nodes.get(connection.from.nodeId);
        const toNode = this.nodes.get(connection.to.nodeId);
        
        if (fromNode && fromNode.connections.outputs[connection.from.port]) {
            fromNode.connections.outputs[connection.from.port] = fromNode.connections.outputs[connection.from.port].filter(id => id !== connectionId);
        }
        
        if (toNode) {
            delete toNode.connections.inputs[connection.to.port];
        }
        
        // Remove connection
        this.connections.delete(connectionId);
        
        // Remove DOM element
        const connectionElement = document.querySelector(`[data-connection-id="${connectionId}"]`);
        if (connectionElement) {
            connectionElement.remove();
        }
        
        this.updateConnectionCount();
    }
    
    duplicateNode(nodeId) {
        const node = this.nodes.get(nodeId);
        if (!node) return;
        
        const newNode = this.createNode(node.type, node.x + 50, node.y + 50, { ...node.properties });
        if (newNode) {
            this.selectNode(newNode.id);
        }
    }
    
    newWorkflow() {
        if (this.nodes.size > 0 && !confirm('Create new workflow? This will clear all current work.')) {
            return;
        }
        
        this.clearWorkflow();
        this.currentWorkflow = {
            id: null,
            name: 'New Workflow',
            description: '',
            created: new Date().toISOString(),
            modified: new Date().toISOString()
        };
        
        this.updateWorkflowStatus('Ready');
    }
    
    clearWorkflow() {
        // Clear all nodes and connections
        this.nodes.clear();
        this.connections.clear();
        this.selectedNode = null;
        this.nodeIdCounter = 0;
        this.connectionIdCounter = 0;
        
        // Clear DOM
        this.canvasContent.innerHTML = '';
        this.connectionLayer.innerHTML = '';
        
        // Clear properties panel
        document.getElementById('nodeProperties').innerHTML = '<div class="properties-placeholder">Select a component to view its properties</div>';
        
        this.updateComponentCount();
        this.updateConnectionCount();
    }
    
    saveWorkflow() {
        if (this.nodes.size === 0) {
            alert('No workflow to save!');
            return;
        }
        
        const workflowData = {
            ...this.currentWorkflow,
            nodes: Array.from(this.nodes.values()),
            connections: Array.from(this.connections.values()),
            modified: new Date().toISOString()
        };
        
        // Save to localStorage for now (can be extended to API)
        const workflowName = prompt('Enter workflow name:', this.currentWorkflow?.name || 'My Workflow');
        if (!workflowName) return;
        
        workflowData.name = workflowName;
        workflowData.id = workflowData.id || `workflow_${Date.now()}`;
        
        const savedWorkflows = JSON.parse(localStorage.getItem('brandPlatformWorkflows') || '{}');
        savedWorkflows[workflowData.id] = workflowData;
        localStorage.setItem('brandPlatformWorkflows', JSON.stringify(savedWorkflows));
        
        this.currentWorkflow = workflowData;
        this.updateWorkflowStatus(`Saved: ${workflowName}`);
        
        alert('Workflow saved successfully!');
    }
    
    loadWorkflow() {
        const savedWorkflows = JSON.parse(localStorage.getItem('brandPlatformWorkflows') || '{}');
        const workflowList = Object.values(savedWorkflows);
        
        if (workflowList.length === 0) {
            alert('No saved workflows found!');
            return;
        }
        
        // Simple workflow selector (can be enhanced with a proper dialog)
        const workflowNames = workflowList.map(w => `${w.name} (${new Date(w.modified).toLocaleDateString()})`);
        const selection = prompt(`Select workflow to load:\n${workflowNames.map((name, i) => `${i + 1}. ${name}`).join('\n')}\n\nEnter number:`);
        
        const index = parseInt(selection) - 1;
        if (isNaN(index) || index < 0 || index >= workflowList.length) {
            return;
        }
        
        const workflow = workflowList[index];
        this.loadWorkflowData(workflow);
    }
    
    loadWorkflowData(workflowData) {
        this.clearWorkflow();
        
        this.currentWorkflow = workflowData;
        
        // Load nodes
        workflowData.nodes.forEach(nodeData => {
            const node = {
                ...nodeData,
                connections: { inputs: {}, outputs: {} }
            };
            this.nodes.set(node.id, node);
            this.renderNode(node);
        });
        
        // Load connections
        workflowData.connections.forEach(connectionData => {
            this.connections.set(connectionData.id, connectionData);
            
            // Restore node connection references
            const fromNode = this.nodes.get(connectionData.from.nodeId);
            const toNode = this.nodes.get(connectionData.to.nodeId);
            
            if (fromNode && toNode) {
                if (!fromNode.connections.outputs[connectionData.from.port]) {
                    fromNode.connections.outputs[connectionData.from.port] = [];
                }
                fromNode.connections.outputs[connectionData.from.port].push(connectionData.id);
                toNode.connections.inputs[connectionData.to.port] = connectionData.id;
            }
        });
        
        // Update counters
        this.nodeIdCounter = Math.max(...Array.from(this.nodes.keys()).map(id => parseInt(id.split('_')[1]))) + 1 || 0;
        this.connectionIdCounter = Math.max(...Array.from(this.connections.keys()).map(id => parseInt(id.split('_')[1]))) + 1 || 0;
        
        this.updateConnections();
        this.updateComponentCount();
        this.updateConnectionCount();
        this.updateWorkflowStatus(`Loaded: ${workflowData.name}`);
    }
    
    runWorkflow() {
        if (this.nodes.size === 0) {
            alert('No workflow to run!');
            return;
        }
        
        const validation = this.validateWorkflow(false);
        if (!validation.isValid) {
            alert(`Cannot run workflow: ${validation.errors.join(', ')}`);
            return;
        }
        
        // Convert workflow to execution format
        const workflowExecution = {
            workflow: {
                nodes: Array.from(this.nodes.values()),
                connections: Array.from(this.connections.values())
            },
            timestamp: new Date().toISOString()
        };
        
        this.updateWorkflowStatus('Running...');
        
        // Send to backend for execution
        fetch('/api/workflow/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(workflowExecution)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.updateWorkflowStatus('Execution Complete');
                alert('Workflow executed successfully!');
            } else {
                this.updateWorkflowStatus('Execution Failed');
                alert(`Workflow execution failed: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Workflow execution error:', error);
            this.updateWorkflowStatus('Execution Error');
            alert('Error executing workflow. Check console for details.');
        });
    }
    
    validateWorkflow(showAlert = true) {
        const errors = [];
        const warnings = [];
        
        if (this.nodes.size === 0) {
            errors.push('Workflow is empty');
        }
        
        // Check for orphaned nodes
        const connectedNodes = new Set();
        this.connections.forEach(conn => {
            connectedNodes.add(conn.from.nodeId);
            connectedNodes.add(conn.to.nodeId);
        });
        
        this.nodes.forEach((node, nodeId) => {
            if (!connectedNodes.has(nodeId) && this.nodes.size > 1) {
                warnings.push(`Node ${node.name} is not connected`);
            }
            
            // Validate required properties
            const nodeType = this.nodeTypes[node.type];
            if (nodeType.properties) {
                Object.entries(nodeType.properties).forEach(([key, prop]) => {
                    if (prop.required && (!node.properties[key] || node.properties[key] === '')) {
                        errors.push(`Node ${node.name}: Required property '${prop.label}' is missing`);
                    }
                });
            }
        });
        
        // Check for cycles (basic detection)
        const visited = new Set();
        const recStack = new Set();
        
        const hasCycle = (nodeId) => {
            visited.add(nodeId);
            recStack.add(nodeId);
            
            const node = this.nodes.get(nodeId);
            if (node && node.connections.outputs) {
                for (const outputs of Object.values(node.connections.outputs)) {
                    for (const connId of outputs) {
                        const connection = this.connections.get(connId);
                        if (connection) {
                            const nextNodeId = connection.to.nodeId;
                            if (!visited.has(nextNodeId)) {
                                if (hasCycle(nextNodeId)) return true;
                            } else if (recStack.has(nextNodeId)) {
                                return true;
                            }
                        }
                    }
                }
            }
            
            recStack.delete(nodeId);
            return false;
        };
        
        for (const nodeId of this.nodes.keys()) {
            if (!visited.has(nodeId) && hasCycle(nodeId)) {
                errors.push('Workflow contains cycles');
                break;
            }
        }
        
        const isValid = errors.length === 0;
        
        if (showAlert) {
            let message = isValid ? 'Workflow is valid!' : 'Workflow validation failed:';
            if (errors.length > 0) {
                message += '\n\nErrors:\n' + errors.join('\n');
            }
            if (warnings.length > 0) {
                message += '\n\nWarnings:\n' + warnings.join('\n');
            }
            alert(message);
        }
        
        return { isValid, errors, warnings };
    }
    
    loadWorkflowTemplates() {
        const templates = {
            'brand-analysis': {
                name: 'Brand Analysis Workflow',
                description: 'Complete brand deconstruction analysis',
                nodes: [
                    { type: 'input', x: 100, y: 100, properties: { input_name: 'brand_name', input_type: 'text' } },
                    { type: 'brand-agent', x: 300, y: 100, properties: { analysis_depth: 'comprehensive' } },
                    { type: 'analytics-agent', x: 500, y: 100, properties: { metric_types: ['performance', 'sentiment'] } },
                    { type: 'output', x: 700, y: 100, properties: { output_name: 'analysis_result', output_format: 'json' } }
                ],
                connections: [
                    { from: { nodeId: 'node_0', port: 'output' }, to: { nodeId: 'node_1', port: 'trigger' } },
                    { from: { nodeId: 'node_1', port: 'analysis' }, to: { nodeId: 'node_2', port: 'data' } },
                    { from: { nodeId: 'node_2', port: 'insights' }, to: { nodeId: 'node_3', port: 'input' } }
                ]
            },
            'image-generation': {
                name: 'Image Generation Workflow',
                description: 'Satirical image generation pipeline',
                nodes: [
                    { type: 'input', x: 100, y: 100, properties: { input_name: 'concepts', input_type: 'json' } },
                    { type: 'image-agent', x: 300, y: 100, properties: { image_count: 5, satirical_intensity: 7 } },
                    { type: 'output', x: 500, y: 100, properties: { output_name: 'generated_images', output_format: 'json' } }
                ],
                connections: [
                    { from: { nodeId: 'node_0', port: 'output' }, to: { nodeId: 'node_1', port: 'concepts' } },
                    { from: { nodeId: 'node_1', port: 'images' }, to: { nodeId: 'node_2', port: 'input' } }
                ]
            },
            'campaign-flow': {
                name: 'Campaign Management Flow',
                description: 'Complete campaign workflow with analysis and generation',
                nodes: [
                    { type: 'input', x: 50, y: 100, properties: { input_name: 'campaign_brief', input_type: 'json' } },
                    { type: 'brand-agent', x: 250, y: 50, properties: { analysis_depth: 'standard' } },
                    { type: 'parallel', x: 450, y: 100, properties: { branch_count: 2 } },
                    { type: 'image-agent', x: 650, y: 50, properties: { image_count: 3 } },
                    { type: 'analytics-agent', x: 650, y: 150, properties: { metric_types: ['performance'] } },
                    { type: 'output', x: 850, y: 100, properties: { output_name: 'campaign_results', output_format: 'json' } }
                ],
                connections: [
                    { from: { nodeId: 'node_0', port: 'output' }, to: { nodeId: 'node_1', port: 'trigger' } },
                    { from: { nodeId: 'node_1', port: 'concepts' }, to: { nodeId: 'node_2', port: 'input' } },
                    { from: { nodeId: 'node_2', port: 'branch1' }, to: { nodeId: 'node_3', port: 'concepts' } },
                    { from: { nodeId: 'node_2', port: 'branch2' }, to: { nodeId: 'node_4', port: 'data' } },
                    { from: { nodeId: 'node_3', port: 'images' }, to: { nodeId: 'node_5', port: 'input' } },
                    { from: { nodeId: 'node_4', port: 'insights' }, to: { nodeId: 'node_5', port: 'input' } }
                ]
            }
        };
        
        this.workflowTemplates = templates;
    }
    
    loadTemplate(templateId) {
        if (!templateId || !this.workflowTemplates[templateId]) return;
        
        if (this.nodes.size > 0 && !confirm('Load template? This will clear current workflow.')) {
            document.getElementById('workflowTemplate').value = '';
            return;
        }
        
        const template = this.workflowTemplates[templateId];
        
        this.clearWorkflow();
        
        // Create nodes
        template.nodes.forEach((nodeData, index) => {
            const node = this.createNode(nodeData.type, nodeData.x, nodeData.y, nodeData.properties);
            // Update the node ID to match template expectations
            if (node) {
                this.nodes.delete(node.id);
                node.id = `node_${index}`;
                this.nodes.set(node.id, node);
                
                const nodeElement = document.querySelector(`[data-node-id="${node.id.replace('node_', 'node_')}"]`);
                if (nodeElement) {
                    nodeElement.dataset.nodeId = node.id;
                }
            }
        });
        
        // Create connections
        template.connections.forEach(connData => {
            this.createConnection(connData.from, connData.to);
        });
        
        this.currentWorkflow = {
            id: null,
            name: template.name,
            description: template.description,
            created: new Date().toISOString(),
            modified: new Date().toISOString()
        };
        
        this.updateWorkflowStatus(`Template Loaded: ${template.name}`);
        
        // Reset template selector
        setTimeout(() => {
            document.getElementById('workflowTemplate').value = '';
        }, 100);
    }
    
    handleCanvasClick(e) {
        if (e.target === this.canvas || e.target.classList.contains('canvas-background') || e.target.classList.contains('canvas-grid')) {
            // Clear selection
            document.querySelectorAll('.workflow-node.selected').forEach(node => {
                node.classList.remove('selected');
            });
            this.selectedNode = null;
            document.getElementById('nodeProperties').innerHTML = '<div class="properties-placeholder">Select a component to view its properties</div>';
        }
    }
    
    handleCanvasRightClick(e) {
        e.preventDefault();
        // Could implement context menu here
    }
    
    handleKeyDown(e) {
        if (e.key === 'Delete' && this.selectedNode) {
            this.deleteNode(this.selectedNode);
        } else if (e.key === 'Escape') {
            if (this.isConnecting) {
                this.cancelConnection();
            }
        } else if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 's':
                    e.preventDefault();
                    this.saveWorkflow();
                    break;
                case 'd':
                    e.preventDefault();
                    if (this.selectedNode) {
                        this.duplicateNode(this.selectedNode);
                    }
                    break;
            }
        }
    }
    
    updateComponentCount() {
        const countElement = document.getElementById('componentCount');
        if (countElement) {
            countElement.textContent = this.nodes.size;
        }
    }
    
    updateConnectionCount() {
        const countElement = document.getElementById('connectionCount');
        if (countElement) {
            countElement.textContent = this.connections.size;
        }
    }
    
    updateWorkflowStatus(status) {
        const statusElement = document.getElementById('workflowStatus');
        if (statusElement) {
            statusElement.textContent = status;
        }
    }
}

// Initialize workflow builder when the page loads
let workflowBuilder;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize only if we're on the workflow builder tab
    if (document.getElementById('workflowCanvas')) {
        workflowBuilder = new WorkflowBuilder();
    }
});

// Initialize when tab becomes active
document.addEventListener('tabActivated', function(e) {
    if (e.detail === 'workflow-builder' && !workflowBuilder) {
        workflowBuilder = new WorkflowBuilder();
    }
});
