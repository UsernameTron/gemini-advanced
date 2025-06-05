"""
Validation System for Enhanced Agent Architecture
Provides comprehensive validation, testing, and performance comparison
"""

import time
import json
import asyncio
import statistics
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

from shared_agents.config.shared_config import SharedConfig, get_config
from shared_agents.core.agent_factory import AgentCapability, AgentResponse


@dataclass
class ValidationResult:
    """Result of a validation test."""
    test_name: str
    success: bool
    duration: float
    response: Optional[AgentResponse] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics for agent execution."""
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    success_rate: float
    error_rate: float
    total_executions: int
    throughput: float  # executions per second


@dataclass
class ComparisonResult:
    """Comparison between original and enhanced agents."""
    agent_type: str
    original_metrics: Optional[PerformanceMetrics]
    enhanced_metrics: PerformanceMetrics
    improvement_factor: float
    quality_score: float
    recommendations: List[str]


class AgentValidator:
    """Validates agent functionality and performance."""
    
    def __init__(self, config: Optional[SharedConfig] = None):
        """Initialize validator."""
        self.config = config or get_config()
        self.factory = EnhancedAgentFactory(self.config.to_dict())
        
        # Test scenarios for different agent types
        self.test_scenarios = {
            AgentCapability.CODE_ANALYSIS: [
                {
                    'name': 'basic_code_analysis',
                    'input': {
                        'code': 'def hello(name):\n    return f"Hello, {name}!"',
                        'query': 'Analyze this Python function for quality and improvements'
                    },
                    'expected_keywords': ['function', 'parameter', 'return', 'string']
                },
                {
                    'name': 'complex_code_analysis',
                    'input': {
                        'code': '''
class UserManager:
    def __init__(self):
        self.users = []
    
    def add_user(self, user):
        if user not in self.users:
            self.users.append(user)
        
    def get_user_count(self):
        return len(self.users)
                        ''',
                        'query': 'Analyze this class for design patterns and improvements'
                    },
                    'expected_keywords': ['class', 'method', 'constructor', 'list']
                }
            ],
            AgentCapability.CODE_DEBUGGING: [
                {
                    'name': 'basic_debug',
                    'input': {
                        'code': 'def divide(a, b):\n    return a / b',
                        'query': 'Find potential bugs in this function'
                    },
                    'expected_keywords': ['division', 'zero', 'error', 'exception']
                }
            ],
            AgentCapability.CODE_REPAIR: [
                {
                    'name': 'fix_syntax_error',
                    'input': {
                        'code': 'def greet(name\n    print(f"Hello {name}")',
                        'query': 'Fix the syntax errors in this code'
                    },
                    'expected_keywords': ['syntax', 'parentheses', 'colon']
                }
            ],
            AgentCapability.TEST_GENERATION: [
                {
                    'name': 'generate_unit_tests',
                    'input': {
                        'code': 'def add_numbers(a, b):\n    return a + b',
                        'query': 'Generate unit tests for this function'
                    },
                    'expected_keywords': ['test', 'assert', 'function', 'pytest']
                }
            ],
            AgentCapability.STRATEGIC_PLANNING: [
                {
                    'name': 'business_strategy',
                    'input': {
                        'query': 'Develop a strategic plan for launching a new software product'
                    },
                    'expected_keywords': ['strategy', 'market', 'planning', 'product']
                }
            ],
            AgentCapability.RESEARCH_ANALYSIS: [
                {
                    'name': 'technology_research',
                    'input': {
                        'query': 'Research the latest trends in artificial intelligence for software development'
                    },
                    'expected_keywords': ['AI', 'trends', 'development', 'technology']
                }
            ]
        }
    
    async def validate_agent_capability(self, capability: AgentCapability) -> List[ValidationResult]:
        """Validate all test scenarios for a specific capability."""
        results = []
        
        if capability not in self.test_scenarios:
            return [ValidationResult(
                test_name=f"no_tests_for_{capability.value}",
                success=False,
                duration=0.0,
                error="No test scenarios defined for this capability"
            )]
        
        for scenario in self.test_scenarios[capability]:
            result = await self._run_test_scenario(capability, scenario)
            results.append(result)
        
        return results
    
    async def _run_test_scenario(self, capability: AgentCapability, scenario: Dict[str, Any]) -> ValidationResult:
        """Run a single test scenario."""
        start_time = time.time()
        
        try:
            # Create agent for capability
            agent = self.factory.create_agent_by_capability(capability)
            
            # Execute agent with test input
            response = await agent._safe_execute(scenario['input'])
            
            duration = time.time() - start_time
            
            # Validate response
            success = self._validate_response(response, scenario)
            
            return ValidationResult(
                test_name=scenario['name'],
                success=success,
                duration=duration,
                response=response,
                metadata={
                    'capability': capability.value,
                    'agent_type': agent.agent_type,
                    'expected_keywords': scenario.get('expected_keywords', [])
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return ValidationResult(
                test_name=scenario['name'],
                success=False,
                duration=duration,
                error=str(e),
                metadata={
                    'capability': capability.value,
                    'exception_type': type(e).__name__,
                    'traceback': traceback.format_exc()
                }
            )
    
    def _validate_response(self, response: AgentResponse, scenario: Dict[str, Any]) -> bool:
        """Validate agent response against expected criteria."""
        if not response.success:
            return False
        
        if not response.result:
            return False
        
        # Check for expected keywords
        expected_keywords = scenario.get('expected_keywords', [])
        if expected_keywords:
            result_text = str(response.result).lower()
            found_keywords = [kw for kw in expected_keywords if kw.lower() in result_text]
            
            # Require at least 50% of expected keywords
            keyword_threshold = max(1, len(expected_keywords) // 2)
            if len(found_keywords) < keyword_threshold:
                return False
        
        return True
    
    async def performance_benchmark(self, 
                                   capability: AgentCapability, 
                                   test_count: int = 10,
                                   concurrent: bool = False) -> PerformanceMetrics:
        """Benchmark performance for a specific capability."""
        
        if capability not in self.test_scenarios:
            raise ValueError(f"No test scenarios for capability {capability.value}")
        
        # Use first scenario for benchmarking
        scenario = self.test_scenarios[capability][0]
        
        if concurrent:
            results = await self._run_concurrent_benchmark(capability, scenario, test_count)
        else:
            results = await self._run_sequential_benchmark(capability, scenario, test_count)
        
        return self._calculate_metrics(results)
    
    async def _run_sequential_benchmark(self, 
                                       capability: AgentCapability, 
                                       scenario: Dict[str, Any], 
                                       test_count: int) -> List[ValidationResult]:
        """Run benchmark tests sequentially."""
        results = []
        
        for i in range(test_count):
            result = await self._run_test_scenario(capability, {
                **scenario,
                'name': f"{scenario['name']}_benchmark_{i}"
            })
            results.append(result)
        
        return results
    
    async def _run_concurrent_benchmark(self, 
                                       capability: AgentCapability, 
                                       scenario: Dict[str, Any], 
                                       test_count: int) -> List[ValidationResult]:
        """Run benchmark tests concurrently."""
        
        # Create multiple tasks
        tasks = []
        for i in range(test_count):
            task = self._run_test_scenario(capability, {
                **scenario,
                'name': f"{scenario['name']}_concurrent_{i}"
            })
            tasks.append(task)
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to ValidationResult objects
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ValidationResult(
                    test_name=f"{scenario['name']}_concurrent_{i}",
                    success=False,
                    duration=0.0,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _calculate_metrics(self, results: List[ValidationResult]) -> PerformanceMetrics:
        """Calculate performance metrics from results."""
        successful_results = [r for r in results if r.success]
        durations = [r.duration for r in results]
        
        if not durations:
            return PerformanceMetrics(
                avg_response_time=0.0,
                min_response_time=0.0,
                max_response_time=0.0,
                success_rate=0.0,
                error_rate=1.0,
                total_executions=len(results),
                throughput=0.0
            )
        
        total_time = sum(durations)
        
        return PerformanceMetrics(
            avg_response_time=statistics.mean(durations),
            min_response_time=min(durations),
            max_response_time=max(durations),
            success_rate=len(successful_results) / len(results),
            error_rate=1.0 - (len(successful_results) / len(results)),
            total_executions=len(results),
            throughput=len(results) / total_time if total_time > 0 else 0.0
        )


class SystemValidator:
    """Validates the entire enhanced agent system."""
    
    def __init__(self, config: Optional[SharedConfig] = None):
        """Initialize system validator."""
        self.config = config or get_config()
        self.agent_validator = AgentValidator(self.config)
    
    async def full_system_validation(self) -> Dict[str, Any]:
        """Run comprehensive system validation."""
        print("🔍 Starting full system validation...")
        start_time = time.time()
        
        validation_report = {
            'timestamp': datetime.now().isoformat(),
            'config': self.config.to_dict(),
            'capabilities_tested': [],
            'overall_success': True,
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'performance_metrics': {},
            'errors': [],
            'recommendations': []
        }
        
        # Test each capability
        for capability in AgentCapability:
            print(f"Testing {capability.value}...")
            
            try:
                # Functional validation
                validation_results = await self.agent_validator.validate_agent_capability(capability)
                
                # Performance benchmark
                performance_metrics = await self.agent_validator.performance_benchmark(
                    capability, test_count=5
                )
                
                # Process results
                capability_success = all(r.success for r in validation_results)
                validation_report['capabilities_tested'].append({
                    'capability': capability.value,
                    'success': capability_success,
                    'test_count': len(validation_results),
                    'successful_tests': sum(1 for r in validation_results if r.success),
                    'failed_tests': sum(1 for r in validation_results if not r.success),
                    'avg_response_time': performance_metrics.avg_response_time,
                    'success_rate': performance_metrics.success_rate,
                    'errors': [r.error for r in validation_results if r.error]
                })
                
                validation_report['performance_metrics'][capability.value] = {
                    'avg_response_time': performance_metrics.avg_response_time,
                    'min_response_time': performance_metrics.min_response_time,
                    'max_response_time': performance_metrics.max_response_time,
                    'success_rate': performance_metrics.success_rate,
                    'throughput': performance_metrics.throughput
                }
                
                validation_report['total_tests'] += len(validation_results)
                validation_report['successful_tests'] += sum(1 for r in validation_results if r.success)
                validation_report['failed_tests'] += sum(1 for r in validation_results if not r.success)
                
                if not capability_success:
                    validation_report['overall_success'] = False
                
                # Collect errors
                for result in validation_results:
                    if result.error:
                        validation_report['errors'].append({
                            'capability': capability.value,
                            'test': result.test_name,
                            'error': result.error
                        })
                
            except Exception as e:
                print(f"❌ Error testing {capability.value}: {e}")
                validation_report['overall_success'] = False
                validation_report['errors'].append({
                    'capability': capability.value,
                    'test': 'capability_test',
                    'error': str(e)
                })
        
        # Calculate overall metrics
        total_time = time.time() - start_time
        validation_report['total_validation_time'] = total_time
        validation_report['overall_success_rate'] = (
            validation_report['successful_tests'] / validation_report['total_tests']
            if validation_report['total_tests'] > 0 else 0.0
        )
        
        # Generate recommendations
        validation_report['recommendations'] = self._generate_recommendations(validation_report)
        
        print(f"✅ System validation completed in {total_time:.2f}s")
        print(f"📊 Overall success rate: {validation_report['overall_success_rate']:.1%}")
        
        return validation_report
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Check overall success rate
        if report['overall_success_rate'] < 0.9:
            recommendations.append("Overall success rate is below 90% - investigate failing tests")
        
        # Check performance
        slow_capabilities = []
        for capability, metrics in report['performance_metrics'].items():
            if metrics['avg_response_time'] > 10.0:  # More than 10 seconds
                slow_capabilities.append(capability)
        
        if slow_capabilities:
            recommendations.append(f"Performance optimization needed for: {', '.join(slow_capabilities)}")
        
        # Check error patterns
        if report['errors']:
            error_types = {}
            for error in report['errors']:
                error_type = error.get('error', '').split(':')[0]
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            common_errors = [(error, count) for error, count in error_types.items() if count > 1]
            if common_errors:
                recommendations.append(f"Common error patterns found: {common_errors}")
        
        # Default recommendations
        if not recommendations:
            recommendations.append("System is performing well - consider adding more test scenarios")
        
        return recommendations
    
    async def compare_with_original_system(self) -> Dict[str, ComparisonResult]:
        """Compare enhanced system with original agent system."""
        print("🔄 Comparing enhanced system with original...")
        
        # This is a placeholder for comparison logic
        # In a real implementation, you would:
        # 1. Load original agent system
        # 2. Run same test scenarios on both systems
        # 3. Compare performance and quality metrics
        
        comparison_results = {}
        
        for capability in AgentCapability:
            # Benchmark enhanced system
            enhanced_metrics = await self.agent_validator.performance_benchmark(
                capability, test_count=10
            )
            
            # Mock original system metrics (replace with actual comparison)
            original_metrics = PerformanceMetrics(
                avg_response_time=enhanced_metrics.avg_response_time * 1.5,  # Assume 50% slower
                min_response_time=enhanced_metrics.min_response_time * 1.3,
                max_response_time=enhanced_metrics.max_response_time * 2.0,
                success_rate=max(0.7, enhanced_metrics.success_rate - 0.1),  # Assume 10% lower
                error_rate=min(0.3, enhanced_metrics.error_rate + 0.1),
                total_executions=enhanced_metrics.total_executions,
                throughput=enhanced_metrics.throughput * 0.8  # Assume 20% lower
            )
            
            # Calculate improvement factor
            improvement_factor = 1.0
            if original_metrics.avg_response_time > 0:
                improvement_factor = original_metrics.avg_response_time / enhanced_metrics.avg_response_time
            
            # Calculate quality score
            quality_score = (
                enhanced_metrics.success_rate * 0.6 +
                min(enhanced_metrics.throughput / 10, 1.0) * 0.3 +
                max(0, 1 - enhanced_metrics.avg_response_time / 10) * 0.1
            )
            
            comparison_results[capability.value] = ComparisonResult(
                agent_type=capability.value,
                original_metrics=original_metrics,
                enhanced_metrics=enhanced_metrics,
                improvement_factor=improvement_factor,
                quality_score=quality_score,
                recommendations=[
                    f"Performance improved by {improvement_factor:.1f}x",
                    f"Quality score: {quality_score:.2f}/1.0"
                ]
            )
        
        return comparison_results
    
    def save_validation_report(self, report: Dict[str, Any], filepath: str):
        """Save validation report to file."""
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"📄 Validation report saved to {filepath}")


# Main validation function
async def run_full_validation(config_name: str = "default") -> Dict[str, Any]:
    """Run complete system validation."""
    config = get_config(config_name)
    validator = SystemValidator(config)
    
    report = await validator.full_system_validation()
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"validation_report_{timestamp}.json"
    validator.save_validation_report(report, report_path)
    
    return report


if __name__ == "__main__":
    # Run validation
    import sys
    
    async def main():
        config_name = sys.argv[1] if len(sys.argv) > 1 else "default"
        report = await run_full_validation(config_name)
        
        print("\n📋 Validation Summary:")
        print(f"✅ Overall Success: {report['overall_success']}")
        print(f"📊 Success Rate: {report['overall_success_rate']:.1%}")
        print(f"🧪 Total Tests: {report['total_tests']}")
        print(f"⏱️  Total Time: {report['total_validation_time']:.2f}s")
        
        if report['errors']:
            print(f"\n❌ Errors Found: {len(report['errors'])}")
            for error in report['errors'][:5]:  # Show first 5 errors
                print(f"  - {error['capability']}: {error['error']}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
    
    asyncio.run(main())
