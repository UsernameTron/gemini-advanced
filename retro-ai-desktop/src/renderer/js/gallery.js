class ImageGallery {
    constructor() {
        this.gallery = document.getElementById('image-gallery');
        this.uploadBtn = document.getElementById('upload-btn');
        this.clearBtn = document.getElementById('clear-gallery');
        this.exportBtn = document.getElementById('export-gallery');
        this.fileInput = document.getElementById('file-input');
        
        this.images = [];
        this.selectedImage = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadGallery();
    }

    setupEventListeners() {
        this.uploadBtn.addEventListener('click', () => this.triggerUpload());
        this.clearBtn.addEventListener('click', () => this.clearGallery());
        this.exportBtn.addEventListener('click', () => this.exportGallery());
        this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
    }

    triggerUpload() {
        this.fileInput.click();
    }

    async handleFileUpload(event) {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        const file = files[0];
        if (!file.type.startsWith('image/')) {
            this.showError('Please select a valid image file.');
            return;
        }

        try {
            this.showLoading('Uploading image...');
            
            const formData = new FormData();
            formData.append('image', file);

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                const sessionId = result.result.sessionId;
                const imagePath = result.result.path;
                
                this.addImage(imagePath, sessionId, {
                    name: file.name,
                    size: file.size,
                    type: 'uploaded'
                });
                
                // Update terminal with session info
                if (window.terminal) {
                    window.terminal.setSessionId(sessionId);
                    window.terminal.addOutput(`
╔══════════════════════════════════════════════════════════════════╗
║                      IMAGE UPLOADED                              ║
╠══════════════════════════════════════════════════════════════════╣
║ FILE: ${file.name.substring(0, 50).padEnd(50)} ║
║ SIZE: ${this.formatFileSize(file.size).padEnd(50)} ║
║ SESSION: ${sessionId.substring(0, 45).padEnd(45)} ║
║                                                                  ║
║ You can now edit this image using:                               ║
║ EDIT ${sessionId} [your edit prompt]                      ║
╚══════════════════════════════════════════════════════════════════╝
                    `, 'system');
                }
                
                this.showSuccess('Image uploaded successfully!');
            } else {
                this.showError(`Upload failed: ${result.error}`);
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showError(`Upload failed: ${error.message}`);
        } finally {
            this.hideLoading();
            // Clear file input
            this.fileInput.value = '';
        }
    }

    addImage(imagePath, sessionId, metadata = {}) {
        const imageData = {
            id: sessionId || this.generateId(),
            path: imagePath,
            sessionId: sessionId,
            timestamp: new Date().toISOString(),
            metadata: metadata
        };

        this.images.unshift(imageData);
        this.renderGallery();
        
        // Remove placeholder if it exists
        const placeholder = this.gallery.querySelector('.gallery-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
    }

    renderGallery() {
        // Clear existing items (except placeholder)
        const items = this.gallery.querySelectorAll('.gallery-item');
        items.forEach(item => item.remove());

        this.images.forEach(image => {
            const item = this.createGalleryItem(image);
            this.gallery.appendChild(item);
        });
    }

    createGalleryItem(imageData) {
        const item = document.createElement('div');
        item.className = 'gallery-item';
        item.dataset.sessionId = imageData.sessionId;

        // For now, create a placeholder since we're dealing with JSON metadata
        // In a real implementation, you'd display actual images
        item.innerHTML = `
            <div class="image-placeholder">
                <div class="placeholder-icon">🖼️</div>
                <div class="placeholder-text">
                    ${imageData.metadata.type || 'Generated'}
                </div>
            </div>
            <div class="gallery-item-info">
                <div class="image-id">ID: ${imageData.id.substring(0, 12)}...</div>
                <div class="image-timestamp">${this.formatTimestamp(imageData.timestamp)}</div>
                ${imageData.metadata.name ? `<div class="image-name">${imageData.metadata.name}</div>` : ''}
            </div>
        `;

        // Add click handler
        item.addEventListener('click', () => this.selectImage(imageData));
        
        // Add context menu
        item.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.showContextMenu(e, imageData);
        });

        return item;
    }

    selectImage(imageData) {
        // Remove previous selection
        const selected = this.gallery.querySelector('.gallery-item.selected');
        if (selected) {
            selected.classList.remove('selected');
        }

        // Select new item
        const item = this.gallery.querySelector(`[data-session-id="${imageData.sessionId}"]`);
        if (item) {
            item.classList.add('selected');
        }

        this.selectedImage = imageData;
        
        // Update terminal session
        if (window.terminal && imageData.sessionId) {
            window.terminal.setSessionId(imageData.sessionId);
            window.terminal.addOutput(`Selected image session: ${imageData.sessionId}`, 'system');
        }
    }

    showContextMenu(event, imageData) {
        // Create context menu
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.innerHTML = `
            <div class="context-item" data-action="edit">Edit Image</div>
            <div class="context-item" data-action="copy-id">Copy Session ID</div>
            <div class="context-item" data-action="export">Export</div>
            <div class="context-item" data-action="delete">Delete</div>
        `;

        menu.style.position = 'fixed';
        menu.style.left = `${event.clientX}px`;
        menu.style.top = `${event.clientY}px`;
        menu.style.zIndex = '2000';

        document.body.appendChild(menu);

        // Handle menu clicks
        menu.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            this.handleContextAction(action, imageData);
            document.body.removeChild(menu);
        });

        // Close menu on outside click
        const closeHandler = (e) => {
            if (!menu.contains(e.target)) {
                document.body.removeChild(menu);
                document.removeEventListener('click', closeHandler);
            }
        };
        
        setTimeout(() => {
            document.addEventListener('click', closeHandler);
        }, 100);
    }

    handleContextAction(action, imageData) {
        switch (action) {
            case 'edit':
                if (window.terminal) {
                    window.terminal.executeCommandProgrammatically(`EDIT ${imageData.sessionId} `);
                }
                break;
                
            case 'copy-id':
                navigator.clipboard.writeText(imageData.sessionId);
                this.showSuccess('Session ID copied to clipboard');
                break;
                
            case 'export':
                this.exportSingleImage(imageData);
                break;
                
            case 'delete':
                this.deleteImage(imageData);
                break;
        }
    }

    clearGallery() {
        if (this.images.length === 0) return;

        if (confirm('Are you sure you want to clear all images from the gallery?')) {
            this.images = [];
            this.selectedImage = null;
            this.renderGallery();
            
            // Show placeholder
            if (this.gallery.children.length === 0) {
                this.showPlaceholder();
            }
            
            this.showSuccess('Gallery cleared');
        }
    }

    async exportGallery() {
        if (this.images.length === 0) {
            this.showError('No images to export');
            return;
        }

        try {
            this.showLoading('Exporting gallery...');
            
            const response = await fetch('/api/gallery');
            const result = await response.json();
            
            if (result.success) {
                // Create and download export file
                const exportData = {
                    timestamp: new Date().toISOString(),
                    totalImages: this.images.length,
                    images: this.images,
                    metadata: {
                        exportedBy: 'Retro AI Desktop',
                        version: '1.0.0'
                    }
                };
                
                this.downloadJSON(exportData, `retro-ai-gallery-${Date.now()}.json`);
                this.showSuccess('Gallery exported successfully');
            } else {
                this.showError(`Export failed: ${result.error}`);
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showError(`Export failed: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    exportSingleImage(imageData) {
        const exportData = {
            timestamp: new Date().toISOString(),
            image: imageData
        };
        
        this.downloadJSON(exportData, `retro-ai-image-${imageData.id}.json`);
        this.showSuccess('Image exported successfully');
    }

    deleteImage(imageData) {
        if (confirm('Are you sure you want to delete this image?')) {
            this.images = this.images.filter(img => img.id !== imageData.id);
            this.renderGallery();
            
            if (this.selectedImage && this.selectedImage.id === imageData.id) {
                this.selectedImage = null;
            }
            
            if (this.images.length === 0) {
                this.showPlaceholder();
            }
            
            this.showSuccess('Image deleted');
        }
    }

    async loadGallery() {
        try {
            const response = await fetch('/api/gallery');
            const result = await response.json();
            
            if (result.success && result.gallery.length > 0) {
                // Load existing gallery from server
                result.gallery.forEach(imagePath => {
                    this.addImage(imagePath, this.generateId(), { type: 'existing' });
                });
            }
        } catch (error) {
            console.error('Failed to load gallery:', error);
        }
    }

    showPlaceholder() {
        if (this.gallery.querySelector('.gallery-placeholder')) return;
        
        const placeholder = document.createElement('div');
        placeholder.className = 'gallery-placeholder';
        placeholder.innerHTML = `
            <div class="placeholder-text">
                ┌─────────────────────┐<br>
                │  GENERATED IMAGES   │<br>
                │  WILL APPEAR HERE   │<br>
                │                     │<br>
                │  TYPE 'GEN' OR      │<br>
                │  'IMAGEN' TO START  │<br>
                └─────────────────────┘
            </div>
        `;
        
        this.gallery.appendChild(placeholder);
    }

    // Utility methods
    generateId() {
        return `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    downloadJSON(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        const details = overlay.querySelector('.loading-details');
        details.textContent = message;
        overlay.classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.add('hidden');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '4px',
            color: '#fff',
            fontSize: '14px',
            fontFamily: 'Source Code Pro, monospace',
            zIndex: '3000',
            maxWidth: '300px',
            wordWrap: 'break-word'
        });

        // Set background color based on type
        switch (type) {
            case 'success':
                notification.style.backgroundColor = '#00ff00';
                notification.style.color = '#000';
                break;
            case 'error':
                notification.style.backgroundColor = '#ff0000';
                break;
            default:
                notification.style.backgroundColor = '#ffaa00';
                notification.style.color = '#000';
        }

        document.body.appendChild(notification);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 3000);
    }
}

// Initialize gallery when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.gallery = new ImageGallery();
});
