#!/usr/bin/env python3
"""
Production System Monitor
Real-time monitoring for the Unified AI Platform
"""

import asyncio
import json
import time
import psutil
import requests
from datetime import datetime
from pathlib import Path
import os

class ProductionMonitor:
    def __init__(self, base_url="http://127.0.0.1:5001"):
        self.base_url = base_url
        self.metrics = {
            'uptime_start': time.time(),
            'total_requests': 0,
            'api_errors': 0,
            'rate_limit_hits': 0,
            'avg_response_time': 0,
            'system_resources': {},
            'agent_performance': {}
        }
        
    def check_system_health(self):
        """Monitor system resources"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.metrics['system_resources'] = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'timestamp': datetime.now().isoformat()
            }
            
            return True
        except Exception as e:
            print(f"❌ System health check failed: {e}")
            return False
    
    def check_api_health(self):
        """Check API endpoint health"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            self.metrics['total_requests'] += 1
            
            if response.status_code == 200:
                # Update average response time
                current_avg = self.metrics['avg_response_time']
                total_requests = self.metrics['total_requests']
                self.metrics['avg_response_time'] = (
                    (current_avg * (total_requests - 1) + response_time) / total_requests
                )
                return True, response_time
            else:
                self.metrics['api_errors'] += 1
                return False, response_time
                
        except Exception as e:
            self.metrics['api_errors'] += 1
            print(f"❌ API health check failed: {e}")
            return False, 0
    
    def test_agent_performance(self):
        """Test agent response times"""
        agents_to_test = ['research', 'ceo', 'triage']
        
        for agent in agents_to_test:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/agents/{agent}/chat",
                    json={"message": "Hello, brief status check"},
                    timeout=30
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.metrics['agent_performance'][agent] = {
                        'response_time': response_time,
                        'status': 'healthy',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    self.metrics['agent_performance'][agent] = {
                        'response_time': response_time,
                        'status': 'error',
                        'error_code': response.status_code,
                        'timestamp': datetime.now().isoformat()
                    }
                    
            except Exception as e:
                self.metrics['agent_performance'][agent] = {
                    'response_time': 0,
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
    
    def check_rate_limits(self):
        """Monitor OpenAI API rate limit status"""
        try:
            # Check if we have recent rate limit hits
            log_file = Path('production.log')
            if log_file.exists():
                with open(log_file, 'r') as f:
                    recent_logs = f.read()
                    if 'rate_limit' in recent_logs.lower() or '429' in recent_logs:
                        self.metrics['rate_limit_hits'] += 1
        except Exception as e:
            print(f"⚠️ Rate limit check failed: {e}")
    
    def generate_report(self):
        """Generate monitoring report"""
        uptime = time.time() - self.metrics['uptime_start']
        uptime_hours = uptime / 3600
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'uptime_hours': round(uptime_hours, 2),
            'system_status': 'healthy' if self.metrics['api_errors'] < 5 else 'degraded',
            'metrics': self.metrics,
            'alerts': []
        }
        
        # Generate alerts
        if self.metrics['system_resources'].get('cpu_percent', 0) > 80:
            report['alerts'].append('⚠️ High CPU usage detected')
        
        if self.metrics['system_resources'].get('memory_percent', 0) > 85:
            report['alerts'].append('⚠️ High memory usage detected')
        
        if self.metrics['rate_limit_hits'] > 10:
            report['alerts'].append('⚠️ Multiple rate limit hits detected')
        
        if self.metrics['api_errors'] > 10:
            report['alerts'].append('❌ High API error rate detected')
        
        return report
    
    def save_metrics(self):
        """Save metrics to file"""
        report = self.generate_report()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with open(f'production_metrics_{timestamp}.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def print_dashboard(self, report):
        """Print monitoring dashboard"""
        print("\n" + "="*60)
        print("🖥️  UNIFIED AI PLATFORM - PRODUCTION MONITOR")
        print("="*60)
        print(f"📅 Timestamp: {report['timestamp']}")
        print(f"⏰ Uptime: {report['uptime_hours']} hours")
        print(f"🟢 Status: {report['system_status'].upper()}")
        
        print(f"\n📊 SYSTEM RESOURCES:")
        resources = self.metrics['system_resources']
        if resources:
            print(f"  💻 CPU: {resources.get('cpu_percent', 0):.1f}%")
            print(f"  🧠 Memory: {resources.get('memory_percent', 0):.1f}% ({resources.get('memory_available_gb', 0):.1f}GB free)")
            print(f"  💾 Disk: {resources.get('disk_percent', 0):.1f}% ({resources.get('disk_free_gb', 0):.1f}GB free)")
        
        print(f"\n🌐 API METRICS:")
        print(f"  📈 Total Requests: {self.metrics['total_requests']}")
        print(f"  ❌ Errors: {self.metrics['api_errors']}")
        print(f"  ⚡ Avg Response Time: {self.metrics['avg_response_time']:.3f}s")
        print(f"  🚫 Rate Limit Hits: {self.metrics['rate_limit_hits']}")
        
        print(f"\n🤖 AGENT PERFORMANCE:")
        for agent, perf in self.metrics['agent_performance'].items():
            status_emoji = "🟢" if perf['status'] == 'healthy' else "🔴"
            print(f"  {status_emoji} {agent}: {perf['response_time']:.2f}s ({perf['status']})")
        
        if report['alerts']:
            print(f"\n🚨 ALERTS:")
            for alert in report['alerts']:
                print(f"  {alert}")
        else:
            print(f"\n✅ No alerts - system running smoothly")
        
        print("="*60)

async def monitor_loop():
    """Main monitoring loop"""
    monitor = ProductionMonitor()
    
    print("🚀 Starting Production Monitor...")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            # Run all checks
            monitor.check_system_health()
            api_healthy, response_time = monitor.check_api_health()
            monitor.test_agent_performance()
            monitor.check_rate_limits()
            
            # Generate and display report
            report = monitor.generate_report()
            monitor.print_dashboard(report)
            
            # Save metrics every 10 minutes
            if int(time.time()) % 600 == 0:
                monitor.save_metrics()
                print("💾 Metrics saved to file")
            
            # Wait 30 seconds before next check
            await asyncio.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")
        final_report = monitor.save_metrics()
        print(f"📊 Final report saved: production_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

if __name__ == "__main__":
    asyncio.run(monitor_loop())
