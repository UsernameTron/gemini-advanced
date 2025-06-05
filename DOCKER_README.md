# Docker Setup for Meld & RAG System

## Quick Start

### 1. Environment Setup
```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 2. Production Deployment
```bash
# Build and start services
./docker-manage.sh build production
./docker-manage.sh start production

# Check status
./docker-manage.sh status
```

### 3. Development Mode
```bash
# Build and start in development mode
./docker-manage.sh build development
./docker-manage.sh start development
```

## System Architecture

### Services
- **App Container**: Flask web application with AI agents
- **Redis Container**: Session management and caching
- **Volumes**: Persistent storage for ChromaDB, sessions, and logs

### Ports
- **5000**: Production Flask app
- **5001**: Development Flask app  
- **6379**: Redis (development only)
- **8888**: Jupyter notebook (development only)

## Management Scripts

### docker-manage.sh
```bash
./docker-manage.sh build [production|development]
./docker-manage.sh start [production|development]
./docker-manage.sh stop
./docker-manage.sh restart [mode]
./docker-manage.sh logs [service] [-f]
./docker-manage.sh status
./docker-manage.sh health
./docker-manage.sh backup
./docker-manage.sh restore [backup_path]
./docker-manage.sh cleanup [basic|full|images]
./docker-manage.sh shell [service]
```

### Test Suite
```bash
# Run comprehensive Docker tests
./test-docker.sh
```

### Health Monitoring
```bash
# Run health checks
./health-check.sh
```

## Data Management

### Backup
```bash
# Automated backup with timestamp
./docker-manage.sh backup

# Backup location: ./backups/YYYYMMDD_HHMMSS/
```

### Restore
```bash
# Restore from backup
./docker-manage.sh restore ./backups/20240101_120000
```

### Volume Information
- `chromadb_data`: Vector database storage
- `session_data`: User session files  
- `redis_data`: Redis persistence
- `app_logs`: Application logs

## Configuration

### Required Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
REDIS_PASSWORD=your_redis_password
```

### Optional Configuration
```env
# Flask settings
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_ENV=production

# Redis settings
REDIS_HOST=redis
REDIS_PORT=6379

# AI settings
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000

# Performance
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
```

## Development Features

### Live Code Reloading
Development mode mounts source code for instant updates.

### Jupyter Notebooks
Available at `http://localhost:8888` in development mode.

### Debug Tools
- Interactive debugging with pdb++
- Memory profiling tools
- Code quality tools (black, flake8, pylint)

### Development Dependencies
Additional packages in `requirements-dev.txt`:
- Testing: pytest, pytest-cov
- Code quality: black, isort, flake8
- Debugging: ipdb, memory-profiler
- Documentation: sphinx

## Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check logs
./docker-manage.sh logs

# Verify environment
cat .env

# Test connectivity
./docker-manage.sh health
```

**Redis connection issues:**
```bash
# Check Redis status
./docker-manage.sh logs redis

# Test from app container
./docker-manage.sh shell app
redis-cli -h redis ping
```

**Performance issues:**
```bash
# Monitor resources
./docker-manage.sh status

# Check container stats
docker stats
```

**Data persistence issues:**
```bash
# Check volumes
docker volume ls

# Inspect volume
docker volume inspect meld-rag_chromadb_data
```

### Clean Start
```bash
# Stop all services
./docker-manage.sh stop

# Full cleanup (removes data!)
./docker-manage.sh cleanup full

# Rebuild and restart
./docker-manage.sh build production
./docker-manage.sh start production
```

## Security

### Best Practices
- Use strong passwords in `.env`
- Keep `.env` file secure (not in git)
- Regularly update base images
- Monitor container resources
- Use health checks

### Production Hardening
- Set resource limits
- Use reverse proxy (nginx)
- Enable HTTPS
- Implement monitoring
- Regular security updates

## Monitoring

### Health Checks
```bash
# Application health
curl http://localhost:5000/health

# Redis health  
redis-cli ping

# Comprehensive check
./health-check.sh
```

### Logs
```bash
# Real-time logs
./docker-manage.sh logs -f

# Service-specific logs
./docker-manage.sh logs app
./docker-manage.sh logs redis

# Export logs
docker-compose logs > system_logs.txt
```

### Metrics
```bash
# Container statistics
docker stats

# System resources
docker system df

# Service status
./docker-manage.sh status
```

## File Structure

```
├── Dockerfile                 # Multi-stage Docker build
├── docker-compose.yml         # Production orchestration
├── docker-compose.dev.yml     # Development overrides
├── .dockerignore              # Build context exclusions
├── .env.example               # Environment template
├── docker-manage.sh           # Management script
├── health-check.sh            # Health monitoring
├── start-dev.sh              # Development startup
├── test-docker.sh            # Test suite
├── requirements-dev.txt      # Development dependencies
└── DOCKER_DEPLOYMENT.md      # Detailed documentation
```

## Support

### Documentation
- `DOCKER_DEPLOYMENT.md`: Comprehensive deployment guide
- Inline script comments
- Container health endpoints

### Debugging
- Use `./docker-manage.sh shell` for container access
- Check logs with `./docker-manage.sh logs`
- Run health checks with `./health-check.sh`
- Test setup with `./test-docker.sh`

### Updates
- Rebuild images: `./docker-manage.sh build`
- Update dependencies: Edit requirements files and rebuild
- Version updates: Pull new base images and rebuild

---

For detailed information, see `DOCKER_DEPLOYMENT.md`.
