#!/bin/bash
# Startup Script for Enhanced Brand Deconstruction Engine

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_ENV="$PROJECT_ROOT/venv"
LOG_DIR="/var/log/brand-deconstruction"
PID_FILE="/var/run/brand-deconstruction.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check requirements
check_requirements() {
    print_status "Checking requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check OpenAI API key
    if [ -z "$OPENAI_API_KEY" ]; then
        print_error "OPENAI_API_KEY environment variable is required"
        exit 1
    fi
    
    print_status "✅ Requirements check passed"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Create log directory
    sudo mkdir -p "$LOG_DIR"
    sudo chown $USER:$USER "$LOG_DIR"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$PYTHON_ENV" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv "$PYTHON_ENV"
    fi
    
    # Activate virtual environment
    source "$PYTHON_ENV/bin/activate"
    
    # Install/update dependencies
    print_status "Installing dependencies..."
    pip install -r "$PROJECT_ROOT/requirements.txt"
    
    print_status "✅ Environment setup complete"
}

# Function to start the service
start_service() {
    print_status "Starting Brand Deconstruction Engine..."
    
    cd "$PROJECT_ROOT"
    source "$PYTHON_ENV/bin/activate"
    
    # Start with gunicorn for production
    if [ "$NODE_ENV" = "production" ]; then
        gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 \
                 --access-logfile "$LOG_DIR/access.log" \
                 --error-logfile "$LOG_DIR/error.log" \
                 --pid "$PID_FILE" \
                 enhanced_web_interface:app &
    else
        python enhanced_web_interface.py > "$LOG_DIR/app.log" 2>&1 &
        echo $! > "$PID_FILE"
    fi
    
    print_status "✅ Service started successfully (PID: $(cat $PID_FILE))"
}

# Function to stop the service
stop_service() {
    print_status "Stopping Brand Deconstruction Engine..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            rm -f "$PID_FILE"
            print_status "✅ Service stopped successfully"
        else
            print_warning "Service was not running"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "PID file not found"
    fi
}

# Function to check service status
check_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            print_status "✅ Service is running (PID: $PID)"
            
            # Check health endpoint
            if curl -s -f http://localhost:5000/api/health > /dev/null 2>&1; then
                print_status "✅ Health check passed"
            else
                print_warning "⚠️ Health check failed"
            fi
        else
            print_error "❌ Service is not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        print_error "❌ Service is not running"
    fi
}

# Main script logic
main() {
    case "$1" in
        start)
            check_requirements
            setup_environment
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            stop_service
            sleep 2
            check_requirements
            setup_environment
            start_service
            ;;
        status)
            check_status
            ;;
        setup)
            check_requirements
            setup_environment
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status|setup}"
            echo ""
            echo "Commands:"
            echo "  start   - Start the service"
            echo "  stop    - Stop the service"
            echo "  restart - Restart the service"
            echo "  status  - Check service status"
            echo "  setup   - Setup environment only"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
