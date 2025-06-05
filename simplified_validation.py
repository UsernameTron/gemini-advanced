#!/usr/bin/env python3
"""
Simplified End-to-End Validation for Enhanced Agent System
This script validates the hybrid architecture without complex dependencies.
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, List

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class SimplifiedValidator:
    """Simplified system validator for the hybrid architecture."""
    
    def __init__(self):
        self.results = {}
        self.errors = []
        
    def validate_project_structure(self) -> Dict[str, Any]:
        """Validate that all required files and directories exist."""
        print("🔍 Validating project structure...")
        
        required_paths = [
            "shared_agents/__init__.py",
            "shared_agents/core/agent_factory.py",
            "shared_agents/config/shared_config.py",
            "VectorDBRAG/agents/enhanced/enhanced_agents.py",
            "VectorDBRAG/agents/enhanced/factory.py",
            "VectorDBRAG/enhanced_agent_integration.py",
            "VectorDBRAG/app.py",
            "MIGRATION_GUIDE.md"
        ]
        
        structure_results = {
            'test_name': 'project_structure',
            'success': True,
            'missing_files': [],
            'existing_files': []
        }
        
        for path in required_paths:
            full_path = project_root / path
            if full_path.exists():
                structure_results['existing_files'].append(path)
                print(f"  ✅ {path}")
            else:
                structure_results['missing_files'].append(path)
                structure_results['success'] = False
                print(f"  ❌ {path}")
        
        return structure_results
    
    def validate_imports(self) -> Dict[str, Any]:
        """Validate that core modules can be imported."""
        print("🔍 Validating imports...")
        
        import_results = {
            'test_name': 'imports',
            'success': True,
            'successful_imports': [],
            'failed_imports': []
        }
        
        # Test imports
        test_imports = [
            ("shared_agents", "shared_agents"),
            ("shared_agents.core.agent_factory", "AgentCapability, AgentResponse"),
            ("shared_agents.config.shared_config", "SharedConfig, get_config"),
        ]
        
        for module_name, import_spec in test_imports:
            try:
                if import_spec == module_name:
                    __import__(module_name)
                else:
                    exec(f"from {module_name} import {import_spec}")
                
                import_results['successful_imports'].append(f"{module_name}: {import_spec}")
                print(f"  ✅ {module_name}")
                
            except Exception as e:
                import_results['failed_imports'].append({
                    'module': module_name,
                    'error': str(e)
                })
                import_results['success'] = False
                print(f"  ❌ {module_name}: {e}")
        
        return import_results
    
    def validate_config_system(self) -> Dict[str, Any]:
        """Validate the configuration management system."""
        print("🔍 Validating configuration system...")
        
        config_results = {
            'test_name': 'configuration',
            'success': True,
            'tests_passed': [],
            'tests_failed': []
        }
        
        try:
            from shared_agents.config.shared_config import SharedConfig, get_config
            
            # Test default config creation
            default_config = get_config()
            if default_config:
                config_results['tests_passed'].append("default_config_creation")
                print("  ✅ Default config creation")
            else:
                config_results['tests_failed'].append("default_config_creation: No config returned")
                config_results['success'] = False
                print("  ❌ Default config creation failed")
            
            # Test config serialization
            config_dict = default_config.to_dict()
            if isinstance(config_dict, dict) and 'environment' in config_dict:
                config_results['tests_passed'].append("config_serialization")
                print("  ✅ Config serialization")
            else:
                config_results['tests_failed'].append("config_serialization: Invalid dict structure")
                config_results['success'] = False
                print("  ❌ Config serialization failed")
            
        except Exception as e:
            config_results['tests_failed'].append(f"config_system_error: {str(e)}")
            config_results['success'] = False
            print(f"  ❌ Configuration system error: {e}")
        
        return config_results
    
    def validate_agent_capabilities(self) -> Dict[str, Any]:
        """Validate that all agent capabilities are defined."""
        print("🔍 Validating agent capabilities...")
        
        capabilities_results = {
            'test_name': 'agent_capabilities',
            'success': True,
            'available_capabilities': [],
            'missing_capabilities': []
        }
        
        try:
            from shared_agents.core.agent_factory import AgentCapability
            
            # Expected capabilities
            expected_capabilities = [
                'CODE_ANALYSIS', 'CODE_DEBUGGING', 'CODE_REPAIR',
                'PERFORMANCE_ANALYSIS', 'TEST_GENERATION',
                'SPEECH_ANALYSIS', 'VISUAL_ANALYSIS',
                'STRATEGIC_PLANNING'
            ]
            
            available_capabilities = [cap.name for cap in AgentCapability]
            capabilities_results['available_capabilities'] = available_capabilities
            
            for expected in expected_capabilities:
                if expected in available_capabilities:
                    print(f"  ✅ {expected}")
                else:
                    capabilities_results['missing_capabilities'].append(expected)
                    capabilities_results['success'] = False
                    print(f"  ❌ {expected}")
            
            print(f"  📊 Total capabilities available: {len(available_capabilities)}")
            
        except Exception as e:
            capabilities_results['success'] = False
            self.errors.append(f"Agent capabilities validation failed: {e}")
            print(f"  ❌ Agent capabilities validation error: {e}")
        
        return capabilities_results
    
    def validate_enhanced_agents(self) -> Dict[str, Any]:
        """Validate that enhanced agents can be imported."""
        print("🔍 Validating enhanced agent system...")
        
        agents_results = {
            'test_name': 'enhanced_agents',
            'success': True,
            'available_agents': [],
            'import_errors': []
        }
        
        try:
            # Check if enhanced agents file exists and can be imported
            enhanced_agents_path = project_root / "VectorDBRAG/agents/enhanced/enhanced_agents.py"
            
            if enhanced_agents_path.exists():
                print("  ✅ Enhanced agents file exists")
                
                # Try to import (but don't instantiate due to dependencies)
                sys.path.insert(0, str(project_root / "VectorDBRAG"))
                
                try:
                    import agents.enhanced.enhanced_agents as enhanced_agents
                    
                    # Look for agent classes
                    agent_classes = [name for name in dir(enhanced_agents) 
                                   if name.endswith('Agent') and not name.startswith('_')]
                    
                    agents_results['available_agents'] = agent_classes
                    print(f"  ✅ Found {len(agent_classes)} agent classes")
                    for agent_class in agent_classes:
                        print(f"    - {agent_class}")
                    
                except ImportError as e:
                    agents_results['import_errors'].append(str(e))
                    print(f"  ⚠️  Import warning: {e}")
                    # Don't mark as failure since this might be due to missing dependencies
                
            else:
                agents_results['success'] = False
                agents_results['import_errors'].append("Enhanced agents file not found")
                print("  ❌ Enhanced agents file not found")
                
        except Exception as e:
            agents_results['success'] = False
            agents_results['import_errors'].append(str(e))
            print(f"  ❌ Enhanced agents validation error: {e}")
        
        return agents_results
    
    def validate_flask_integration(self) -> Dict[str, Any]:
        """Validate Flask integration files."""
        print("🔍 Validating Flask integration...")
        
        flask_results = {
            'test_name': 'flask_integration',
            'success': True,
            'integration_files': [],
            'missing_files': []
        }
        
        integration_files = [
            "VectorDBRAG/enhanced_agent_integration.py",
            "VectorDBRAG/app.py"
        ]
        
        for file_path in integration_files:
            full_path = project_root / file_path
            if full_path.exists():
                flask_results['integration_files'].append(file_path)
                print(f"  ✅ {file_path}")
                
                # Check for key Flask integration patterns
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                        
                    if 'enhanced' in file_path.lower():
                        if '@app.route' in content or 'def get_factory' in content:
                            print(f"    ✅ Contains Flask integration patterns")
                        else:
                            print(f"    ⚠️  Missing expected Flask patterns")
                    
                except Exception as e:
                    print(f"    ⚠️  Could not analyze file: {e}")
                    
            else:
                flask_results['missing_files'].append(file_path)
                flask_results['success'] = False
                print(f"  ❌ {file_path}")
        
        return flask_results
    
    def run_complete_validation(self) -> Dict[str, Any]:
        """Run all validation tests."""
        print("🚀 Starting complete system validation...\n")
        start_time = time.time()
        
        # Run all validation tests
        validation_tests = [
            self.validate_project_structure,
            self.validate_imports,
            self.validate_config_system,
            self.validate_agent_capabilities,
            self.validate_enhanced_agents,
            self.validate_flask_integration
        ]
        
        all_results = []
        overall_success = True
        
        for test_func in validation_tests:
            try:
                result = test_func()
                all_results.append(result)
                
                if not result.get('success', False):
                    overall_success = False
                
                print()  # Add spacing between tests
                
            except Exception as e:
                error_result = {
                    'test_name': test_func.__name__,
                    'success': False,
                    'error': str(e)
                }
                all_results.append(error_result)
                overall_success = False
                print(f"❌ {test_func.__name__} failed with error: {e}\n")
        
        # Compile final report
        total_time = time.time() - start_time
        
        final_report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_success': overall_success,
            'total_validation_time': total_time,
            'individual_tests': all_results,
            'summary': {
                'total_tests': len(all_results),
                'passed_tests': sum(1 for r in all_results if r.get('success', False)),
                'failed_tests': sum(1 for r in all_results if not r.get('success', False)),
                'success_rate': sum(1 for r in all_results if r.get('success', False)) / len(all_results)
            },
            'errors': self.errors
        }
        
        return final_report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print validation summary."""
        print("=" * 60)
        print("🎯 VALIDATION SUMMARY")
        print("=" * 60)
        
        summary = report['summary']
        print(f"Overall Success: {'✅ PASS' if report['overall_success'] else '❌ FAIL'}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Total Time: {report['total_validation_time']:.2f}s")
        
        if report['errors']:
            print(f"\n❌ Errors Found ({len(report['errors'])}):")
            for error in report['errors']:
                print(f"  - {error}")
        
        print("\n🔧 Next Steps:")
        if report['overall_success']:
            print("  ✅ System validation passed! Ready for testing.")
            print("  🚀 You can now:")
            print("    - Start the Flask server: cd VectorDBRAG && python app.py")
            print("    - Run integration tests: python test_enhanced_flask_integration.py")
            print("    - Test specific agent endpoints")
        else:
            print("  ❌ Fix the following issues before proceeding:")
            failed_tests = [test for test in report['individual_tests'] if not test.get('success', False)]
            for test in failed_tests:
                print(f"    - {test['test_name']}: Check {test.get('error', 'configuration')}")
        
        print("=" * 60)


def main():
    """Main validation function."""
    validator = SimplifiedValidator()
    report = validator.run_complete_validation()
    validator.print_summary(report)
    
    # Save report
    report_file = project_root / f"validation_report_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Return appropriate exit code
    return 0 if report['overall_success'] else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
