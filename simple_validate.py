#!/usr/bin/env python3
"""
Simple validation script for the hybrid architecture.
"""

import os
import sys
from pathlib import Path

def main():
    print("🚀 Starting hybrid architecture validation...")
    
    # Check project structure
    print("\n🔍 Checking project structure...")
    
    project_root = Path(__file__).parent
    
    required_files = [
        "shared_agents/__init__.py",
        "shared_agents/core/agent_factory.py",
        "shared_agents/config/shared_config.py",
        "VectorDBRAG/agents/enhanced/enhanced_agents.py",
        "VectorDBRAG/agents/enhanced/factory.py",
        "VectorDBRAG/enhanced_agent_integration.py",
        "MIGRATION_GUIDE.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            all_exist = False
    
    # Test imports
    print("\n🔍 Testing imports...")
    
    try:
        sys.path.insert(0, str(project_root))
        
        from shared_agents.core.agent_factory import AgentCapability, AgentResponse
        print("  ✅ Core agent factory imports")
        
        from shared_agents.config.shared_config import SharedConfig, get_config
        print("  ✅ Configuration imports")
        
        config = get_config()
        print("  ✅ Configuration creation")
        
        capabilities = list(AgentCapability)
        print(f"  ✅ Found {len(capabilities)} agent capabilities")
        
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        all_exist = False
    
    # Summary
    print("\n" + "="*50)
    if all_exist:
        print("✅ VALIDATION PASSED")
        print("🎯 Hybrid architecture is properly set up!")
        print("\nNext steps:")
        print("  - Test Flask server: cd VectorDBRAG && python app.py")
        print("  - Run integration tests")
    else:
        print("❌ VALIDATION FAILED")
        print("🔧 Fix the missing components above")
    
    print("="*50)
    
    return 0 if all_exist else 1

if __name__ == "__main__":
    sys.exit(main())
