# Production Deployment and Monitoring System
# Complete deployment solution with Docker, monitoring, and error handling

import os
import sys
import json
import time
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import yaml
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionDeploymentManager:
    """
    Complete production deployment manager with monitoring and error handling.
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent
        self.deployment_config = {}
        self.monitoring_data = {}
        
    def create_deployment_files(self):
        """Create all necessary deployment files"""
        print("🚀 Creating Production Deployment Files")
        print("=" * 50)
        
        # Create Docker files
        self._create_dockerfile()
        self._create_docker_compose()
        
        # Create configuration files
        self._create_requirements_file()
        self._create_config_yaml()
        
        # Create monitoring files
        self._create_monitoring_script()
        self._create_health_check()
        
        # Create startup scripts
        self._create_startup_script()
        self._create_systemd_service()
        
        print("✅ All deployment files created successfully!")
    
    def _create_dockerfile(self):
        """Create optimized Dockerfile for production"""
        dockerfile_content = '''# Enhanced Brand Deconstruction Engine - Production Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:5000/api/health || exit 1

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "enhanced_web_interface.py"]
'''
        
        dockerfile_path = self.project_root / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        print(f"   ✅ Created: {dockerfile_path}")
    
    def _create_docker_compose(self):
        """Create Docker Compose configuration"""
        compose_content = '''version: '3.8'

services:
  brand-deconstruction:
    build: .
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - FLASK_ENV=production
      - PYTHONPATH=/app
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - brand-deconstruction
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    restart: unless-stopped

volumes:
  redis_data:
  prometheus_data:
  grafana_data:
'''
        
        compose_path = self.project_root / "docker-compose.yml"
        with open(compose_path, 'w') as f:
            f.write(compose_content)
        
        print(f"   ✅ Created: {compose_path}")
    
    def _create_requirements_file(self):
        """Create requirements.txt for production"""
        requirements_content = '''# Production requirements for Enhanced Brand Deconstruction Engine
flask==3.0.0
flask-cors==4.0.0
aiohttp==3.9.1
beautifulsoup4==4.12.2
requests==2.31.0
openai==1.6.1
pyyaml==6.0.1
python-dotenv==1.0.0
gunicorn==21.2.0
redis==5.0.1
psutil==5.9.6
prometheus-client==0.19.0
pillow==10.1.0

# Development and testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0

# Monitoring and logging
structlog==23.2.0
'''
        
        requirements_path = self.project_root / "requirements.txt"
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)
        
        print(f"   ✅ Created: {requirements_path}")
    
    def _create_config_yaml(self):
        """Create production configuration file"""
        config_content = {
            'production': {
                'debug': False,
                'testing': False,
                'api': {
                    'rate_limit': '100/hour',
                    'timeout': 30,
                    'max_concurrent_requests': 10
                },
                'scraping': {
                    'timeout': 30,
                    'retry_attempts': 3,
                    'delay_between_requests': 1,
                    'user_agent_rotation': True
                },
                'image_generation': {
                    'max_images_per_request': 5,
                    'default_resolution': '1024x1024',
                    'quality': 'hd',
                    'cache_duration': 3600
                },
                'monitoring': {
                    'metrics_enabled': True,
                    'logging_level': 'INFO',
                    'health_check_interval': 30,
                    'performance_tracking': True
                },
                'security': {
                    'api_key_required': True,
                    'cors_origins': ['http://localhost:3000', 'https://yourdomain.com'],
                    'max_request_size': '10MB'
                }
            },
            'development': {
                'debug': True,
                'testing': True,
                'api': {
                    'rate_limit': '1000/hour',
                    'timeout': 60
                }
            }
        }
        
        config_path = self.project_root / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config_content, f, default_flow_style=False)
        
        print(f"   ✅ Created: {config_path}")
    
    def _create_monitoring_script(self):
        """Create system monitoring script"""
        monitoring_content = '''#!/usr/bin/env python3
# System Monitoring Script for Brand Deconstruction Engine

import time
import psutil
import requests
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self, service_url="http://localhost:5000"):
        self.service_url = service_url
        self.metrics = []
    
    def check_health(self):
        """Check service health"""
        try:
            response = requests.get(f"{self.service_url}/api/health", timeout=10)
            return response.status_code == 200, response.json()
        except Exception as e:
            return False, {"error": str(e)}
    
    def collect_system_metrics(self):
        """Collect system metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_io": dict(psutil.net_io_counters()._asdict()),
            "process_count": len(psutil.pids())
        }
    
    def monitor_loop(self, interval=60):
        """Main monitoring loop"""
        logger.info("Starting system monitoring...")
        
        while True:
            # Health check
            is_healthy, health_data = self.check_health()
            
            # System metrics
            system_metrics = self.collect_system_metrics()
            
            # Combined metrics
            metrics = {
                "health": {"status": is_healthy, "data": health_data},
                "system": system_metrics
            }
            
            # Log metrics
            logger.info(f"Metrics: CPU {system_metrics['cpu_percent']}%, "
                       f"Memory {system_metrics['memory_percent']}%, "
                       f"Healthy: {is_healthy}")
            
            # Store metrics (in production, send to monitoring system)
            self.metrics.append(metrics)
            
            # Keep only last 100 metrics
            if len(self.metrics) > 100:
                self.metrics = self.metrics[-100:]
            
            time.sleep(interval)

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.monitor_loop()
'''
        
        monitoring_path = self.project_root / "monitor.py"
        with open(monitoring_path, 'w') as f:
            f.write(monitoring_content)
        
        # Make executable
        os.chmod(monitoring_path, 0o755)
        
        print(f"   ✅ Created: {monitoring_path}")
    
    def _create_health_check(self):
        """Create health check script"""
        health_check_content = '''#!/bin/bash
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
'''
        
        health_check_path = self.project_root / "health_check.sh"
        with open(health_check_path, 'w') as f:
            f.write(health_check_content)
        
        # Make executable
        os.chmod(health_check_path, 0o755)
        
        print(f"   ✅ Created: {health_check_path}")
    
    def _create_startup_script(self):
        """Create startup script"""
        startup_content = '''#!/bin/bash
# Startup Script for Enhanced Brand Deconstruction Engine

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_ENV="$PROJECT_ROOT/venv"
LOG_DIR="/var/log/brand-deconstruction"
PID_FILE="/var/run/brand-deconstruction.pid"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

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
        gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 \\
                 --access-logfile "$LOG_DIR/access.log" \\
                 --error-logfile "$LOG_DIR/error.log" \\
                 --pid "$PID_FILE" \\
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
'''
        
        startup_path = self.project_root / "startup.sh"
        with open(startup_path, 'w') as f:
            f.write(startup_content)
        
        # Make executable
        os.chmod(startup_path, 0o755)
        
        print(f"   ✅ Created: {startup_path}")
    
    def _create_systemd_service(self):
        """Create systemd service file"""
        service_content = '''[Unit]
Description=Enhanced Brand Deconstruction Engine
After=network.target
Wants=network.target

[Service]
Type=forking
User=branduser
Group=branduser
WorkingDirectory=/opt/brand-deconstruction
Environment=OPENAI_API_KEY=your_api_key_here
Environment=FLASK_ENV=production
Environment=PYTHONPATH=/opt/brand-deconstruction
ExecStart=/opt/brand-deconstruction/startup.sh start
ExecStop=/opt/brand-deconstruction/startup.sh stop
ExecReload=/opt/brand-deconstruction/startup.sh restart
PIDFile=/var/run/brand-deconstruction.pid
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/log/brand-deconstruction /opt/brand-deconstruction

[Install]
WantedBy=multi-user.target
'''
        
        service_path = self.project_root / "brand-deconstruction.service"
        with open(service_path, 'w') as f:
            f.write(service_content)
        
        print(f"   ✅ Created: {service_path}")
        print(f"      To install: sudo cp {service_path} /etc/systemd/system/")
        print(f"      Then: sudo systemctl enable brand-deconstruction")
    
    def deploy_to_docker(self):
        """Deploy using Docker Compose"""
        print("🐳 Deploying with Docker Compose")
        print("=" * 50)
        
        try:
            # Check if Docker is available
            subprocess.run(['docker', '--version'], check=True, capture_output=True)
            subprocess.run(['docker-compose', '--version'], check=True, capture_output=True)
            
            # Build and start services
            print("   📦 Building Docker images...")
            subprocess.run(['docker-compose', 'build'], cwd=self.project_root, check=True)
            
            print("   🚀 Starting services...")
            subprocess.run(['docker-compose', 'up', '-d'], cwd=self.project_root, check=True)
            
            print("   ✅ Docker deployment successful!")
            print("   🌐 Service available at: http://localhost:5000")
            print("   📊 Grafana dashboard: http://localhost:3000")
            print("   📈 Prometheus metrics: http://localhost:9090")
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Docker deployment failed: {e}")
        except FileNotFoundError:
            print("   ❌ Docker or Docker Compose not found")
    
    def create_nginx_config(self):
        """Create Nginx configuration for reverse proxy"""
        nginx_config = '''events {
    worker_connections 1024;
}

http {
    upstream brand_deconstruction {
        server brand-deconstruction:5000;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    server {
        listen 80;
        server_name your-domain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name your-domain.com;
        
        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_stapling on;
        ssl_stapling_verify on;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;
        
        # Main application
        location / {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://brand_deconstruction;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        # Health check endpoint (no rate limiting)
        location /api/health {
            proxy_pass http://brand_deconstruction;
            access_log off;
        }
        
        # Static files
        location /static/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
'''
        
        nginx_path = self.project_root / "nginx.conf"
        with open(nginx_path, 'w') as f:
            f.write(nginx_config)
        
        print(f"   ✅ Created: {nginx_path}")
    
    def create_monitoring_config(self):
        """Create Prometheus monitoring configuration"""
        prometheus_config = '''global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'brand-deconstruction'
    static_configs:
      - targets: ['brand-deconstruction:5000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
'''
        
        prometheus_path = self.project_root / "prometheus.yml"
        with open(prometheus_path, 'w') as f:
            f.write(prometheus_config)
        
        print(f"   ✅ Created: {prometheus_path}")
    
    def print_deployment_instructions(self):
        """Print complete deployment instructions"""
        instructions = '''
🚀 ENHANCED BRAND DECONSTRUCTION ENGINE - DEPLOYMENT GUIDE
==========================================================

📋 PREREQUISITES:
1. Set OPENAI_API_KEY environment variable
2. Install Docker and Docker Compose (recommended)
   OR Python 3.11+ with pip

🐳 DOCKER DEPLOYMENT (Recommended):
1. Build and deploy:
   docker-compose up -d

2. Check status:
   docker-compose ps

3. View logs:
   docker-compose logs -f brand-deconstruction

4. Access services:
   - Main app: http://localhost:5000
   - Grafana: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090

🛠️ MANUAL DEPLOYMENT:
1. Setup environment:
   ./startup.sh setup

2. Start service:
   ./startup.sh start

3. Check status:
   ./startup.sh status

📊 MONITORING:
- Health checks run automatically every 30s
- Metrics available at /metrics endpoint
- Logs stored in /var/log/brand-deconstruction/
- Use monitoring script: python monitor.py

🔧 PRODUCTION CHECKLIST:
□ Set strong passwords for Grafana
□ Configure SSL certificates in nginx.conf
□ Update domain name in nginx.conf
□ Set up firewall rules
□ Configure log rotation
□ Set up automated backups
□ Test health check and restart procedures

🚨 TROUBLESHOOTING:
- Check logs: docker-compose logs brand-deconstruction
- Restart service: docker-compose restart brand-deconstruction
- Full reset: docker-compose down && docker-compose up -d
- Manual health check: curl http://localhost:5000/api/health

📞 SUPPORT:
- Service logs: /var/log/brand-deconstruction/
- System monitoring: python monitor.py
- Health checks: ./health_check.sh
'''
        
        print(instructions)
        
        # Save to file
        instructions_path = self.project_root / "DEPLOYMENT_INSTRUCTIONS.md"
        with open(instructions_path, 'w') as f:
            f.write(instructions)
        
        print(f"💾 Instructions saved to: {instructions_path}")

def main():
    """Main deployment function"""
    print("🎭 Enhanced Brand Deconstruction Engine - Production Deployment")
    print("=" * 70)
    
    # Get project root
    project_root = Path(__file__).parent
    
    # Initialize deployment manager
    deployment_manager = ProductionDeploymentManager(project_root)
    
    # Create all deployment files
    deployment_manager.create_deployment_files()
    
    # Create additional configuration files
    print(f"\n📊 Creating Additional Configuration Files")
    print("-" * 50)
    deployment_manager.create_nginx_config()
    deployment_manager.create_monitoring_config()
    
    # Print deployment instructions
    print(f"\n📖 Deployment Instructions")
    print("-" * 50)
    deployment_manager.print_deployment_instructions()
    
    # Ask if user wants to deploy now
    print(f"\n🚀 Ready to Deploy!")
    print("-" * 50)
    deploy_now = input("Deploy with Docker now? (y/n): ").lower().strip()
    
    if deploy_now == 'y':
        deployment_manager.deploy_to_docker()
    else:
        print("✅ Deployment files created. Run 'docker-compose up -d' when ready.")

if __name__ == "__main__":
    main()
