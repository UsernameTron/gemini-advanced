#!/usr/bin/env python3
"""
End-to-End Validation Script for Enhanced Agent Architecture
Tests the complete hybrid architecture from configuration to execution
"""

import os
import sys
import json
import time
import asyncio
import requests
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Add project paths
sys.path.append('/Users/cpconnor/projects/Meld and RAG/VectorDBRAG')
sys.path.append('/Users/cpconnor/projects/Meld and RAG/shared_agents')

from shared_agents.config.shared_config import SharedConfig, ConfigEnvironment, get_config
from shared_agents.validation.system_validator import SystemValidator, run_full_validation


@dataclass
class TestResult:
    """Result of a test execution."""
    test_name: str
    success: bool
    duration: float
    details: Dict[str, Any]
    error: Optional[str] = None


class EndToEndValidator:
    """Comprehensive end-to-end validation of the enhanced agent architecture."""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        """Initialize validator."""
        self.base_url = base_url
        self.results: List[TestResult] = []
        
        # Test configuration
        self.test_config = {
            'timeout': 30,
            'retry_count': 3,
            'test_agents': [
                'code_analysis',
                'code_debugging', 
                'code_repair',
                'test_generation',
                'research_analysis',
                'strategic_planning'
            ],
            'test_queries': {
                'code_analysis': 'Analyze this Python function: def factorial(n): return 1 if n <= 1 else n * factorial(n-1)',
                'code_debugging': 'Find bugs in this code: def divide(a, b): return a / b',
                'code_repair': 'Fix this broken code: def greet(name print(f"Hello {name}")',
                'test_generation': 'Generate tests for this function: def add(a, b): return a + b',
                'research_analysis': 'Research the latest trends in AI for software development',
                'strategic_planning': 'Create a strategic plan for launching a new AI product'
            }
        }
    
    def run_complete_validation(self) -> Dict[str, Any]:
        """Run complete end-to-end validation."""
        print("🚀 Starting End-to-End Validation of Enhanced Agent Architecture")
        print("=" * 80)
        
        start_time = time.time()
        
        # Step 1: Configuration Validation
        print("1️⃣  Configuration Validation...")
        config_result = self.validate_configuration()
        self.results.append(config_result)
        
        # Step 2: System Health Check
        print("2️⃣  System Health Check...")
        health_result = self.validate_system_health()
        self.results.append(health_result)
        
        # Step 3: Agent Factory Validation
        print("3️⃣  Agent Factory Validation...")
        factory_result = self.validate_agent_factory()
        self.results.append(factory_result)
        
        # Step 4: Flask Integration Test
        print("4️⃣  Flask Integration Test...")
        flask_result = self.validate_flask_integration()
        self.results.append(flask_result)
        
        # Step 5: Enhanced Agent Endpoints
        print("5️⃣  Enhanced Agent Endpoints...")
        endpoints_result = self.validate_enhanced_endpoints()
        self.results.append(endpoints_result)
        
        # Step 6: Agent Execution Tests
        print("6️⃣  Agent Execution Tests...")
        execution_result = self.validate_agent_execution()
        self.results.append(execution_result)
        
        # Step 7: Performance Benchmarks
        print("7️⃣  Performance Benchmarks...")
        performance_result = self.validate_performance()
        self.results.append(performance_result)
        
        # Step 8: Concurrency Tests
        print("8️⃣  Concurrency Tests...")
        concurrency_result = self.validate_concurrency()
        self.results.append(concurrency_result)
        
        total_time = time.time() - start_time
        
        # Generate final report
        report = self.generate_final_report(total_time)
        
        print("=" * 80)
        print("✅ End-to-End Validation Completed")
        print(f"📊 Total Time: {total_time:.2f}s")
        print(f"🧪 Tests: {len(self.results)}")
        print(f"✅ Passed: {sum(1 for r in self.results if r.success)}")
        print(f"❌ Failed: {sum(1 for r in self.results if not r.success)}")
        
        return report
    
    def validate_configuration(self) -> TestResult:
        """Validate configuration loading and validation."""
        start_time = time.time()
        
        try:
            # Test configuration loading
            config = get_config("default", ConfigEnvironment.TESTING)
            
            # Test configuration validation
            errors = config.validate()
            
            # Test model configurations
            model_configs = list(config.models.keys())
            
            success = len(errors) == 0 and len(model_configs) > 0
            
            return TestResult(
                test_name="configuration_validation",
                success=success,
                duration=time.time() - start_time,
                details={
                    'config_environment': config.environment.value,
                    'validation_errors': errors,
                    'models_configured': model_configs,
                    'agent_config_loaded': config.agent_config is not None,
                    'rag_config_loaded': config.rag_config is not None
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="configuration_validation",
                success=False,
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    def validate_system_health(self) -> TestResult:
        """Validate system health endpoints."""
        start_time = time.time()
        
        try:
            # Test basic health endpoint
            response = requests.get(f"{self.base_url}/health", timeout=self.test_config['timeout'])
            
            if response.status_code == 200:
                health_data = response.json()
                success = health_data.get('status') in ['healthy', 'connected']
            else:
                success = False
                health_data = {"error": f"HTTP {response.status_code}"}
            
            return TestResult(
                test_name="system_health_check",
                success=success,
                duration=time.time() - start_time,
                details={
                    'status_code': response.status_code,
                    'health_data': health_data,
                    'response_time': response.elapsed.total_seconds()
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="system_health_check",
                success=False,
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    def validate_agent_factory(self) -> TestResult:
        """Validate agent factory functionality."""
        start_time = time.time()
        
        try:
            from agents.enhanced.factory import EnhancedAgentFactory
            from shared_agents.core.agent_factory import AgentCapability
            
            # Test factory creation
            config = get_config()
            factory = EnhancedAgentFactory(config.to_dict())
            
            # Test agent creation
            test_agent = factory.create_agent('code_analysis')
            
            # Test capability-based creation
            capability_agent = factory.create_agent_by_capability(AgentCapability.CODE_ANALYSIS)
            
            # Test agent types
            agent_types = factory.get_agent_types()
            
            success = (
                test_agent is not None and
                capability_agent is not None and
                len(agent_types) > 0
            )
            
            return TestResult(
                test_name="agent_factory_validation",
                success=success,
                duration=time.time() - start_time,
                details={
                    'factory_created': factory is not None,
                    'test_agent_created': test_agent is not None,
                    'capability_agent_created': capability_agent is not None,
                    'agent_types_count': len(agent_types),
                    'available_types': agent_types
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="agent_factory_validation",
                success=False,
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    def validate_flask_integration(self) -> TestResult:
        """Validate Flask application integration."""
        start_time = time.time()
        
        try:
            # Test enhanced agent status endpoint
            response = requests.get(
                f"{self.base_url}/api/enhanced/agents/status",
                timeout=self.test_config['timeout']
            )
            
            if response.status_code == 200:
                status_data = response.json()
                success = status_data.get('status') == 'success'
            else:
                success = False
                status_data = {"error": f"HTTP {response.status_code}"}
            
            return TestResult(
                test_name="flask_integration",
                success=success,
                duration=time.time() - start_time,
                details={
                    'status_code': response.status_code,
                    'status_data': status_data,
                    'enhanced_routes_available': success
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="flask_integration",
                success=False,
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    def validate_enhanced_endpoints(self) -> TestResult:
        """Validate enhanced agent endpoints."""
        start_time = time.time()
        
        endpoints_tested = []
        
        try:
            # Test agent types endpoint
            response = requests.get(f"{self.base_url}/api/enhanced/agents/types")
            endpoints_tested.append({
                'endpoint': '/api/enhanced/agents/types',
                'status': response.status_code,
                'success': response.status_code == 200
            })
            
            # Test capabilities endpoint
            response = requests.get(f"{self.base_url}/api/enhanced/agents/capabilities")
            endpoints_tested.append({
                'endpoint': '/api/enhanced/agents/capabilities',
                'status': response.status_code,
                'success': response.status_code == 200
            })
            
            # Test health endpoint
            response = requests.get(f"{self.base_url}/api/enhanced/agents/health")
            endpoints_tested.append({
                'endpoint': '/api/enhanced/agents/health',
                'status': response.status_code,
                'success': response.status_code == 200
            })
            
            success = all(endpoint['success'] for endpoint in endpoints_tested)
            
            return TestResult(
                test_name="enhanced_endpoints",
                success=success,
                duration=time.time() - start_time,
                details={
                    'endpoints_tested': endpoints_tested,
                    'total_endpoints': len(endpoints_tested),
                    'successful_endpoints': sum(1 for e in endpoints_tested if e['success'])
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="enhanced_endpoints",
                success=False,
                duration=time.time() - start_time,
                details={'endpoints_tested': endpoints_tested},
                error=str(e)
            )
    
    def validate_agent_execution(self) -> TestResult:
        """Validate agent execution functionality."""
        start_time = time.time()
        
        execution_results = []
        
        try:
            for agent_type in self.test_config['test_agents']:
                if agent_type in self.test_config['test_queries']:
                    query = self.test_config['test_queries'][agent_type]
                    
                    # Test agent execution
                    payload = {
                        'query': query,
                        'agent_type': agent_type,
                        'context': {'test': True}
                    }
                    
                    response = requests.post(
                        f"{self.base_url}/api/enhanced/agents/query",
                        json=payload,
                        timeout=self.test_config['timeout']
                    )
                    
                    execution_results.append({
                        'agent_type': agent_type,
                        'status_code': response.status_code,
                        'success': response.status_code == 200,
                        'response_time': response.elapsed.total_seconds(),
                        'query': query
                    })
            
            success = all(result['success'] for result in execution_results)
            
            return TestResult(
                test_name="agent_execution",
                success=success,
                duration=time.time() - start_time,
                details={
                    'execution_results': execution_results,
                    'agents_tested': len(execution_results),
                    'successful_executions': sum(1 for r in execution_results if r['success']),
                    'avg_response_time': sum(r['response_time'] for r in execution_results) / len(execution_results) if execution_results else 0
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="agent_execution",
                success=False,
                duration=time.time() - start_time,
                details={'execution_results': execution_results},
                error=str(e)
            )
    
    def validate_performance(self) -> TestResult:
        """Validate system performance."""
        start_time = time.time()
        
        try:
            # Run async validation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                validation_report = loop.run_until_complete(run_full_validation("default"))
            finally:
                loop.close()
            
            success = validation_report.get('overall_success', False)
            
            return TestResult(
                test_name="performance_validation",
                success=success,
                duration=time.time() - start_time,
                details={
                    'overall_success_rate': validation_report.get('overall_success_rate', 0),
                    'total_tests': validation_report.get('total_tests', 0),
                    'successful_tests': validation_report.get('successful_tests', 0),
                    'capabilities_tested': len(validation_report.get('capabilities_tested', [])),
                    'validation_time': validation_report.get('total_validation_time', 0)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="performance_validation",
                success=False,
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    def validate_concurrency(self) -> TestResult:
        """Validate concurrent request handling."""
        start_time = time.time()
        
        try:
            import threading
            import concurrent.futures
            
            def make_concurrent_request(agent_type: str) -> Dict[str, Any]:
                payload = {
                    'query': f'Concurrent test for {agent_type}',
                    'agent_type': agent_type,
                    'context': {'concurrent_test': True}
                }
                
                response = requests.post(
                    f"{self.base_url}/api/enhanced/agents/query",
                    json=payload,
                    timeout=self.test_config['timeout']
                )
                
                return {
                    'agent_type': agent_type,
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'response_time': response.elapsed.total_seconds()
                }
            
            # Test concurrent requests
            agent_types = self.test_config['test_agents'][:3]  # Limit to 3 for concurrency test
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(make_concurrent_request, agent_type) for agent_type in agent_types]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            success = all(result['success'] for result in results)
            
            return TestResult(
                test_name="concurrency_validation",
                success=success,
                duration=time.time() - start_time,
                details={
                    'concurrent_requests': len(results),
                    'successful_requests': sum(1 for r in results if r['success']),
                    'results': results,
                    'avg_response_time': sum(r['response_time'] for r in results) / len(results) if results else 0
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="concurrency_validation",
                success=False,
                duration=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    def generate_final_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        passed_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'validation_summary': {
                'total_time': total_time,
                'total_tests': len(self.results),
                'passed_tests': len(passed_tests),
                'failed_tests': len(failed_tests),
                'success_rate': len(passed_tests) / len(self.results) if self.results else 0,
                'overall_success': len(failed_tests) == 0
            },
            'test_results': [
                {
                    'test_name': r.test_name,
                    'success': r.success,
                    'duration': r.duration,
                    'error': r.error,
                    'details': r.details
                }
                for r in self.results
            ],
            'performance_metrics': {
                'avg_test_duration': sum(r.duration for r in self.results) / len(self.results) if self.results else 0,
                'longest_test': max(self.results, key=lambda r: r.duration).test_name if self.results else None,
                'shortest_test': min(self.results, key=lambda r: r.duration).test_name if self.results else None
            },
            'recommendations': self._generate_recommendations(failed_tests)
        }
        
        return report
    
    def _generate_recommendations(self, failed_tests: List[TestResult]) -> List[str]:
        """Generate recommendations based on failed tests."""
        recommendations = []
        
        if not failed_tests:
            recommendations.append("All tests passed! System is ready for production.")
            return recommendations
        
        for test in failed_tests:
            if test.test_name == "configuration_validation":
                recommendations.append("Check configuration files and environment variables")
            elif test.test_name == "system_health_check":
                recommendations.append("Verify Flask server is running and accessible")
            elif test.test_name == "agent_factory_validation":
                recommendations.append("Check agent factory dependencies and configurations")
            elif test.test_name == "flask_integration":
                recommendations.append("Verify Flask routes are properly registered")
            elif test.test_name == "enhanced_endpoints":
                recommendations.append("Check enhanced agent endpoint implementations")
            elif test.test_name == "agent_execution":
                recommendations.append("Verify agent execution logic and dependencies")
            elif test.test_name == "performance_validation":
                recommendations.append("Review system performance and optimize slow components")
            elif test.test_name == "concurrency_validation":
                recommendations.append("Check concurrency handling and thread safety")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None):
        """Save validation report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"e2e_validation_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Validation report saved to {filename}")


def main():
    """Main validation execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="End-to-End Validation of Enhanced Agent Architecture")
    parser.add_argument('--url', default='http://localhost:5001', help='Base URL for Flask server')
    parser.add_argument('--output', help='Output file for validation report')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    
    args = parser.parse_args()
    
    # Create validator
    validator = EndToEndValidator(base_url=args.url)
    validator.test_config['timeout'] = args.timeout
    
    # Run validation
    report = validator.run_complete_validation()
    
    # Save report
    validator.save_report(report, args.output)
    
    # Exit with appropriate code
    if report['validation_summary']['overall_success']:
        print("\n🎉 All validations passed! System is ready.")
        sys.exit(0)
    else:
        print(f"\n❌ {report['validation_summary']['failed_tests']} validations failed.")
        print("📋 Check the report for details and recommendations.")
        sys.exit(1)


if __name__ == "__main__":
    main()
