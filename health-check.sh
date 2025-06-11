#!/bin/bash
# Health Check Script for Meld & RAG System
# This script performs comprehensive health checks on all system components

set -e

# Configuration
HEALTH_CHECK_TIMEOUT=10
REDIS_HOST=${REDIS_HOST:-"redis"}
REDIS_PORT=${REDIS_PORT:-6379}
REDIS_PASSWORD=${REDIS_PASSWORD:-}
FLASK_HOST=${FLASK_HOST:-"127.0.0.1"}
FLASK_PORT=${FLASK_PORT:-5001}
# Do NOT set a default for FLASK_SECRET_KEY; fail if not set
if [ -z "$FLASK_SECRET_KEY" ]; then
    echo -e "${RED}[FAIL]${NC} FLASK_SECRET_KEY is not set. Exiting health check."
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Health check results
OVERALL_HEALTH=true
HEALTH_RESULTS=()

# Logging functions
log() {
    echo -e "${BLUE}[HEALTH]${NC} $1"
}

success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    HEALTH_RESULTS+=("✓ $1")
}

failure() {
    echo -e "${RED}[FAIL]${NC} $1"
    HEALTH_RESULTS+=("✗ $1")
    OVERALL_HEALTH=false
}

warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    HEALTH_RESULTS+=("⚠ $1")
}    # Check if running in container
is_container() {
    [ -f /.dockerenv ] || grep -q 'docker\|lxc' /proc/1/cgroup 2>/dev/null
}

# Make sure health check script is executable
check_health_script() {
    if [ -f "/app/health-check.sh" ]; then
        chmod +x /app/health-check.sh
        success "Health check script is available"
        return 0
    else
        failure "Health check script not found"
        return 1
    fi
}

# Check Redis connectivity and health
check_redis() {
    log "Checking Redis connectivity..."
    local redis_cli_cmd=(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT")
    if [ -n "$REDIS_PASSWORD" ]; then
        redis_cli_cmd+=( -a "$REDIS_PASSWORD" )
    fi
    # Try to ping Redis
    if command -v redis-cli >/dev/null 2>&1; then
        if timeout $HEALTH_CHECK_TIMEOUT "${redis_cli_cmd[@]}" ping | grep -q "PONG"; then
            success "Redis is responding to ping"
            # Check Redis info
            local redis_info=$(timeout $HEALTH_CHECK_TIMEOUT "${redis_cli_cmd[@]}" info server | grep "redis_version")
            if [ -n "$redis_info" ]; then
                success "Redis version: $(echo $redis_info | cut -d: -f2)"
            fi
            # Check memory usage
            local memory_info=$(timeout $HEALTH_CHECK_TIMEOUT "${redis_cli_cmd[@]}" info memory | grep "used_memory_human")
            if [ -n "$memory_info" ]; then
                success "Redis memory usage: $(echo $memory_info | cut -d: -f2)"
            fi
        else
            failure "Redis is not responding to ping"
        fi
    else
        warning "redis-cli not available, skipping detailed Redis checks"
        # Try basic network connectivity
        if timeout $HEALTH_CHECK_TIMEOUT nc -z "$REDIS_HOST" "$REDIS_PORT" 2>/dev/null; then
            success "Redis port $REDIS_PORT is accessible"
        else
            failure "Cannot connect to Redis on $REDIS_HOST:$REDIS_PORT"
        fi
    fi
}

# Check Flask application health
check_flask() {
    log "Checking Flask application..."
    
    local health_url="http://$FLASK_HOST:$FLASK_PORT/health"
    
    # Check if Flask is responding
    if command -v curl >/dev/null 2>&1; then
        local response=$(timeout $HEALTH_CHECK_TIMEOUT curl -s -o /dev/null -w "%{http_code}" "$health_url" 2>/dev/null || echo "000")
        
        case $response in
            "200")
                success "Flask health endpoint is responding (HTTP 200)"
                
                # Get detailed health info if available
                local health_data=$(timeout $HEALTH_CHECK_TIMEOUT curl -s "$health_url" 2>/dev/null || echo "{}")
                if echo "$health_data" | grep -q "status"; then
                    success "Flask application reports healthy status"
                fi
                ;;
            "000")
                failure "Cannot connect to Flask application"
                ;;
            *)
                failure "Flask health check failed (HTTP $response)"
                ;;
        esac
    else
        warning "curl not available, trying alternative methods"
        
        # Try with wget if available
        if command -v wget >/dev/null 2>&1; then
            if timeout $HEALTH_CHECK_TIMEOUT wget -q --spider "$health_url" 2>/dev/null; then
                success "Flask application is responding (via wget)"
            else
                failure "Flask application is not responding"
            fi
        else
            # Try basic network connectivity
            if timeout $HEALTH_CHECK_TIMEOUT nc -z "$FLASK_HOST" "$FLASK_PORT" 2>/dev/null; then
                success "Flask port $FLASK_PORT is accessible"
            else
                failure "Cannot connect to Flask on $FLASK_HOST:$FLASK_PORT"
            fi
        fi
    fi
}

# Check file system and volumes
check_filesystem() {
    log "Checking file system and volumes..."
    
    # Check required directories
    local required_dirs=(
        "/app"
        "/app/data"
        "/app/logs"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            success "Directory exists: $dir"
            
            # Check if writable
            if [ -w "$dir" ]; then
                success "Directory is writable: $dir"
            else
                warning "Directory is not writable: $dir"
            fi
        else
            failure "Required directory missing: $dir"
        fi
    done
    
    # Check ChromaDB data directory
    local chromadb_dir="/app/data/chromadb"
    if [ -d "$chromadb_dir" ]; then
        success "ChromaDB data directory exists"
        
        # Check for ChromaDB files
        if find "$chromadb_dir" -name "*.sqlite3" -o -name "*.parquet" | grep -q .; then
            success "ChromaDB data files found"
        else
            warning "No ChromaDB data files found (may be first run)"
        fi
    else
        warning "ChromaDB data directory not found"
    fi
    
    # Check disk space
    local disk_usage=$(df /app 2>/dev/null | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ -n "$disk_usage" ]; then
        if [ "$disk_usage" -lt 90 ]; then
            success "Disk usage is acceptable ($disk_usage%)"
        elif [ "$disk_usage" -lt 95 ]; then
            warning "Disk usage is high ($disk_usage%)"
        else
            failure "Disk usage is critical ($disk_usage%)"
        fi
    fi
}

# Check environment variables
check_environment() {
    log "Checking environment configuration..."
    
    # Required environment variables
    local required_vars=(
        "FLASK_SECRET_KEY"
        "OPENAI_API_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [ "$var" = "FLASK_SECRET_KEY" ] && [ -z "${!var}" ]; then
            failure "Missing required environment variable: FLASK_SECRET_KEY"
            continue
        fi
        if [ -n "${!var}" ]; then
            success "Environment variable set: $var"
        else
            failure "Missing required environment variable: $var"
        fi
    done
    
    # Optional but recommended variables
    local optional_vars=(
        "REDIS_HOST"
        "REDIS_PORT"
        "FLASK_HOST"
        "FLASK_PORT"
    )
    
    for var in "${optional_vars[@]}"; do
        if [ -n "${!var}" ]; then
            success "Optional environment variable set: $var"
        else
            warning "Optional environment variable not set: $var"
        fi
    done
}

# Check Python dependencies
check_dependencies() {
    log "Checking Python dependencies..."
    
    if command -v python3 >/dev/null 2>&1; then
        success "Python 3 is available"
        
        # Check critical packages
        local critical_packages=(
            "flask"
            "redis"
            "openai"
            "chromadb"
        )
        
        for package in "${critical_packages[@]}"; do
            if python3 -c "import $package" 2>/dev/null; then
                local version=$(python3 -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null)
                success "Package available: $package ($version)"
            else
                failure "Missing critical package: $package"
            fi
        done
    else
        failure "Python 3 is not available"
    fi
}

# Check system resources
check_resources() {
    log "Checking system resources..."
    
    # Check memory usage
    if [ -f /proc/meminfo ]; then
        local total_mem=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        local available_mem=$(grep MemAvailable /proc/meminfo | awk '{print $2}' 2>/dev/null || grep MemFree /proc/meminfo | awk '{print $2}')
        
        if [ -n "$total_mem" ] && [ -n "$available_mem" ]; then
            local mem_usage_pct=$((100 - (available_mem * 100 / total_mem)))
            
            if [ "$mem_usage_pct" -lt 80 ]; then
                success "Memory usage is acceptable ($mem_usage_pct%)"
            elif [ "$mem_usage_pct" -lt 90 ]; then
                warning "Memory usage is high ($mem_usage_pct%)"
            else
                failure "Memory usage is critical ($mem_usage_pct%)"
            fi
        fi
    fi
    
    # Check CPU load
    if [ -f /proc/loadavg ]; then
        local load_avg=$(cut -d' ' -f1 /proc/loadavg)
        local cpu_cores=$(nproc 2>/dev/null || echo "1")
        
        if [ -n "$load_avg" ] && [ -n "$cpu_cores" ]; then
            local load_per_core=$(echo "$load_avg $cpu_cores" | awk '{printf "%.2f", $1/$2}')
            
            if (( $(echo "$load_per_core < 0.8" | bc -l 2>/dev/null || echo 0) )); then
                success "CPU load is acceptable ($load_avg on $cpu_cores cores)"
            elif (( $(echo "$load_per_core < 1.0" | bc -l 2>/dev/null || echo 0) )); then
                warning "CPU load is high ($load_avg on $cpu_cores cores)"
            else
                failure "CPU load is critical ($load_avg on $cpu_cores cores)"
            fi
        fi
    fi
}

# Generate health report
generate_report() {
    echo
    echo "==================== HEALTH CHECK REPORT ===================="
    echo "Timestamp: $(date)"
    echo "Host: $(hostname)"
    echo "Container: $(if is_container; then echo "Yes"; else echo "No"; fi)"
    echo
    
    for result in "${HEALTH_RESULTS[@]}"; do
        echo "$result"
    done
    
    echo
    if [ "$OVERALL_HEALTH" = true ]; then
        echo -e "${GREEN}Overall Status: HEALTHY${NC}"
        exit 0
    else
        echo -e "${RED}Overall Status: UNHEALTHY${NC}"
        exit 1
    fi
}

# Main health check function
main() {
    log "Starting comprehensive health check..."
    echo
    
    check_environment
    echo
    
    check_filesystem
    echo
    
    check_dependencies
    echo
    
    check_redis
    echo
    
    check_flask
    echo
    
    check_resources
    echo
    
    generate_report
}

# Run health check
main "$@"
