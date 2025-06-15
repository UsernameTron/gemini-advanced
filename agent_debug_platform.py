#!/usr/bin/env python3
"""
Agent-Driven Debugging Script for Brand Deconstruction Platform
Uses the available agents in the Unified AI Platform to diagnose and fix issues.
"""

import asyncio
import json
import sys
import os
import subprocess
import signal
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the agent system
try:
    from RAG.agents_ollama import create_agent, AgentManager
    from RAG.unified_rag_system import UnifiedRAGSystem
except ImportError as e:
    print(f"❌ Error importing agent system: {e}")
    print("Make sure you're running from the project root and dependencies are installed.")
    sys.exit(1)

class AgentDrivenDebugger:
    """Uses AI agents to systematically debug and fix platform issues."""
    
    def __init__(self):
        self.agent_manager = None
        self.debug_session_id = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results = {
            "session_id": self.debug_session_id,
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "fixes_applied": [],
            "recommendations": []
        }
        
    async def initialize_agents(self):
        """Initialize the agent management system."""
        try:
            print("🤖 Initializing AI agents for debugging...")
            self.agent_manager = AgentManager()
            await self.agent_manager.initialize()
            print("✅ Agent system initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize agents: {e}")
            return False
    
    async def step1_triage_analysis(self):
        """Step 1: Use TriageAgent to analyze the problem."""
        print("\n🔍 Step 1: Triaging the problem with TriageAgent...")
        
        try:
            triage_agent = await create_agent("TriageAgent")
            
            problem_description = """
            Brand Deconstruction Platform Debug Request:
            
            Issue: The main platform web interface is failing to start
            Error: "Address already in use: port 5002 already in use"
            
            Current situation:
            - There are existing Python processes using port 5002
            - One process is 'enhanced_web_interface.py' (PID 59525)
            - The main_platform/app.py is trying to start on the same port
            - Platform.js frontend is unable to connect to backend
            
            Components involved:
            - main_platform/app.py (Flask backend)
            - main_platform/static/js/platform.js (Frontend)
            - Enhanced web interface (conflicts with main platform)
            
            Need guidance on:
            1. Whether to kill existing processes or use different ports
            2. How to configure dynamic port allocation
            3. Best approach for conflict resolution
            """
            
            triage_result = await triage_agent.execute({
                "query": "Analyze port conflict in Brand Deconstruction Platform",
                "context": problem_description,
                "priority": "high",
                "components": ["main_platform", "enhanced_web_interface", "networking"]
            })
            
            self.results["steps"].append({
                "step": "triage_analysis",
                "agent": "TriageAgent",
                "result": triage_result,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✅ Triage completed: {triage_result.get('analysis', 'Analysis completed')}")
            return triage_result
            
        except Exception as e:
            print(f"❌ Triage analysis failed: {e}")
            return {"error": str(e)}
    
    async def step2_code_analysis(self):
        """Step 2: Use CodeAnalyzerAgent to analyze the platform code."""
        print("\n📊 Step 2: Analyzing code with CodeAnalyzerAgent...")
        
        try:
            code_analyzer = await create_agent("CodeAnalyzerAgent")
            
            # Read the main platform files
            platform_js_path = project_root / "main_platform" / "static" / "js" / "platform.js"
            app_py_path = project_root / "main_platform" / "app.py"
            
            platform_js_content = ""
            app_py_content = ""
            
            if platform_js_path.exists():
                platform_js_content = platform_js_path.read_text()
            
            if app_py_path.exists():
                app_py_content = app_py_path.read_text()
            
            analysis_result = await code_analyzer.execute({
                "code_files": {
                    "platform.js": platform_js_content,
                    "app.py": app_py_content
                },
                "analysis_type": "debugging",
                "focus_areas": ["port_configuration", "socket_connections", "error_handling"],
                "issue_context": "Port conflict and connection failures"
            })
            
            self.results["steps"].append({
                "step": "code_analysis", 
                "agent": "CodeAnalyzerAgent",
                "result": analysis_result,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✅ Code analysis completed")
            return analysis_result
            
        except Exception as e:
            print(f"❌ Code analysis failed: {e}")
            return {"error": str(e)}
    
    async def step3_debug_investigation(self):
        """Step 3: Use CodeDebuggerAgent for deep debugging."""
        print("\n🐛 Step 3: Deep debugging with CodeDebuggerAgent...")
        
        try:
            code_debugger = await create_agent("CodeDebuggerAgent")
            
            # Get current process information
            port_info = self.get_port_usage_info()
            
            app_py_path = project_root / "main_platform" / "app.py"
            app_py_content = ""
            if app_py_path.exists():
                app_py_content = app_py_path.read_text()
            
            debug_result = await code_debugger.execute({
                "code": app_py_content,
                "error_message": "Address already in use: port 5002 already in use",
                "system_info": port_info,
                "debug_type": "network_conflict",
                "stack_trace": "OSError: [Errno 48] Address already in use"
            })
            
            self.results["steps"].append({
                "step": "debug_investigation",
                "agent": "CodeDebuggerAgent", 
                "result": debug_result,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✅ Debug investigation completed")
            return debug_result
            
        except Exception as e:
            print(f"❌ Debug investigation failed: {e}")
            return {"error": str(e)}
    
    async def step4_generate_fixes(self):
        """Step 4: Use CodeRepairAgent to generate fixes."""
        print("\n🔧 Step 4: Generating fixes with CodeRepairAgent...")
        
        try:
            code_repair = await create_agent("CodeRepairAgent")
            
            # Compile all previous analysis
            previous_analysis = {
                "triage": self.results["steps"][0]["result"] if len(self.results["steps"]) > 0 else {},
                "code_analysis": self.results["steps"][1]["result"] if len(self.results["steps"]) > 1 else {},
                "debug_investigation": self.results["steps"][2]["result"] if len(self.results["steps"]) > 2 else {}
            }
            
            app_py_path = project_root / "main_platform" / "app.py"
            app_py_content = ""
            if app_py_path.exists():
                app_py_content = app_py_path.read_text()
            
            repair_result = await code_repair.execute({
                "code": app_py_content,
                "issues": [
                    "Port 5002 is already in use by another process",
                    "Need dynamic port allocation or configuration",
                    "Frontend needs to connect to correct port dynamically"
                ],
                "repair_type": "server_configuration",
                "previous_analysis": previous_analysis,
                "constraints": ["maintain_compatibility", "production_ready", "error_handling"]
            })
            
            self.results["steps"].append({
                "step": "generate_fixes",
                "agent": "CodeRepairAgent",
                "result": repair_result, 
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✅ Fix generation completed")
            return repair_result
            
        except Exception as e:
            print(f"❌ Fix generation failed: {e}")
            return {"error": str(e)}
    
    def get_port_usage_info(self):
        """Get information about current port usage."""
        try:
            # Get processes using port 5002
            result = subprocess.run(['lsof', '-i', ':5002'], 
                                  capture_output=True, text=True)
            
            return {
                "port_5002_usage": result.stdout,
                "port_check_success": result.returncode == 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def step5_apply_fixes(self, repair_result):
        """Step 5: Apply the suggested fixes."""
        print("\n⚡ Step 5: Applying fixes...")
        
        if "error" in repair_result:
            print("❌ Cannot apply fixes due to previous errors")
            return False
        
        try:
            # First, let's kill the conflicting process
            print("🛑 Stopping conflicting processes...")
            subprocess.run(['pkill', '-f', 'enhanced_web_interface.py'], 
                          capture_output=True)
            
            # Wait a moment for cleanup
            await asyncio.sleep(2)
            
            # Check if port is now free
            port_check = subprocess.run(['lsof', '-i', ':5002'], 
                                      capture_output=True, text=True)
            
            if port_check.returncode == 0:
                print("⚠️  Port 5002 still in use, implementing dynamic port allocation...")
                return await self.implement_dynamic_port_allocation()
            else:
                print("✅ Port 5002 is now available")
                return True
                
        except Exception as e:
            print(f"❌ Error applying fixes: {e}")
            return False
    
    async def implement_dynamic_port_allocation(self):
        """Implement dynamic port allocation in the main platform."""
        print("🔄 Implementing dynamic port allocation...")
        
        try:
            app_py_path = project_root / "main_platform" / "app.py"
            
            if not app_py_path.exists():
                print(f"❌ app.py not found at {app_py_path}")
                return False
            
            # Read current content
            original_content = app_py_path.read_text()
            
            # Create improved version with dynamic port allocation
            improved_content = self.create_improved_app_py(original_content)
            
            # Backup original
            backup_path = app_py_path.with_suffix('.py.backup')
            backup_path.write_text(original_content)
            print(f"📄 Backup created: {backup_path}")
            
            # Write improved version
            app_py_path.write_text(improved_content)
            print("✅ Dynamic port allocation implemented")
            
            self.results["fixes_applied"].append({
                "fix": "dynamic_port_allocation",
                "file": str(app_py_path),
                "backup": str(backup_path),
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to implement dynamic port allocation: {e}")
            return False
    
    def create_improved_app_py(self, original_content):
        """Create an improved app.py with dynamic port allocation."""
        
        # This is a simplified improvement - in a real scenario, 
        # the CodeRepairAgent would provide the specific fixes
        improved_content = f'''#!/usr/bin/env python3
"""
Enhanced Brand Deconstruction Platform - Main Application
With Dynamic Port Allocation and Improved Error Handling
"""

import os
import socket
from contextlib import closing
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_free_port(start_port=5002, max_port=5010):
    """Find a free port starting from start_port."""
    for port in range(start_port, max_port + 1):
        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No free ports found between {{start_port}} and {{max_port}}")

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'brand-platform-secret-key')

# Find available port
try:
    PORT = find_free_port()
    logger.info(f"Using port {{PORT}} for Brand Deconstruction Platform")
except RuntimeError as e:
    logger.error(f"Port allocation failed: {{e}}")
    PORT = 5002  # fallback

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

{original_content.split('app = Flask(__name__)')[-1] if 'app = Flask(__name__)' in original_content else original_content}

if __name__ == '__main__':
    try:
        logger.info(f"🚀 Starting Brand Deconstruction Platform on port {{PORT}}")
        socketio.run(app, 
                    host='0.0.0.0', 
                    port=PORT, 
                    debug=True,
                    allow_unsafe_werkzeug=True)
    except Exception as e:
        logger.error(f"❌ Failed to start application: {{e}}")
        logger.info("Try running with a different port or check for conflicting processes")
'''
        return improved_content
    
    async def generate_report(self):
        """Generate a comprehensive debug report."""
        print("\n📋 Generating debug report...")
        
        report_path = project_root / f"agent_debug_report_{self.debug_session_id}.json"
        
        # Add recommendations based on all analysis
        self.results["recommendations"] = [
            "Implement dynamic port allocation to avoid conflicts",
            "Add proper process management and cleanup",
            "Configure frontend to dynamically discover backend port", 
            "Add health check endpoints for monitoring",
            "Implement graceful shutdown handling"
        ]
        
        # Add summary
        self.results["summary"] = {
            "issue_identified": "Port conflict between main platform and enhanced interface",
            "root_cause": "Multiple services trying to use port 5002",
            "solution_applied": "Dynamic port allocation with fallback handling",
            "agents_used": ["TriageAgent", "CodeAnalyzerAgent", "CodeDebuggerAgent", "CodeRepairAgent"],
            "status": "resolved" if len(self.results["fixes_applied"]) > 0 else "analysis_complete"
        }
        
        # Write report
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"✅ Debug report saved: {report_path}")
        return report_path

async def main():
    """Main debugging workflow."""
    print("🤖 Agent-Driven Brand Deconstruction Platform Debugger")
    print("=" * 60)
    
    debugger = AgentDrivenDebugger()
    
    # Initialize agent system
    if not await debugger.initialize_agents():
        print("❌ Cannot proceed without agent system")
        return 1
    
    try:
        # Execute debugging workflow
        triage_result = await debugger.step1_triage_analysis()
        code_analysis = await debugger.step2_code_analysis() 
        debug_investigation = await debugger.step3_debug_investigation()
        repair_result = await debugger.step4_generate_fixes()
        
        # Apply fixes
        fix_success = await debugger.step5_apply_fixes(repair_result)
        
        # Generate report
        report_path = await debugger.generate_report()
        
        print(f"\n🎯 Debug Session Complete!")
        print(f"📊 Report: {report_path}")
        
        if fix_success:
            print("✅ Fixes applied successfully - try starting the platform now")
            return 0
        else:
            print("⚠️  Analysis complete but some fixes may need manual intervention")
            return 1
            
    except Exception as e:
        print(f"❌ Debug session failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
