#!/bin/bash
# Health Check Script for Brand Deconstruction Engine

SERVICE_URL="http://localhost:5000"
LOG_FILE="/var/log/brand-deconstruction/health.log"
MAX_RETRIES=3
RETRY_DELAY=5

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check service health
check_health() {
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        if curl -s -f "$SERVICE_URL/api/health" > /dev/null 2>&1; then
            log_message "✅ Health check passed"
            return 0
        else
            retry_count=$((retry_count + 1))
            log_message "❌ Health check failed (attempt $retry_count/$MAX_RETRIES)"
            
            if [ $retry_count -lt $MAX_RETRIES ]; then
                sleep $RETRY_DELAY
            fi
        fi
    done
    
    return 1
}

# Function to restart service if unhealthy
restart_service() {
    log_message "🔄 Attempting to restart service..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose restart brand-deconstruction
    elif command -v systemctl &> /dev/null; then
        sudo systemctl restart brand-deconstruction
    else
        log_message "❌ No restart method available"
        return 1
    fi
    
    # Wait for service to start
    sleep 30
    
    # Check if restart was successful
    if check_health; then
        log_message "✅ Service restarted successfully"
        return 0
    else
        log_message "❌ Service restart failed"
        return 1
    fi
}

# Main health check logic
main() {
    log_message "🏥 Starting health check..."
    
    if check_health; then
        exit 0
    else
        log_message "⚠️ Service is unhealthy, attempting restart..."
        
        if restart_service; then
            exit 0
        else
            log_message "🚨 CRITICAL: Service restart failed"
            exit 1
        fi
    fi
}

# Run main function
main "$@"
