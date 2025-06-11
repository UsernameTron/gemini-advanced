# Dockerfile for Unified Meld & RAG System
# Multi-stage build for production-ready containerization

# Stage 1: Base image with Python dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN useradd --create-home --shell /bin/bash app
WORKDIR /app
RUN chown app:app /app

# Stage 2: Dependencies installation
FROM base as dependencies

# Copy requirements first for better caching
COPY VectorDBRAG/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for the unified system
RUN pip install --no-cache-dir \
    flask-session \
    redis \
    chromadb

# Stage 3: Application files
FROM dependencies as application

# Switch to app user
USER app

# Copy application code
COPY --chown=app:app VectorDBRAG/ /app/VectorDBRAG/
COPY --chown=app:app agent_system/ /app/agent_system/
COPY --chown=app:app shared_agents/ /app/shared_agents/
COPY --chown=app:app start_unified_interface.py /app/
COPY --chown=app:app README.md /app/
COPY --chown=app:app UNIFIED_INTERFACE_README.md /app/

# Create necessary directories
RUN mkdir -p /app/chroma_db \
    && mkdir -p /app/flask_session \
    && mkdir -p /app/logs

# Set Python path for imports
ENV PYTHONPATH="/app:/app/VectorDBRAG:/app/agent_system:/app/shared_agents"

# Install networking and health check tools in application stage (for all images)
USER root
RUN apt-get update && apt-get install -y redis-tools ca-certificates netcat-openbsd curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
USER app

# Create required directories for tests with proper permissions
RUN mkdir -p /app/data/test /app/data/backup_test /app/data/chromadb \
    && chown -R app:app /app/data /app/logs /app/chroma_db /app/flask_session
USER app

# Create health check script
USER root
COPY --chown=app:app health-check.sh /app/health-check.sh
RUN chmod +x /app/health-check.sh
USER app

# Stage 4: Production image
FROM application as production

# Install gunicorn for production server
USER root
RUN pip install --no-cache-dir gunicorn[gevent] && \
    apt-get update && \
    apt-get install -y redis-tools ca-certificates netcat-openbsd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
USER app

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Wait for Redis if configured\n\
if [ "$REDIS_URL" ]; then\n\
    echo "Waiting for Redis..."\n\
    timeout=30\n\
    while ! nc -z redis 6379 && [ $timeout -gt 0 ]; do\n\
        sleep 1\n\
        timeout=$((timeout-1))\n\
    done\n\
    if [ $timeout -eq 0 ]; then\n\
        echo "Warning: Redis connection timed out after 30 seconds"\n\
    else\n\
        echo "Redis is reachable!"\n\
    \n\
    # Test Redis connection with password if provided\n\
    if [ "$REDIS_PASSWORD" ]; then\n\
        # Multiple attempts for Redis connection with password\n\
        retry_count=0\n\
        max_retries=5\n\
        while [ $retry_count -lt $max_retries ]; do\n\
            if redis-cli -h redis -a "$REDIS_PASSWORD" ping > /dev/null 2>&1; then\n\
                echo "Redis authentication successful!"\n\
                break\n\
            else\n\
                retry_count=$((retry_count+1))\n\
                if [ $retry_count -eq $max_retries ]; then\n\
                    echo "Warning: Redis auth failed after $max_retries attempts, check REDIS_PASSWORD"\n\
                else\n\
                    echo "Retrying Redis connection ($retry_count/$max_retries)..."\n\
                    sleep 2\n\
                fi\n\
            fi\n\
        done\n\
    else\n\
        # Multiple attempts for Redis connection without password\n\
        retry_count=0\n\
        max_retries=5\n\
        while [ $retry_count -lt $max_retries ]; do\n\
            if redis-cli -h redis ping > /dev/null 2>&1; then\n\
                echo "Redis ping successful!"\n\
                break\n\
            else\n\
                retry_count=$((retry_count+1))\n\
                if [ $retry_count -eq $max_retries ]; then\n\
                    echo "Warning: Redis ping failed after $max_retries attempts"\n\
                else\n\
                    echo "Retrying Redis connection ($retry_count/$max_retries)..."\n\
                    sleep 2\n\
                fi\n\
            fi\n\
        done\n\
    fi\n\
fi\n\
\n\
# Initialize ChromaDB directory\n\
mkdir -p /app/chroma_db\n\
\n\
# Start the unified interface\n\
if [ "$FLASK_ENV" = "development" ]; then\n\
    echo "Starting in development mode..."\n\
    python start_unified_interface.py\n\
else\n\
    echo "Starting in production mode with Gunicorn..."\n\
    cd /app/agent_system\n\
    gunicorn --bind 0.0.0.0:5001 \\\n\
        --workers 4 \\\n\
        --worker-class gevent \\\n\
        --worker-connections 1000 \\\n\
        --timeout 300 \\\n\
        --max-requests 1000 \\\n\
        --max-requests-jitter 50 \\\n\
        --preload \\\n\
        --access-logfile - \\\n\
        --error-logfile - \\\n\
        "web_interface:create_unified_app()"\n\
fi\n\
' > /app/start.sh && chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/health-check.sh || exit 1

# Expose port
EXPOSE 5001

# Set default command
CMD ["/app/start.sh"]

# Stage 5: Development image
FROM application as development

# Install development dependencies
USER root
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    flask-testing \
    ipython \
    jupyter
USER app

# Create development startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting Unified Meld & RAG System in Development Mode..."\n\
echo "Environment: $FLASK_ENV"\n\
echo "Port: 5001"\n\
echo "Features enabled:"\n\
echo "  • 12 Specialized AI Agents"\n\
echo "  • Vector Database Integration (ChromaDB)"\n\
echo "  • Session Management (Redis/Filesystem)"\n\
echo "  • Document Upload & Processing"\n\
echo "  • Real-time Chat Interface"\n\
echo ""\n\
\n\
# Wait for Redis if configured\n\
if [ "$REDIS_URL" ]; then\n\
    echo "Waiting for Redis..."\n\
    timeout=30\n\
    while ! nc -z redis 6379 && [ $timeout -gt 0 ]; do\n\
        sleep 1\n\
        timeout=$((timeout-1))\n\
    done\n\
    if [ $timeout -eq 0 ]; then\n\
        echo "⚠️  Redis not available, using filesystem sessions"\n\
    else\n\
        echo "✅ Redis connected"\n\
    fi\n\
fi\n\
\n\
# Initialize directories\n\
mkdir -p /app/chroma_db /app/flask_session /app/logs\n\
\n\
# Start the application\n\
python /app/start_unified_interface.py\n\
' > /app/start-dev.sh && chmod +x /app/start-dev.sh

# Override command for development
CMD ["/app/start-dev.sh"]
