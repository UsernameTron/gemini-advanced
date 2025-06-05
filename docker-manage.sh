#!/bin/bash
# Docker Management Script for Meld & RAG System
# Usage: ./docker-manage.sh [command] [options]

set -e

PROJECT_NAME="meld-rag"
DOCKER_COMPOSE_FILES="-f docker-compose.yml"
DEV_COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker and Docker Compose are installed
check_dependencies() {
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
}

# Build containers
build() {
    local target=${1:-production}
    log "Building Docker images for target: $target"
    
    if [ "$target" = "dev" ] || [ "$target" = "development" ]; then
        docker-compose $DEV_COMPOSE_FILES build --build-arg TARGET=development
    else
        docker-compose $DOCKER_COMPOSE_FILES build --build-arg TARGET=production
    fi
    success "Build completed"
}

# Start services
start() {
    local mode=${1:-production}
    
    if [ "$mode" = "dev" ] || [ "$mode" = "development" ]; then
        log "Starting services in development mode"
        docker-compose $DEV_COMPOSE_FILES up -d
    else
        log "Starting services in production mode"
        docker-compose $DOCKER_COMPOSE_FILES up -d
    fi
    
    log "Waiting for services to be ready..."
    sleep 5
    
    # Check service health
    check_health
    success "Services started successfully"
}

# Stop services
stop() {
    log "Stopping services"
    docker-compose $DOCKER_COMPOSE_FILES down
    success "Services stopped"
}

# Restart services
restart() {
    local mode=${1:-production}
    log "Restarting services"
    stop
    start "$mode"
}

# Show logs
logs() {
    local service=${1:-""}
    local follow=${2:-false}
    
    if [ "$follow" = "true" ] || [ "$follow" = "-f" ]; then
        if [ -n "$service" ]; then
            docker-compose $DOCKER_COMPOSE_FILES logs -f "$service"
        else
            docker-compose $DOCKER_COMPOSE_FILES logs -f
        fi
    else
        if [ -n "$service" ]; then
            docker-compose $DOCKER_COMPOSE_FILES logs --tail=100 "$service"
        else
            docker-compose $DOCKER_COMPOSE_FILES logs --tail=100
        fi
    fi
}

# Show service status
status() {
    log "Service status:"
    docker-compose $DOCKER_COMPOSE_FILES ps
    
    log "Container resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Health check
check_health() {
    log "Checking service health..."
    
    # Check Redis
    if docker-compose $DOCKER_COMPOSE_FILES exec -T redis redis-cli ping | grep -q "PONG"; then
        success "Redis is healthy"
    else
        error "Redis is not responding"
        return 1
    fi
    
    # Check Flask app
    local app_health=$(docker-compose $DOCKER_COMPOSE_FILES exec -T app curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health || echo "000")
    if [ "$app_health" = "200" ]; then
        success "Flask app is healthy"
    else
        warning "Flask app health check failed (HTTP $app_health)"
    fi
}

# Clean up
cleanup() {
    local level=${1:-basic}
    
    case $level in
        "basic")
            log "Basic cleanup - removing stopped containers"
            docker-compose $DOCKER_COMPOSE_FILES down --remove-orphans
            docker system prune -f
            ;;
        "full")
            log "Full cleanup - removing all containers, networks, and unused images"
            docker-compose $DOCKER_COMPOSE_FILES down --remove-orphans --volumes
            docker system prune -a -f
            warning "All data volumes have been removed!"
            ;;
        "images")
            log "Removing project images"
            docker-compose $DOCKER_COMPOSE_FILES down
            docker rmi $(docker images "${PROJECT_NAME}*" -q) 2>/dev/null || true
            ;;
    esac
    success "Cleanup completed"
}

# Backup volumes
backup() {
    local backup_dir="./backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    log "Creating backup in $backup_dir"
    
    # Backup ChromaDB data
    docker run --rm -v "${PROJECT_NAME}_chromadb_data:/data" -v "$(pwd)/$backup_dir:/backup" alpine \
        tar czf /backup/chromadb_data.tar.gz -C /data .
    
    # Backup session data
    docker run --rm -v "${PROJECT_NAME}_session_data:/data" -v "$(pwd)/$backup_dir:/backup" alpine \
        tar czf /backup/session_data.tar.gz -C /data .
    
    # Backup Redis data
    docker run --rm -v "${PROJECT_NAME}_redis_data:/data" -v "$(pwd)/$backup_dir:/backup" alpine \
        tar czf /backup/redis_data.tar.gz -C /data .
    
    success "Backup created in $backup_dir"
}

# Restore volumes
restore() {
    local backup_path=$1
    
    if [ -z "$backup_path" ]; then
        error "Please provide backup path"
        echo "Usage: $0 restore /path/to/backup/directory"
        exit 1
    fi
    
    if [ ! -d "$backup_path" ]; then
        error "Backup directory does not exist: $backup_path"
        exit 1
    fi
    
    log "Restoring from $backup_path"
    warning "This will overwrite existing data. Continue? (y/N)"
    read -r confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log "Restore cancelled"
        exit 0
    fi
    
    # Stop services
    docker-compose $DOCKER_COMPOSE_FILES down
    
    # Restore ChromaDB data
    if [ -f "$backup_path/chromadb_data.tar.gz" ]; then
        docker run --rm -v "${PROJECT_NAME}_chromadb_data:/data" -v "$backup_path:/backup" alpine \
            sh -c "rm -rf /data/* && tar xzf /backup/chromadb_data.tar.gz -C /data"
    fi
    
    # Restore session data
    if [ -f "$backup_path/session_data.tar.gz" ]; then
        docker run --rm -v "${PROJECT_NAME}_session_data:/data" -v "$backup_path:/backup" alpine \
            sh -c "rm -rf /data/* && tar xzf /backup/session_data.tar.gz -C /data"
    fi
    
    # Restore Redis data
    if [ -f "$backup_path/redis_data.tar.gz" ]; then
        docker run --rm -v "${PROJECT_NAME}_redis_data:/data" -v "$backup_path:/backup" alpine \
            sh -c "rm -rf /data/* && tar xzf /backup/redis_data.tar.gz -C /data"
    fi
    
    success "Restore completed"
}

# Development shell
shell() {
    local service=${1:-app}
    log "Opening shell in $service container"
    docker-compose $DOCKER_COMPOSE_FILES exec "$service" /bin/bash
}

# Show help
show_help() {
    cat << EOF
Docker Management Script for Meld & RAG System

Usage: $0 [command] [options]

Commands:
    build [target]          Build Docker images (target: production|development)
    start [mode]           Start services (mode: production|development)
    stop                   Stop all services
    restart [mode]         Restart services
    logs [service] [-f]    Show logs (optional: specific service and follow)
    status                 Show service status and resource usage
    health                 Check service health
    cleanup [level]        Clean up (level: basic|full|images)
    backup                 Backup all volumes
    restore [path]         Restore from backup
    shell [service]        Open shell in container (default: app)
    help                   Show this help message

Examples:
    $0 build development
    $0 start dev
    $0 logs app -f
    $0 cleanup full
    $0 backup
    $0 restore ./backups/20240101_120000

Environment:
    Copy .env.example to .env and configure before starting services.
EOF
}

# Main command dispatcher
main() {
    check_dependencies
    
    case ${1:-help} in
        "build")
            build "$2"
            ;;
        "start")
            start "$2"
            ;;
        "stop")
            stop
            ;;
        "restart")
            restart "$2"
            ;;
        "logs")
            logs "$2" "$3"
            ;;
        "status")
            status
            ;;
        "health")
            check_health
            ;;
        "cleanup")
            cleanup "$2"
            ;;
        "backup")
            backup
            ;;
        "restore")
            restore "$2"
            ;;
        "shell")
            shell "$2"
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
