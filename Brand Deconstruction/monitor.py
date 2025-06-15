#!/usr/bin/env python3
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
