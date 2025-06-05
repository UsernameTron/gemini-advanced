# Meld & RAG System - Docker Deployment Guide

## Overview

This document provides comprehensive instructions for deploying the unified Meld & RAG system using Docker containers. The system includes:

- **Flask Web Application**: Main interface for the unified system
- **Redis**: Session management and caching
- **ChromaDB**: Vector database for RAG capabilities
- **12 Specialized AI Agents**: Each with vector database integration
- **Development & Production Configurations**: Optimized for different environments

## Prerequisites

### System Requirements
- **Docker**: Version 20.10+ (with BuildKit support)
- **Docker Compose**: Version 2.0+
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: 10GB+ free space for volumes and images
- **OS**: Linux, macOS, or Windows with WSL2

### API Requirements
- **OpenAI API Key**: For AI agent functionality
- **Other AI APIs**: Optional (Anthropic, Google, etc.)

## Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (required)
nano .env  # or your preferred editor
```

**Required Configuration:**
```env
# AI API Keys
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Security
JWT_SECRET_KEY=your_jwt_secret_key
```

### 2. Production Deployment

```bash
# Build production images
./docker-manage.sh build production

# Start services
./docker-manage.sh start production

# Check status
./docker-manage.sh status

# View logs
./docker-manage.sh logs
```

### 3. Development Deployment

```bash
# Build development images
./docker-manage.sh build development

# Start in development mode
./docker-manage.sh start development

# Access development shell
./docker-manage.sh shell
```

## Service Architecture

### Container Services

#### 1. **App Container** (`meld-rag-app`)
- **Base Image**: Python 3.11-slim
- **Purpose**: Main Flask application
- **Ports**: 5000 (production), 5001 (development)
- **Volumes**: 
  - ChromaDB data persistence
  - Session data storage
  - Log files
- **Health Check**: HTTP endpoint monitoring

#### 2. **Redis Container** (`meld-rag-redis`)
- **Base Image**: Redis 7-alpine
- **Purpose**: Session management and caching
- **Ports**: 6379 (internal), exposed in development
- **Volumes**: Persistent data storage
- **Configuration**: Password-protected, optimized settings

### Volume Management

#### Persistent Volumes
- **`chromadb_data`**: Vector database storage
- **`session_data`**: User session files
- **`redis_data`**: Redis persistence
- **`app_logs`**: Application logs

#### Development Volumes
- Source code mounting for live reloading
- Configuration file mounting
- Development tool access

### Network Configuration
- **Internal Network**: `meld-rag-network`
- **Service Discovery**: DNS-based container communication
- **Port Mapping**: Production vs development configurations

## Configuration Management

### Environment Variables

#### Flask Application
```env
# Core Flask Settings
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Session Management
SESSION_TYPE=redis
SESSION_REDIS_HOST=redis
SESSION_REDIS_PORT=6379
SESSION_REDIS_PASSWORD=your_redis_password
PERMANENT_SESSION_LIFETIME=86400

# Security
JWT_SECRET_KEY=your_jwt_secret_key
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

#### AI API Configuration
```env
# OpenAI (Required)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000

# Optional AI Services
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
COHERE_API_KEY=your_cohere_key
```

#### Database & Storage
```env
# ChromaDB Configuration
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_PATH=/app/data/chromadb
COLLECTION_NAME=meld_rag_vectors

# Vector Database Settings
VECTOR_DIMENSION=1536
SIMILARITY_THRESHOLD=0.7
MAX_RESULTS=10
```

#### Performance & Monitoring
```env
# Application Performance
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=120
GUNICORN_KEEPALIVE=5

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/app/logs/app.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5

# Monitoring
HEALTH_CHECK_INTERVAL=30
METRICS_ENABLED=true
PROFILING_ENABLED=false
```

## Operations Guide

### Starting Services

#### Production Mode
```bash
# Full production startup
./docker-manage.sh build production
./docker-manage.sh start production

# Quick restart
./docker-manage.sh restart production
```

#### Development Mode
```bash
# Development with live reloading
./docker-manage.sh build development
./docker-manage.sh start development

# Access Jupyter notebook (port 8888)
# Access Redis directly (port 6379)
```

### Monitoring & Debugging

#### Service Status
```bash
# Overall status
./docker-manage.sh status

# Detailed container information
docker-compose ps -a
docker stats

# Resource usage
docker system df
```

#### Log Management
```bash
# View all logs
./docker-manage.sh logs

# Follow specific service logs
./docker-manage.sh logs app -f
./docker-manage.sh logs redis -f

# Export logs
docker-compose logs > system_logs_$(date +%Y%m%d).log
```

#### Health Checks
```bash
# Automated health check
./docker-manage.sh health

# Manual checks
curl http://localhost:5000/health
redis-cli -h localhost -p 6379 ping
```

### Troubleshooting

#### Common Issues

**1. Container Won't Start**
```bash
# Check container logs
./docker-manage.sh logs app

# Inspect container
docker inspect meld-rag-app

# Check resource usage
docker stats --no-stream
```

**2. Redis Connection Issues**
```bash
# Test Redis connectivity
docker-compose exec app redis-cli -h redis ping

# Check Redis logs
./docker-manage.sh logs redis

# Verify network connectivity
docker-compose exec app nslookup redis
```

**3. ChromaDB Data Issues**
```bash
# Check volume status
docker volume ls | grep chromadb

# Inspect volume
docker volume inspect meld-rag_chromadb_data

# Access container shell
./docker-manage.sh shell app
```

**4. Performance Issues**
```bash
# Monitor resource usage
docker stats

# Check application metrics
curl http://localhost:5000/metrics

# Review configuration
./docker-manage.sh shell app
cat /app/.env
```

## Data Management

### Backup Procedures

#### Automated Backup
```bash
# Create timestamped backup
./docker-manage.sh backup

# Backup created in: ./backups/YYYYMMDD_HHMMSS/
```

#### Manual Backup
```bash
# Create backup directory
mkdir -p backups/manual_$(date +%Y%m%d)

# Backup ChromaDB
docker run --rm -v meld-rag_chromadb_data:/data \
  -v $(pwd)/backups/manual_$(date +%Y%m%d):/backup alpine \
  tar czf /backup/chromadb.tar.gz -C /data .

# Backup Redis
docker run --rm -v meld-rag_redis_data:/data \
  -v $(pwd)/backups/manual_$(date +%Y%m%d):/backup alpine \
  tar czf /backup/redis.tar.gz -C /data .
```

### Restore Procedures

#### From Backup Script
```bash
# Restore from specific backup
./docker-manage.sh restore ./backups/20240101_120000
```

#### Manual Restore
```bash
# Stop services
./docker-manage.sh stop

# Restore volumes
docker run --rm -v meld-rag_chromadb_data:/data \
  -v $(pwd)/backup_path:/backup alpine \
  sh -c "rm -rf /data/* && tar xzf /backup/chromadb.tar.gz -C /data"

# Restart services
./docker-manage.sh start
```

### Volume Migration

#### Export Volumes
```bash
# Export to tarball
docker run --rm -v meld-rag_chromadb_data:/data alpine \
  tar czf - -C /data . > chromadb_export.tar.gz
```

#### Import Volumes
```bash
# Import from tarball
docker volume create meld-rag_chromadb_data
docker run --rm -v meld-rag_chromadb_data:/data alpine \
  sh -c "tar xzf - -C /data" < chromadb_export.tar.gz
```

## Security Considerations

### Container Security

#### 1. **Non-root User**
- Application runs as dedicated `app` user (UID 1000)
- No privileged containers
- Read-only root filesystem where possible

#### 2. **Network Security**
- Internal network isolation
- Minimal port exposure
- Redis password protection

#### 3. **Secret Management**
```bash
# Use Docker secrets for production
echo "your_secret_key" | docker secret create flask_secret -

# Mount secrets in compose
secrets:
  flask_secret:
    external: true
```

### Environment Security

#### 1. **API Key Management**
- Store in `.env` file (not in repository)
- Use environment-specific configurations
- Rotate keys regularly

#### 2. **File Permissions**
```bash
# Secure environment file
chmod 600 .env

# Secure backup directory
chmod 700 backups/
```

#### 3. **Network Policies**
- Implement firewall rules
- Use reverse proxy (nginx/traefik)
- Enable HTTPS in production

## Production Deployment

### Infrastructure Requirements

#### Minimum Hardware
- **CPU**: 2 cores
- **Memory**: 4GB RAM
- **Storage**: 20GB SSD
- **Network**: 100Mbps

#### Recommended Hardware
- **CPU**: 4+ cores
- **Memory**: 8GB+ RAM
- **Storage**: 50GB+ SSD
- **Network**: 1Gbps

### Production Optimizations

#### 1. **Resource Limits**
```yaml
# docker-compose.prod.yml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

#### 2. **Health Monitoring**
```bash
# Set up monitoring
docker-compose exec app curl -f http://localhost:5000/health || exit 1

# Configure alerts
# Use external monitoring (Prometheus, Grafana)
```

#### 3. **Scaling Configuration**
```yaml
# Horizontal scaling
services:
  app:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
```

### Reverse Proxy Setup

#### Nginx Configuration
```nginx
upstream meld_rag_app {
    server localhost:5000;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://meld_rag_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Maintenance

### Regular Tasks

#### Daily
- Check service status
- Monitor resource usage
- Review error logs

#### Weekly
- Create data backups
- Update security patches
- Clean unused images

#### Monthly
- Full system backup
- Performance review
- Configuration audit

### Update Procedures

#### Application Updates
```bash
# Build new images
./docker-manage.sh build production

# Rolling update
docker-compose up -d --no-deps app

# Verify deployment
./docker-manage.sh health
```

#### System Updates
```bash
# Update base images
docker-compose pull

# Rebuild with updates
./docker-manage.sh build production

# Restart services
./docker-manage.sh restart production
```

## Support & Troubleshooting

### Getting Help

#### Log Analysis
- Check application logs: `./docker-manage.sh logs app`
- Monitor system resources: `./docker-manage.sh status`
- Verify configuration: `./docker-manage.sh shell app`

#### Common Solutions
- **Performance**: Increase container resources
- **Connectivity**: Check network configuration
- **Data**: Verify volume mounts and permissions

#### Emergency Procedures
- **Service Down**: `./docker-manage.sh restart`
- **Data Corruption**: Restore from backup
- **Security Issue**: Stop services, investigate, patch

### Contact Information
- **Documentation**: This README and inline comments
- **Issues**: Check Docker and application logs
- **Updates**: Monitor container and dependency updates

---

**Version**: 1.0  
**Last Updated**: 2024  
**Maintainer**: Meld & RAG System Team
