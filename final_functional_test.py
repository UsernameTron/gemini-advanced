#!/usr/bin/env python3
"""
UNIFIED AI PLATFORM - FINAL FUNCTIONAL TEST
==========================================

Comprehensive test of all functional endpoints including file upload testing.
"""

import requests
import json
import time
from datetime import datetime
from tempfile import NamedTemporaryFile

def test_file_upload():
    """Test file upload endpoint"""
    try:
        # Create a temporary test file
        with NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document for RAG processing.")
            temp_file_path = f.name
        
        # Test file upload
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            response = requests.post('http://localhost:5001/api/rag/upload', files=files)
            
        print(f"📄 File Upload Test:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ File upload test failed: {e}")
        return False

def test_all_endpoints():
    """Test all functional endpoints comprehensively"""
    
    print("🚀 UNIFIED AI PLATFORM - FINAL FUNCTIONAL TEST")
    print("=" * 60)
    
    tests = [
        # GET endpoints
        ("GET", "http://localhost:5001/", None, "Main Dashboard"),
        ("GET", "http://localhost:5001/api/status", None, "API Status"),
        ("GET", "http://localhost:5001/functional", None, "Functional Dashboard"),
        ("GET", "http://localhost:5001/health", None, "Health Check"),
        ("GET", "http://localhost:5001/api/unified/capabilities", None, "System Capabilities"),
        
        # POST endpoints with data
        ("POST", "http://localhost:5001/api/brand/analyze", {"brand_name": "Netflix"}, "Brand Analysis"),
        ("POST", "http://localhost:5001/api/brand/generate-image", {"prompt": "futuristic logo design"}, "Image Generation"),
        ("POST", "http://localhost:5001/api/rag/chat", {"message": "Explain quantum computing"}, "RAG Chat"),
        ("POST", "http://localhost:5001/api/agents/chat", {"message": "Plan a marketing strategy"}, "Agent Chat"),
        ("POST", "http://localhost:5001/api/agents/workflow", {"task": "Research competitor analysis"}, "Agent Workflow"),
    ]
    
    results = []
    
    for method, url, data, description in tests:
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json=data, timeout=10)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            success = response.status_code in [200, 201]
            status = "✅" if success else "❌"
            
            print(f"{status} {description}")
            print(f"   Status: {response.status_code} | Time: {response_time:.2f}ms")
            
            if success and method == "POST":
                try:
                    resp_json = response.json()
                    if 'mock' in resp_json:
                        print(f"   Mock Response: ✅")
                    print(f"   Response: {resp_json.get('status', 'N/A')}")
                except:
                    pass
            
            results.append({
                'test': description,
                'method': method,
                'url': url,
                'status_code': response.status_code,
                'success': success,
                'response_time_ms': response_time
            })
            
        except Exception as e:
            print(f"❌ {description}")
            print(f"   Error: {str(e)}")
            results.append({
                'test': description,
                'method': method,
                'url': url,
                'success': False,
                'error': str(e)
            })
    
    # Test file upload separately
    print("\n📄 Testing File Upload...")
    upload_success = test_file_upload()
    
    # Calculate summary
    successful_tests = sum(1 for r in results if r.get('success', False))
    total_tests = len(results)
    
    if upload_success:
        successful_tests += 1
        total_tests += 1
    
    success_rate = (successful_tests / total_tests) * 100
    
    print("\n" + "=" * 60)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Platform Status: {'🟢 OPERATIONAL' if success_rate >= 90 else '🟡 DEGRADED' if success_rate >= 70 else '🔴 CRITICAL'}")
    
    # Save results
    report = {
        'timestamp': datetime.now().isoformat(),
        'test_summary': {
            'total_tests': total_tests,
            'successful': successful_tests,
            'failed': total_tests - successful_tests,
            'success_rate': success_rate
        },
        'test_results': results,
        'file_upload_test': upload_success
    }
    
    filename = f"final_functional_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Detailed report saved to: {filename}")

if __name__ == "__main__":
    test_all_endpoints()
