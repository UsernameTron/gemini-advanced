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

# Stage 4: Production image
FROM application as production

# Install gunicorn for production server
USER root
RUN pip install --no-cache-dir gunicorn[gevent]
USER app

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Wait for Redis if configured\n\
if [ "$REDIS_URL" ]; then\n\
    echo "Waiting for Redis..."\n\
    while ! nc -z redis 6379; do\n\
        sleep 1\n\
    done\n\
    echo "Redis is ready!"\n\
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
    CMD curl -f http://localhost:5001/health || exit 1

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
