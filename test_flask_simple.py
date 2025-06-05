#!/usr/bin/env python3
"""
Simple Flask test for enhanced agents without the complex app.py dependencies.
"""

import sys
import json
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure path
sys.path.append('/Users/cpconnor/projects/Meld and RAG')

# Create a simple Flask app for testing
app = Flask(__name__)
CORS(app)

# Initialize enhanced agent factory
try:
    from VectorDBRAG.agents.enhanced.factory import EnhancedAgentFactory
    
    config = {
        "default_model": "gpt-3.5-turbo",
        "openai_client": None
    }
    
    factory = EnhancedAgentFactory(config)
    app.factory = factory
    print("✅ Enhanced agent factory initialized")
    
except Exception as e:
    print(f"❌ Failed to initialize enhanced agents: {e}")
    app.factory = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "enhanced_agents": app.factory is not None,
        "agent_types": list(app.factory.get_agent_types().keys()) if app.factory else []
    })

@app.route('/api/enhanced/agents/types', methods=['GET'])
def get_agent_types():
    """Get available enhanced agent types."""
    if not app.factory:
        return jsonify({"error": "Enhanced agents not available"}), 500
    
    agent_types = app.factory.get_agent_types()
    return jsonify({
        "agent_types": list(agent_types.keys()),
        "total_count": len(agent_types)
    })

@app.route('/api/enhanced/agents/query', methods=['POST'])
def enhanced_agent_query():
    """Query an enhanced agent."""
    if not app.factory:
        return jsonify({"error": "Enhanced agents not available"}), 500
    
    try:
        data = request.get_json()
        agent_type = data.get('agent_type', 'code_analysis')
        input_data = data.get('input', {})
        
        # Create agent
        agent = app.factory.create_agent(agent_type)
        
        # For testing, we'll simulate execution without actually calling OpenAI
        # unless we have an API key
        import os
        if os.getenv("OPENAI_API_KEY"):
            # Run actual execution in a separate event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(agent.execute(input_data))
                return jsonify({
                    "success": response.success,
                    "result": response.result,
                    "error": response.error,
                    "execution_time": response.execution_time,
                    "agent_name": agent.name,
                    "agent_type": agent_type
                })
            finally:
                loop.close()
        else:
            # Return mock response for testing
            return jsonify({
                "success": True,
                "result": f"Mock response from {agent.name} - agent working correctly",
                "error": None,
                "execution_time": 0.1,
                "agent_name": agent.name,
                "agent_type": agent_type,
                "note": "Mock response - set OPENAI_API_KEY for actual execution"
            })
            
    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

@app.route('/api/enhanced/agents/capabilities/<capability>', methods=['GET'])
def get_agents_by_capability(capability):
    """Get agents with specific capability."""
    if not app.factory:
        return jsonify({"error": "Enhanced agents not available"}), 500
    
    try:
        from shared_agents.core.agent_factory import AgentCapability
        
        # Map string to enum
        capability_enum = None
        for cap in AgentCapability:
            if cap.value == capability:
                capability_enum = cap
                break
        
        if not capability_enum:
            return jsonify({"error": f"Unknown capability: {capability}"}), 400
        
        agents = app.factory.create_agents_with_capability(capability_enum)
        
        return jsonify({
            "capability": capability,
            "agents": [{"name": agent.name, "type": agent_type} 
                      for agent_type, agent in agents.items()],
            "count": len(agents)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced Agent Flask Test Server")
    print("=" * 50)
    print("Available endpoints:")
    print("  - GET  /health")
    print("  - GET  /api/enhanced/agents/types")
    print("  - POST /api/enhanced/agents/query")
    print("  - GET  /api/enhanced/agents/capabilities/<capability>")
    print("\nServer starting on http://localhost:5001")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
