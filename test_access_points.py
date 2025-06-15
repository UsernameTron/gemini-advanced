#!/usr/bin/env python3
"""
UNIFIED AI PLATFORM - ACCESS POINTS TESTING
==========================================

Comprehensive testing of all platform access points and functionality.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class UnifiedPlatformTester:
    """Test all access points and functionality of the Unified AI Platform"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.results = {
            'test_timestamp': datetime.now().isoformat(),
            'base_url': base_url,
            'endpoints_tested': [],
            'functional_tests': [],
            'summary': {}
        }
    
    def test_endpoint(self, endpoint: str, method: str = 'GET', data: Dict = None, description: str = "") -> Dict[str, Any]:
        """Test a single endpoint and return results"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = requests.get(url, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, timeout=10)
            else:
                response = requests.request(method, url, json=data, timeout=10)
            
            response_time = time.time() - start_time
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'description': description,
                'status_code': response.status_code,
                'response_time_ms': round(response_time * 1000, 2),
                'success': response.status_code == 200,
                'content_type': response.headers.get('content-type', ''),
                'response_size': len(response.content),
                'timestamp': datetime.now().isoformat()
            }
            
            # Try to parse JSON response
            try:
                result['response_data'] = response.json()
            except:
                result['response_text'] = response.text[:500]  # First 500 chars
            
            return result
            
        except Exception as e:
            return {
                'endpoint': endpoint,
                'method': method,
                'description': description,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all access points"""
        print("🧪 Starting Comprehensive Access Points Testing...")
        print("=" * 60)
        
        # Core Access Points
        self.test_core_access_points()
        
        # Functional API Endpoints
        self.test_functional_endpoints()
        
        # Additional System Endpoints
        self.test_system_endpoints()
        
        # Generate summary
        self.generate_summary()
        
        # Print results
        self.print_results()
        
        # Save results
        self.save_results()
    
    def test_core_access_points(self):
        """Test the main access points"""
        print("🔍 Testing Core Access Points...")
        
        core_endpoints = [
            ('/', 'GET', 'Main Dashboard'),
            ('/api/status', 'GET', 'API Status'),
            ('/api/unified/status', 'GET', 'Functional Status'),
            ('/api/mindmeld/agents', 'GET', 'MindMeld Agents'),
            ('/api/systems', 'GET', 'Systems Information'),
            ('/functional', 'GET', 'Functional Dashboard')
        ]
        
        for endpoint, method, description in core_endpoints:
            result = self.test_endpoint(endpoint, method, description=description)
            self.results['endpoints_tested'].append(result)
            
            status = "✅" if result.get('success') else "❌"
            print(f"  {status} {endpoint} - {description}")
    
    def test_functional_endpoints(self):
        """Test functional API endpoints"""
        print("\n🔧 Testing Functional API Endpoints...")
        
        functional_tests = [
            # Brand System
            ('/api/brand/analyze', 'POST', {'brand_name': 'TestBrand'}, 'Brand Analysis'),
            ('/api/brand/generate-image', 'POST', {'prompt': 'Test image'}, 'Image Generation'),
            
            # RAG System
            ('/api/rag/chat', 'POST', {'message': 'Hello'}, 'RAG Chat'),
            ('/api/rag/upload', 'POST', {}, 'Document Upload (empty)'),
            
            # Agent System
            ('/api/agents/chat', 'POST', {'message': 'Hello agents'}, 'Agent Chat'),
            ('/api/agents/workflow', 'POST', {'task': 'Test task'}, 'Agent Workflow'),
            
            # Unified System
            ('/api/unified/capabilities', 'GET', None, 'System Capabilities')
        ]
        
        for endpoint, method, data, description in functional_tests:
            result = self.test_endpoint(endpoint, method, data, description)
            self.results['functional_tests'].append(result)
            
            status = "✅" if result.get('success') else "❌"
            response_info = ""
            if result.get('response_data'):
                if 'error' in result['response_data']:
                    response_info = f" (Error: {result['response_data']['error']})"
                elif result.get('success'):
                    response_info = " (Success)"
            
            print(f"  {status} {method} {endpoint} - {description}{response_info}")
    
    def test_system_endpoints(self):
        """Test additional system endpoints"""
        print("\n⚙️ Testing Additional System Endpoints...")
        
        system_endpoints = [
            ('/api/test', 'GET', 'Test Endpoint'),
            ('/api/functional/status', 'GET', 'Functional Integration Status'),
            ('/health', 'GET', 'Health Check'),
            ('/api/health', 'GET', 'API Health Check')
        ]
        
        for endpoint, method, description in system_endpoints:
            result = self.test_endpoint(endpoint, method, description=description)
            self.results['endpoints_tested'].append(result)
            
            status = "✅" if result.get('success') else "❌"
            print(f"  {status} {endpoint} - {description}")
    
    def generate_summary(self):
        """Generate test summary"""
        all_tests = self.results['endpoints_tested'] + self.results['functional_tests']
        
        total_tests = len(all_tests)
        successful_tests = len([t for t in all_tests if t.get('success')])
        failed_tests = total_tests - successful_tests
        
        avg_response_time = 0
        if total_tests > 0:
            response_times = [t.get('response_time_ms', 0) for t in all_tests if t.get('response_time_ms')]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': round((successful_tests / total_tests) * 100, 1) if total_tests > 0 else 0,
            'average_response_time_ms': round(avg_response_time, 2),
            'platform_status': 'operational' if successful_tests >= total_tests * 0.7 else 'degraded'
        }
    
    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("📊 UNIFIED AI PLATFORM - ACCESS POINTS TEST RESULTS")
        print("=" * 60)
        
        summary = self.results['summary']
        print(f"🎯 Test Summary:")
        print(f"   • Total Tests: {summary['total_tests']}")
        print(f"   • Successful: {summary['successful_tests']}")
        print(f"   • Failed: {summary['failed_tests']}")
        print(f"   • Success Rate: {summary['success_rate']}%")
        print(f"   • Avg Response Time: {summary['average_response_time_ms']}ms")
        print(f"   • Platform Status: {summary['platform_status'].upper()}")
        
        print(f"\n🌐 Verified Access Points:")
        working_endpoints = [t for t in self.results['endpoints_tested'] + self.results['functional_tests'] if t.get('success')]
        for test in working_endpoints:
            method = test.get('method', 'GET')
            endpoint = test.get('endpoint', '')
            description = test.get('description', '')
            response_time = test.get('response_time_ms', 0)
            print(f"   ✅ {method} {self.base_url}{endpoint} - {description} ({response_time}ms)")
        
        print(f"\n❌ Failed Endpoints:")
        failed_endpoints = [t for t in self.results['endpoints_tested'] + self.results['functional_tests'] if not t.get('success')]
        for test in failed_endpoints:
            method = test.get('method', 'GET')
            endpoint = test.get('endpoint', '')
            description = test.get('description', '')
            error = test.get('error', 'Unknown error')
            status_code = test.get('status_code', 'N/A')
            print(f"   ❌ {method} {self.base_url}{endpoint} - {description} (Status: {status_code})")
            if 'response_data' in test and 'error' in test['response_data']:
                print(f"      Error: {test['response_data']['error']}")
        
        print("\n" + "=" * 60)
    
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'access_points_test_report_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Results saved to: {filename}")

def main():
    """Run the comprehensive access points test"""
    tester = UnifiedPlatformTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
