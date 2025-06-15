
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
