#!/usr/bin/env python3
"""
Startup script for the Unified Meld and RAG Web Interface
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main startup function."""
    print("🚀 Starting Unified Meld and RAG Web Interface...")
    
    # Set up environment
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Add paths for imports
    sys.path.insert(0, str(project_root / 'VectorDBRAG'))
    sys.path.insert(0, str(project_root / 'agent_system'))
    
    try:
        # Import and run the unified web interface
        from agent_system.web_interface import create_unified_app
        
        print("✅ Unified system components loaded successfully")
        print("🌐 Starting web server on http://localhost:5000")
        print("📊 Available interfaces:")
        print("   • Main Dashboard: http://localhost:5000")
        print("   • Legacy Agent Dashboard: http://localhost:5000/dashboard")
        print("   • Analytics Dashboard: http://localhost:5000/analytics")
        print("   • Health Check: http://localhost:5000/health")
        print()
        print("🔧 System Features:")
        print("   • 12 Specialized AI Agents")
        print("   • Vector Database Integration")
        print("   • Shared Session Management")
        print("   • Document Upload & Processing")
        print("   • Knowledge Base Search")
        print("   • Real-time Chat Interface")
        print()
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Create and run the app
        app = create_unified_app()
        port = int(os.getenv('FLASK_RUN_PORT', '5002'))
        app.run(debug=True, host='0.0.0.0', port=port)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Attempting to install missing dependencies...")
        
        # Try to install missing dependencies
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask-session", "redis"])
            print("✅ Dependencies installed. Please run the script again.")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please run:")
            print("   pip install flask-session redis")
        
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("\n🔍 Troubleshooting:")
        print("1. Check that your OpenAI API key is set in the .env file")
        print("2. Ensure all dependencies are installed: pip install -r VectorDBRAG/requirements.txt")
        print("3. Check that the VectorDBRAG system is properly configured")
        sys.exit(1)


if __name__ == "__main__":
    main()
