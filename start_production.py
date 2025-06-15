#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Set production environment
os.environ['FLASK_ENV'] = 'production'
project_root = Path(__file__).parent
os.environ['PYTHONPATH'] = str(project_root)

# Validate required environment variables
required_vars = ['OPENAI_API_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"Missing required environment variables: {missing_vars}")
    sys.exit(1)

sys.path.append(str(project_root))
sys.path.append(str(project_root / 'VectorDBRAG'))
sys.path.append(str(project_root / 'shared_agents'))

from agent_system.web_interface import create_unified_app

if __name__ == '__main__':
    app = create_unified_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
