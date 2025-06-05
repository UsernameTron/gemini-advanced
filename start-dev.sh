#!/bin/bash
# Development startup script for the Meld & RAG system
# This script runs in development mode with live reloading and debugging

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[DEV-START]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Wait for Redis to be available
wait_for_redis() {
    log "Waiting for Redis to be available..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if redis-cli -h "${REDIS_HOST:-redis}" -p "${REDIS_PORT:-6379}" ping >/dev/null 2>&1; then
            success "Redis is available"
            return 0
        fi
        
        log "Attempt $attempt/$max_attempts: Redis not ready, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    error "Redis is not available after $max_attempts attempts"
    return 1
}

# Setup development environment
setup_dev_environment() {
    log "Setting up development environment..."
    
    # Create necessary directories
    mkdir -p /app/logs
    mkdir -p /app/data/chromadb
    mkdir -p /app/data/sessions
    
    # Set development environment variables
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    export PYTHONPATH="/app:/app/VectorDBRAG:/app/agent_system:/app/shared_agents"
    
    # Install development dependencies if requirements-dev.txt exists
    if [ -f "/app/requirements-dev.txt" ]; then
        log "Installing development dependencies..."
        pip install -r /app/requirements-dev.txt
    fi
    
    success "Development environment ready"
}

# Start Jupyter notebook server (optional)
start_jupyter() {
    if command -v jupyter >/dev/null 2>&1; then
        log "Starting Jupyter notebook server..."
        jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root \
            --notebook-dir=/app --NotebookApp.token='' --NotebookApp.password='' &
        success "Jupyter notebook available at http://localhost:8888"
    else
        warning "Jupyter not installed, skipping notebook server"
    fi
}

# Run health check
run_health_check() {
    log "Running initial health check..."
    if /app/health-check.sh; then
        success "Health check passed"
    else
        warning "Health check failed, but continuing in development mode"
    fi
}

# Start the Flask application
start_flask_app() {
    log "Starting Flask application in development mode..."
    
    cd /app
    
    # Use Flask development server with auto-reload
    python start_unified_interface.py
}

# Main development startup
main() {
    log "Starting Meld & RAG system in development mode..."
    echo
    
    # Wait for dependencies
    wait_for_redis
    echo
    
    # Setup environment
    setup_dev_environment
    echo
    
    # Start optional services
    start_jupyter
    echo
    
    # Health check
    run_health_check
    echo
    
    # Start main application
    start_flask_app
}

# Handle signals gracefully
trap 'echo "Shutting down development server..."; exit 0' SIGTERM SIGINT

# Run main function
main "$@"
