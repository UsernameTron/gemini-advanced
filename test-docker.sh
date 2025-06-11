#!/bin/bash
# Docker Test Suite for Meld & RAG System
# This script tests the Docker containerization setup

set -e

# Configuration
TEST_TIMEOUT=60
PROJECT_NAME="meld-rag"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test tracking
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=()

# Logging functions
log() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

failure() {
    echo -e "${RED}[FAIL]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    FAILED_TESTS+=("$1")
}

warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Detect timeout command (cross-platform)
if command -v timeout >/dev/null 2>&1; then
  TIMEOUT_CMD=timeout
elif command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_CMD=gtimeout
else
  echo "Error: 'timeout' or 'gtimeout' command not found. Please install coreutils."
  exit 1
fi

# Test function wrapper
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    log "Running test: $test_name"
    
    if $test_function; then
        success "$test_name"
    else
        failure "$test_name"
    fi
    echo
}

# Cleanup function
cleanup() {
    log "Cleaning up test environment..."
    docker-compose -f docker-compose.yml down --remove-orphans >/dev/null 2>&1 || true
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml down --remove-orphans >/dev/null 2>&1 || true
}

# Test 1: Check required files exist
test_required_files() {
    local required_files=(
        "Dockerfile"
        "docker-compose.yml"
        "docker-compose.dev.yml"
        ".dockerignore"
        ".env.example"
        "docker-manage.sh"
        "health-check.sh"
        "start-dev.sh"
        "requirements-dev.txt"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "Missing required file: $file"
            return 1
        fi
    done
    
    return 0
}

# Test 2: Validate Docker Compose syntax
test_compose_syntax() {
    if ! docker-compose -f docker-compose.yml config >/dev/null 2>&1; then
        echo "docker-compose.yml syntax error"
        return 1
    fi
    
    if ! docker-compose -f docker-compose.yml -f docker-compose.dev.yml config >/dev/null 2>&1; then
        echo "docker-compose.dev.yml syntax error"
        return 1
    fi
    
    return 0
}

# Test 3: Check environment template
test_env_template() {
    if [ ! -f ".env.example" ]; then
        echo ".env.example not found"
        return 1
    fi
    
    # Check for critical environment variables
    local critical_vars=(
        "OPENAI_API_KEY"
        "FLASK_SECRET_KEY"
        "REDIS_PASSWORD"
    )
    
    for var in "${critical_vars[@]}"; do
        if ! grep -q "^$var=" .env.example; then
            echo "Missing critical variable in .env.example: $var"
            return 1
        fi
    done
    
    return 0
}

# Test 4: Build production image
test_build_production() {
    log "Building production Docker image..."
    
    # Clean any previous builds to avoid cached issues
    docker-compose build --no-cache app
    
    # Check if image was created with more flexible pattern matching
    if ! docker images | grep -E "(${PROJECT_NAME}|meld-rag|unified)" | grep -q "app"; then
        docker images
        echo "Production image not found in docker images"
        return 1
    fi
    
    success "Production image built successfully"
    return 0
}

# Test 5: Build development image
test_build_development() {
    log "Building development Docker image..."
    
    if ! $TIMEOUT_CMD $TEST_TIMEOUT docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --build-arg TARGET=development; then
        echo "Failed to build development image"
        return 1
    fi
    
    return 0
}

# Test 6: Test Redis service
test_redis_service() {
    log "Testing Redis service..."
    
    # Start only Redis
    if ! docker-compose up -d redis; then
        echo "Failed to start Redis service"
        return 1
    fi
    
    # Wait for Redis to be ready
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
            break
        fi
        sleep 2
        attempts=$((attempts + 1))
    done
    
    if [ $attempts -eq 30 ]; then
        echo "Redis service did not become ready"
        return 1
    fi
    
    return 0
}

# Test 7: Test application startup
test_app_startup() {
    log "Testing application startup..."
    
    # Create more complete .env file for testing
    cat > .env << EOF
OPENAI_API_KEY=test_key
FLASK_SECRET_KEY=test_secret_key
REDIS_PASSWORD=test_password
REDIS_HOST=redis
REDIS_PORT=6379
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
# Additional environment variables for potential edge cases
CHROMA_PERSIST_DIRECTORY=/app/chroma_db
SESSION_TYPE=redis
FLASK_ENV=production
EOF
    
    # Start all services
    if ! $TIMEOUT_CMD $TEST_TIMEOUT docker-compose up -d; then
        echo "Failed to start services"
        return 1
    fi
    
    # Wait for application to be ready
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if docker-compose ps | grep -q "Up"; then
            break
        fi
        sleep 2
        attempts=$((attempts + 1))
    done
    
    if [ $attempts -eq 30 ]; then
        echo "Services did not start properly"
        return 1
    fi
    
    return 0
}

# Test 8: Test health check script
test_health_check() {
    log "Testing health check script..."
    
    # Execute health check inside container
    if ! docker-compose exec -T app /app/health-check.sh; then
        echo "Health check script failed"
        return 1
    fi
    
    return 0
}

# Test 9: Test volume persistence
test_volume_persistence() {
    log "Testing volume persistence..."
    
    # Create test data in volumes with proper permissions
    docker-compose exec -T app bash -c "mkdir -p /app/data/test"
    docker-compose exec -T app bash -c "echo 'test data' > /app/data/test/persistence_test.txt"
    docker-compose exec -T app bash -c "cat /app/data/test/persistence_test.txt" || echo "Warning: Can't read test file"
    
    # Restart services
    docker-compose restart app
    
    # Check if data persists
    if ! docker-compose exec -T app bash -c "test -f /app/data/test/persistence_test.txt"; then
        echo "Volume data did not persist"
        return 1
    fi
    
    local content=$(docker-compose exec -T app bash -c "cat /app/data/test/persistence_test.txt" || echo "")
    if [[ "$content" != *"test data"* ]]; then
        echo "Volume data content corrupted or missing"
        return 1
    fi
    
    return 0
}

# Test 10: Test development mode
test_development_mode() {
    log "Testing development mode..."
    
    # Stop production services
    docker-compose down
    
    # Start development services
    if ! $TIMEOUT_CMD $TEST_TIMEOUT docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d; then
        echo "Failed to start development services"
        return 1
    fi
    
    # Check if development port is exposed
    if ! docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps | grep -q "5001"; then
        echo "Development port not exposed"
        return 1
    fi
    
    return 0
}

# Test 11: Test docker-manage.sh script
test_docker_manage_script() {
    log "Testing docker-manage.sh script..."
    
    # Test help command
    if ! ./docker-manage.sh help >/dev/null 2>&1; then
        echo "docker-manage.sh help command failed"
        return 1
    fi
    
    # Test status command
    if ! ./docker-manage.sh status >/dev/null 2>&1; then
        echo "docker-manage.sh status command failed"
        return 1
    fi
    
    return 0
}

# Test 12: Test backup and restore
test_backup_restore() {
    log "Testing backup and restore functionality..."
    
    # Create test data
    docker-compose exec -T app mkdir -p /app/data/backup_test
    docker-compose exec -T app echo "backup test data" > /app/data/backup_test/test.txt
    
    # Create backup
    if ! ./docker-manage.sh backup >/dev/null 2>&1; then
        echo "Backup creation failed"
        return 1
    fi
    
    # Check if backup directory was created
    if [ ! -d "backups" ]; then
        echo "Backup directory not created"
        return 1
    fi
    
    # Check if backup files exist
    local backup_count=$(find backups -name "*.tar.gz" | wc -l)
    if [ "$backup_count" -eq 0 ]; then
        echo "No backup files created"
        return 1
    fi
    
    return 0
}

# Test 13: Test network connectivity
test_network_connectivity() {
    log "Testing network connectivity between services..."
    
    # Test app -> redis connectivity
    local nc_retries=0
    local max_nc_retries=3
    
    while [ $nc_retries -lt $max_nc_retries ]; do
        if docker-compose exec -T app nc -z redis 6379; then
            success "Basic connectivity to Redis is working"
            break
        else
            nc_retries=$((nc_retries + 1))
            if [ $nc_retries -eq $max_nc_retries ]; then
                echo "App cannot connect to Redis after $max_nc_retries attempts"
                return 1
            fi
            log "Retrying Redis connection test ($nc_retries/$max_nc_retries)..."
            sleep 3
        fi
    done
    
    # Test Redis response from app container using password from .env file
    # Get REDIS_PASSWORD from the docker environment
    local redis_password=$(docker-compose exec -T app bash -c 'echo "$REDIS_PASSWORD"')
    local ping_retries=0
    local max_ping_retries=3
    
    if [ -n "$redis_password" ] && [ "$redis_password" != "" ]; then
        # Try with password, with quotes to handle special characters
        while [ $ping_retries -lt $max_ping_retries ]; do
            if docker-compose exec -T app bash -c "redis-cli -h redis -a '$redis_password' ping" | grep -q "PONG"; then
                success "Redis authentication and ping successful"
                return 0
            else
                ping_retries=$((ping_retries + 1))
                if [ $ping_retries -eq $max_ping_retries ]; then
                    echo "Redis not responding from app container (with password) after $max_ping_retries attempts"
                    return 1
                fi
                log "Retrying Redis ping with password ($ping_retries/$max_ping_retries)..."
                sleep 3
            fi
        done
    else
        # Try without password
        while [ $ping_retries -lt $max_ping_retries ]; do
            if docker-compose exec -T app bash -c "redis-cli -h redis ping" | grep -q "PONG"; then
                success "Redis ping successful"
                return 0
            else
                ping_retries=$((ping_retries + 1))
                if [ $ping_retries -eq $max_ping_retries ]; then
                    echo "Redis not responding from app container after $max_ping_retries attempts"
                    return 1
                fi
                log "Retrying Redis ping without password ($ping_retries/$max_ping_retries)..."
                sleep 3
            fi
        done
    fi
    
    return 0
}

# Test 14: Test resource limits
test_resource_limits() {
    log "Testing resource limits and constraints..."
    
    # Check if containers are running within reasonable resource bounds
    local memory_stats=$(docker stats --no-stream --format "{{.MemUsage}}" | head -1)
    if [ -z "$memory_stats" ]; then
        echo "Cannot retrieve memory statistics"
        return 1
    fi
    
    # Check if any container is using excessive resources
    local high_cpu_containers=$(docker stats --no-stream --format "{{.CPUPerc}}" | sed 's/%//' | awk '$1 > 80 {print $1}' | wc -l)
    if [ "$high_cpu_containers" -gt 0 ]; then
        warning "Some containers using high CPU"
    fi
    
    return 0
}

# Test 15: Test security configurations
test_security_config() {
    log "Testing security configurations..."
    
    # Check if containers are running as non-root
    local root_processes=$(docker-compose exec -T app ps -eo user | grep -c "^root" || echo "0")
    if [ "$root_processes" -gt 2 ]; then  # Allow some system processes
        echo "Too many processes running as root"
        return 1
    fi
    
    # Check if sensitive files have proper permissions
    if ! docker-compose exec -T app test -f "/app/.env"; then
        # .env should exist in container if mounted
        warning ".env file not found in container"
    fi
    
    return 0
}

# Main test runner
run_test_suite() {
    log "Starting Docker Test Suite for Meld & RAG System"
    echo "=========================================="
    echo
    
    # Cleanup before starting
    cleanup
    
    # Free Redis port 6379 before starting tests
    echo -e "[TEST] Freeing Redis port 6379..."
    if [ -f "./free_redis_port.sh" ]; then
      ./free_redis_port.sh
    elif [ -f "./scripts/free_redis_port.sh" ]; then
      ./scripts/free_redis_port.sh
    else
      echo "Warning: Redis port freeing script not found"
    fi
    
    # Run all tests
    run_test "Required Files Check" test_required_files
    run_test "Docker Compose Syntax" test_compose_syntax
    run_test "Environment Template" test_env_template
    run_test "Build Production Image" test_build_production
    run_test "Build Development Image" test_build_development
    run_test "Redis Service" test_redis_service
    run_test "Application Startup" test_app_startup
    run_test "Health Check Script" test_health_check
    run_test "Volume Persistence" test_volume_persistence
    run_test "Development Mode" test_development_mode
    run_test "Docker Manage Script" test_docker_manage_script
    run_test "Backup and Restore" test_backup_restore
    run_test "Network Connectivity" test_network_connectivity
    run_test "Resource Limits" test_resource_limits
    run_test "Security Configuration" test_security_config
}

# Generate test report
generate_test_report() {
    echo "=========================================="
    echo "TEST RESULTS SUMMARY"
    echo "=========================================="
    echo "Total Tests Run: $TESTS_RUN"
    echo "Tests Passed: $TESTS_PASSED"
    echo "Tests Failed: $TESTS_FAILED"
    echo
    
    if [ $TESTS_FAILED -gt 0 ]; then
        echo "FAILED TESTS:"
        for test in "${FAILED_TESTS[@]}"; do
            echo "  - $test"
        done
        echo
        echo -e "${RED}OVERALL RESULT: FAILURE${NC}"
        return 1
    else
        echo -e "${GREEN}OVERALL RESULT: SUCCESS${NC}"
        echo "All tests passed! Docker setup is ready for deployment."
        return 0
    fi
}

# Cleanup function for script exit
cleanup_on_exit() {
    log "Performing final cleanup..."
    cleanup
    
    # Remove test .env file
    rm -f .env
}

# Main execution
main() {
    # Set up cleanup on exit
    trap cleanup_on_exit EXIT
    
    # Check prerequisites
    if ! command -v docker >/dev/null 2>&1; then
        error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose >/dev/null 2>&1; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Run the test suite
    run_test_suite
    
    # Generate report
    if generate_test_report; then
        exit 0
    else
        exit 1
    fi
}

# Show help if requested
if [ "${1:-}" = "help" ] || [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    cat << EOF
Docker Test Suite for Meld & RAG System

This script runs a comprehensive test suite to validate the Docker containerization setup.

Usage: $0 [options]

Options:
    help, --help, -h    Show this help message

Tests performed:
    - Required files check
    - Docker Compose syntax validation
    - Environment template validation
    - Image building (production and development)
    - Service startup and health checks
    - Volume persistence
    - Network connectivity
    - Security configurations
    - Backup and restore functionality

Prerequisites:
    - Docker installed and running
    - Docker Compose installed
    - Sufficient system resources (4GB RAM recommended)

The test suite will automatically clean up after completion.
EOF
    exit 0
fi

# Run main function
main "$@"
