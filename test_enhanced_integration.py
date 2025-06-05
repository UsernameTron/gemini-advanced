#!/usr/bin/env python3
"""
Test script to verify the enhanced agent integration with the shared framework.
This script runs direct tests against the agent factory and agents without requiring Flask.
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
import json
import sys
import traceback
from pprint import pprint

# Configure path to include both projects
sys.path.append('/Users/cpconnor/projects/Meld and RAG')

# Import from shared framework
try:
    from shared_agents.core.agent_factory import AgentCapability, AgentBase, AgentResponse
    shared_framework_available = True
except ImportError:
    print("⚠️  Shared agent framework not available")
    shared_framework_available = False

# Import from VectorDBRAG enhanced agents
try:
    from VectorDBRAG.agents.enhanced.factory import EnhancedAgentFactory
    enhanced_agents_available = True
except ImportError:
    print("⚠️  Enhanced agent factory not available")
    enhanced_agents_available = False

# Import from VectorDBRAG Ollama-based agents for local testing
try:
    from VectorDBRAG.agents_ollama import OLLAMA_AVAILABLE, CodeAnalyzerAgent
    ollama_agents_available = True
except ImportError:
    print("⚠️  Ollama-based agents not available")
    ollama_agents_available = False


async def test_enhanced_agent_integration():
    """Test the integration between shared framework and enhanced agents."""
    print("\n🧪 Testing Enhanced Agent Integration")
    print("=" * 50)
    
    if not shared_framework_available:
        print("❌ Shared agent framework not available - aborting test")
        return False
    
    if not enhanced_agents_available:
        print("❌ Enhanced agent factory not available - aborting test")
        return False
    
    # Step 1: Create factory with test configuration
    print("\n📋 Step 1: Creating enhanced agent factory")
    try:
        factory = EnhancedAgentFactory({
            'openai_api_key': os.environ.get('OPENAI_API_KEY'),
            'default_model': 'gpt-4o',  # Will be ignored if no API key
            'fast_model': 'gpt-3.5-turbo'  # Will be ignored if no API key
        })
        print("✅ Factory created successfully")
    except Exception as e:
        print(f"❌ Failed to create factory: {e}")
        traceback.print_exc()
        return False
    
    # Step 2: Get available agent types
    print("\n📋 Step 2: Getting available agent types")
    try:
        agent_types = factory.get_agent_types()
        print(f"✅ Found {len(agent_types)} agent types:")
        for agent_type, info in agent_types.items():
            print(f"  - {agent_type}: {info.get('class', 'Unknown')}")
    except Exception as e:
        print(f"❌ Failed to get agent types: {e}")
        traceback.print_exc()
        return False
    
    # Step 3: Create and test code analysis agent
    print("\n📋 Step 3: Testing code analysis agent")
    try:
        code_agent = factory.create_agent("code_analysis")
        print(f"✅ Created agent: {code_agent.name} ({code_agent.agent_type})")
        
        # Get capabilities
        capabilities = [cap.value for cap in code_agent.capabilities]
        print(f"✅ Agent capabilities: {', '.join(capabilities)}")
        
        # Simple test query if OpenAI API key and client are available
        if os.environ.get('OPENAI_API_KEY') and getattr(code_agent, 'openai_client', None):
            print("\n🧪 Running live test with code analysis query")
            result = await code_agent._safe_execute({
                'code': 'def add(a, b):\n    return a + b',
                'query': 'Analyze this function'
            })

            print("\n✅ Agent Response:")
            print(f"Success: {result.success}")
            print(f"Execution time: {result.execution_time:.2f}s")
            # Safely print result snippet
            if isinstance(result.result, str):
                print(f"Result: {result.result[:200]}...")
            else:
                print(f"Result: {result.result}")
        else:
            print("\n⚠️ Skipping live test - no OpenAI client or API key found")
    except Exception as e:
        print(f"❌ Failed to test code agent: {e}")
        traceback.print_exc()
        return False
    
    # Step 4: Create and test agent by capability
    print("\n📋 Step 4: Testing agent capability creation")
    try:
        capability = AgentCapability.CODE_REPAIR
        agents_with_capability = factory.create_agents_with_capability(capability)
        
        print(f"✅ Found {len(agents_with_capability)} agents with {capability.value} capability:")
        for agent_type, agent in agents_with_capability.items():
            print(f"  - {agent.name} ({agent.agent_type})")
    except Exception as e:
        print(f"❌ Failed to test capability creation: {e}")
        traceback.print_exc()
        return False
    
    # Step 5: Test Ollama-based code analysis agent if available
    print("\n📋 Step 5: Testing Ollama-based code analysis agent")
    if ollama_agents_available and OLLAMA_AVAILABLE:
        try:
            model_name = os.environ.get("LOCAL_MODEL", "phi3.5")
            ollama_agent = CodeAnalyzerAgent(model=model_name)
            print(f"✅ Created Ollama agent: {ollama_agent.name} ({ollama_agent.model})")
            result = await ollama_agent.execute({
                "code": "def add(a, b):\n    return a + b",
                "analysis_type": "general"
            })
            print(f"\n✅ Ollama Agent Response: Success: {result.success}, Execution time: {result.execution_time:.2f}s")
            if isinstance(result.result, str):
                print(f"Result snippet: {result.result[:200]}...")
            else:
                print(f"Result: {result.result}")
        except Exception as e:
            print(f"❌ Ollama agent test failed: {e}")
            traceback.print_exc()
            return False
    else:
        print("\n⚠️ Skipping Ollama test - Ollama client not available or not configured")

    print("\n🎉 All integration tests passed!")
    return True


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    result = asyncio.run(test_enhanced_agent_integration())
    sys.exit(0 if result else 1)
