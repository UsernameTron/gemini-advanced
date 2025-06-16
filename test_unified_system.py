#!/usr/bin/env python3
"""
Comprehensive Integration Test for Unified Meld & RAG Web Interface
Tests all components working together: agents, vector DB, session management, and web interface
"""

import requests
import json
import time
import sys
import os
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:5002"
TEST_TIMEOUT = 30

class UnifiedSystemTester:
    """Comprehensive tester for the unified system."""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name, success, details="", response_time=0):
        """Log test results."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({response_time:.2f}s)")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_time": response_time
        })
    
    def test_health_check(self):
        """Test system health endpoint."""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health", timeout=TEST_TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('status') in ['healthy', 'degraded']
                components = data.get('components', {})
                details = f"Status: {data.get('status')}, Components: {len(components)} active"
                self.log_test("Health Check", success, details, response_time)
                return success
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_unified_dashboard_load(self):
        """Test that the main unified dashboard loads."""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/", timeout=TEST_TIMEOUT)
            response_time = time.time() - start_time
            
            success = response.status_code == 200 and "Unified Meld & RAG" in response.text
            details = f"HTTP {response.status_code}, Contains expected content: {success}"
            self.log_test("Unified Dashboard Load", success, details, response_time)
            return success
        except Exception as e:
            self.log_test("Unified Dashboard Load", False, f"Error: {str(e)}")
            return False
    
    def test_session_status(self):
        """Test session management functionality."""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/session/status", timeout=TEST_TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False) and 'session_id' in data
                session_data = data.get('session_data', {})
                systems_status = data.get('systems_status', {})
                details = f"Session ID: {data.get('session_id', '')[:8]}..., Systems: {sum(systems_status.values())}/3 active"
                self.log_test("Session Management", success, details, response_time)
                return success, data
            else:
                self.log_test("Session Management", False, f"HTTP {response.status_code}", response_time)
                return False, None
        except Exception as e:
            self.log_test("Session Management", False, f"Error: {str(e)}")
            return False, None
    
    def test_vector_stores(self):
        """Test vector store listing functionality."""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/unified/vector-stores", timeout=TEST_TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                vector_stores = data.get('vector_stores', [])
                details = f"Found {len(vector_stores)} vector stores"
                self.log_test("Vector Stores Listing", success, details, response_time)
                return success, vector_stores
            else:
                self.log_test("Vector Stores Listing", False, f"HTTP {response.status_code}", response_time)
                return False, []
        except Exception as e:
            self.log_test("Vector Stores Listing", False, f"Error: {str(e)}")
            return False, []
    
    def test_agent_chat(self, agent_types=None):
        """Test agent chat functionality."""
        if agent_types is None:
            agent_types = ['research', 'ceo', 'performance', 'triage']
        
        all_success = True
        for agent_type in agent_types:
            try:
                start_time = time.time()
                
                payload = {
                    "message": f"Hello, this is a test message for the {agent_type} agent. Please respond briefly.",
                    "agent_type": agent_type,
                    "use_knowledge_base": False,
                    "vector_store_ids": []
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/unified/chat",
                    json=payload,
                    timeout=TEST_TIMEOUT
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    success = data.get('success', False) and len(data.get('response', '')) > 0
                    agent_name = data.get('agent_name', 'Unknown')
                    exec_time = data.get('execution_time', 0)
                    details = f"Agent: {agent_name}, Response length: {len(data.get('response', ''))}, Exec time: {exec_time:.2f}s"
                    self.log_test(f"Agent Chat ({agent_type})", success, details, response_time)
                    if not success:
                        all_success = False
                else:
                    self.log_test(f"Agent Chat ({agent_type})", False, f"HTTP {response.status_code}", response_time)
                    all_success = False
                    
                # Small delay between agent tests
                time.sleep(1)
                
            except Exception as e:
                self.log_test(f"Agent Chat ({agent_type})", False, f"Error: {str(e)}")
                all_success = False
        
        return all_success
    
    def test_knowledge_base_integration(self, vector_stores):
        """Test knowledge base integration in chat."""
        if not vector_stores:
            self.log_test("Knowledge Base Integration", False, "No vector stores available")
            return False
        
        try:
            start_time = time.time()
            
            payload = {
                "message": "What information do you have in the knowledge base? Please search and provide a brief summary.",
                "agent_type": "research",
                "use_knowledge_base": True,
                "vector_store_ids": [vector_stores[0].get('id', '')]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/unified/chat",
                json=payload,
                timeout=TEST_TIMEOUT
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                used_kb = data.get('used_knowledge_base', False)
                details = f"KB Used: {used_kb}, Response length: {len(data.get('response', ''))}"
                self.log_test("Knowledge Base Integration", success, details, response_time)
                return success
            else:
                self.log_test("Knowledge Base Integration", False, f"HTTP {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_test("Knowledge Base Integration", False, f"Error: {str(e)}")
            return False
    
    def test_preferences_update(self):
        """Test user preferences functionality."""
        try:
            start_time = time.time()
            
            payload = {
                "theme": "dark",
                "default_agent": "ceo",
                "search_type": "semantic"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/unified/preferences",
                json=payload,
                timeout=TEST_TIMEOUT
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                preferences = data.get('preferences', {})
                details = f"Updated {len(preferences)} preferences"
                self.log_test("Preferences Update", success, details, response_time)
                return success
            else:
                self.log_test("Preferences Update", False, f"HTTP {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_test("Preferences Update", False, f"Error: {str(e)}")
            return False
    
    def test_legacy_compatibility(self):
        """Test that legacy endpoints still work."""
        legacy_endpoints = [
            ("/dashboard", "AI Agent Dashboard"),
            ("/analytics", "Analytics")
        ]
        
        all_success = True
        for endpoint, expected_content in legacy_endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=TEST_TIMEOUT)
                response_time = time.time() - start_time
                
                success = response.status_code == 200 and expected_content in response.text
                details = f"HTTP {response.status_code}, Content check: {success}"
                self.log_test(f"Legacy Endpoint {endpoint}", success, details, response_time)
                if not success:
                    all_success = False
            except Exception as e:
                self.log_test(f"Legacy Endpoint {endpoint}", False, f"Error: {str(e)}")
                all_success = False
        
        return all_success
    
    def run_comprehensive_test(self):
        """Run all tests and provide comprehensive report."""
        print("🚀 Starting Comprehensive Unified System Test")
        print("=" * 60)
        
        # Test 1: Health Check
        health_ok = self.test_health_check()
        
        # Test 2: Dashboard Load
        dashboard_ok = self.test_unified_dashboard_load()
        
        # Test 3: Session Management
        session_ok, session_data = self.test_session_status()
        
        # Test 4: Vector Stores
        vector_ok, vector_stores = self.test_vector_stores()
        
        # Test 5: Agent Chat (multiple agents)
        agent_ok = self.test_agent_chat(['research', 'ceo', 'performance', 'triage'])
        
        # Test 6: Knowledge Base Integration
        kb_ok = self.test_knowledge_base_integration(vector_stores)
        
        # Test 7: Preferences
        pref_ok = self.test_preferences_update()
        
        # Test 8: Legacy Compatibility
        legacy_ok = self.test_legacy_compatibility()
        
        # Generate Report
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n🔍 COMPONENT STATUS:")
        components = {
            "Core System Health": health_ok,
            "Web Interface": dashboard_ok,
            "Session Management": session_ok,
            "Vector Database": vector_ok,
            "AI Agents": agent_ok,
            "Knowledge Base": kb_ok,
            "User Preferences": pref_ok,
            "Legacy Compatibility": legacy_ok
        }
        
        for component, status in components.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {component}")
        
        print("\n⚡ PERFORMANCE METRICS:")
        avg_response_time = sum(r['response_time'] for r in self.test_results) / len(self.test_results)
        max_response_time = max(r['response_time'] for r in self.test_results)
        print(f"Average Response Time: {avg_response_time:.2f}s")
        print(f"Maximum Response Time: {max_response_time:.2f}s")
        
        overall_success = all(components.values())
        
        print(f"\n🎯 OVERALL STATUS: {'✅ SYSTEM OPERATIONAL' if overall_success else '❌ SYSTEM ISSUES DETECTED'}")
        
        if not overall_success:
            print("\n🔧 RECOMMENDATIONS:")
            if not health_ok:
                print("- Check system health and OpenAI API connectivity")
            if not vector_ok:
                print("- Verify vector database initialization")
            if not agent_ok:
                print("- Check agent system configuration")
            if not kb_ok:
                print("- Ensure knowledge base has content for testing")
        
        return overall_success, {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'components': components,
            'performance': {
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time
            }
        }


def main():
    """Main test execution function."""
    print("🧪 Unified Meld & RAG System Integration Test")
    print("This test validates all components of the unified system")
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding properly at {BASE_URL}")
            print("🔧 Please start the unified interface first:")
            print("   python start_unified_interface.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("🔧 Please start the unified interface first:")
        print("   python start_unified_interface.py")
        sys.exit(1)
    
    # Run comprehensive tests
    tester = UnifiedSystemTester(BASE_URL)
    success, report = tester.run_comprehensive_test()
    
    # Save detailed report
    report_file = Path("unified_system_test_report.json")
    with open(report_file, 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'test_results': tester.test_results,
            'summary': report
        }, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
