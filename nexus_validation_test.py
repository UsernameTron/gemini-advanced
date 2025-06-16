#!/usr/bin/env python3
"""
NEXUS AI Platform - Endpoint Validation Test
Comprehensive testing of all NEXUS endpoints and functionality
"""

import requests
import json
import time
from typing import Dict, Any

class NexusValidator:
    def __init__(self, base_url: str = "http://localhost:5003"):
        self.base_url = base_url
        self.results = []
        
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test a single endpoint and return results"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            end_time = time.time()
            response_time = end_time - start_time
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "success": response.status_code == 200,
                "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]
            }
            
            if not result["success"]:
                result["error"] = f"HTTP {response.status_code}: {response.text[:100]}"
                
        except requests.exceptions.RequestException as e:
            result = {
                "endpoint": endpoint,
                "method": method,
                "success": False,
                "error": str(e),
                "response_time": 0
            }
        
        self.results.append(result)
        return result
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all NEXUS endpoints"""
        print("🚀 Starting NEXUS AI Platform Validation")
        print("=" * 50)
        
        # Test main dashboard
        print("📊 Testing Main Dashboard...")
        dashboard_result = self.test_endpoint("/nexus")
        print(f"   NEXUS Dashboard: {'✅' if dashboard_result['success'] else '❌'}")
        
        # Test API endpoints
        print("\n🔗 Testing API Endpoints...")
        
        api_tests = [
            ("/api/nexus/system-status", "GET", None),
            ("/api/nexus/agent-metrics", "GET", None),
            ("/api/nexus/knowledge-base", "GET", None),
            ("/api/nexus/chat", "POST", {
                "message": "Test NEXUS chat functionality",
                "agent_type": "research"
            })
        ]
        
        for endpoint, method, data in api_tests:
            result = self.test_endpoint(endpoint, method, data)
            print(f"   {endpoint}: {'✅' if result['success'] else '❌'} ({result['response_time']}s)")
            
            if not result['success']:
                print(f"      Error: {result.get('error', 'Unknown error')}")
        
        # Test legacy endpoints for compatibility
        print("\n🔄 Testing Legacy Compatibility...")
        legacy_tests = [
            ("/health", "GET", None),
            ("/", "GET", None),
            ("/dashboard", "GET", None)
        ]
        
        for endpoint, method, data in legacy_tests:
            result = self.test_endpoint(endpoint, method, data)
            print(f"   {endpoint}: {'✅' if result['success'] else '❌'}")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 50)
        print("📋 NEXUS Validation Summary")
        print("=" * 50)
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r['success']])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests} ✅")
        print(f"Failed: {failed_tests} {'❌' if failed_tests > 0 else '✅'}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Response time analysis
        response_times = [r['response_time'] for r in self.results if r['success']]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"Average Response Time: {avg_response_time:.3f}s")
        
        # Failed tests details
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"   {result['endpoint']}: {result.get('error', 'Unknown error')}")
        
        # Success indicators
        nexus_endpoints = [r for r in self.results if '/nexus' in r['endpoint']]
        nexus_success = all(r['success'] for r in nexus_endpoints)
        
        print(f"\n🎯 NEXUS Core Functionality: {'✅ OPERATIONAL' if nexus_success else '❌ ISSUES DETECTED'}")
        
        # API validation
        api_endpoints = [r for r in self.results if '/api/nexus' in r['endpoint']]
        api_success = all(r['success'] for r in api_endpoints)
        
        print(f"🔗 NEXUS API Layer: {'✅ OPERATIONAL' if api_success else '❌ ISSUES DETECTED'}")
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': (successful_tests/total_tests)*100,
            'nexus_operational': nexus_success,
            'api_operational': api_success,
            'avg_response_time': avg_response_time if response_times else 0
        }

def main():
    """Main validation function"""
    print("🔮 NEXUS AI Platform - Endpoint Validation")
    print("Testing all NEXUS endpoints and functionality...\n")
    
    validator = NexusValidator()
    
    try:
        validator.run_comprehensive_test()
        print("\n🎉 NEXUS validation completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Validation interrupted by user")
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")

if __name__ == "__main__":
    main()
