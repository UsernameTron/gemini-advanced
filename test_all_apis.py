#!/usr/bin/env python3
"""
Comprehensive API Testing Suite for UnifiedAI Platform
Tests all APIs configured in .env file
"""

import os
import sys
import json
import time
import asyncio
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class APITestingSuite:
    """Comprehensive API testing for all configured services"""
    
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        
        print("🧪 COMPREHENSIVE API TESTING SUITE")
        print("=" * 60)
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Testing all APIs configured in .env file")
        print("=" * 60)
    
    def test_openai_api(self) -> Dict[str, Any]:
        """Test OpenAI API connectivity and functionality"""
        print("\n🤖 Testing OpenAI API...")
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {'status': 'FAILED', 'error': 'No API key configured'}
        
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            
            # Test basic completion
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'OpenAI API test successful' in exactly those words."}
                ],
                max_tokens=50
            )
            
            result = response.choices[0].message.content.strip()
            
            # Test models list
            models = client.models.list()
            available_models = [model.id for model in models.data[:5]]  # First 5 models
            
            return {
                'status': 'SUCCESS',
                'response': result,
                'available_models': available_models,
                'model_count': len(models.data),
                'api_key_valid': True
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'api_key_configured': bool(api_key)
            }
    
    def test_anthropic_api(self) -> Dict[str, Any]:
        """Test Anthropic Claude API connectivity and functionality"""
        print("\n🧠 Testing Anthropic API...")
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return {'status': 'FAILED', 'error': 'No API key configured'}
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            # Test basic completion
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=50,
                messages=[
                    {"role": "user", "content": "Say 'Anthropic API test successful' in exactly those words."}
                ]
            )
            
            result = response.content[0].text.strip()
            
            return {
                'status': 'SUCCESS',
                'response': result,
                'model': 'claude-3-haiku-20240307',
                'api_key_valid': True
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'api_key_configured': bool(api_key)
            }
    
    def test_google_gemini_api(self) -> Dict[str, Any]:
        """Test Google Gemini API connectivity and functionality"""
        print("\n🌟 Testing Google Gemini API...")
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return {'status': 'FAILED', 'error': 'No API key configured'}
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Test basic generation
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Say 'Google Gemini API test successful' in exactly those words.")
            
            result = response.text.strip()
            
            # List available models
            available_models = []
            for model_info in genai.list_models():
                if 'generateContent' in model_info.supported_generation_methods:
                    available_models.append(model_info.name)
            
            return {
                'status': 'SUCCESS',
                'response': result,
                'available_models': available_models[:5],  # First 5 models
                'model_count': len(available_models),
                'api_key_valid': True
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'api_key_configured': bool(api_key)
            }
    
    def test_ollama_api(self) -> Dict[str, Any]:
        """Test Ollama local API connectivity and functionality"""
        print("\n🏠 Testing Ollama Local API...")
        
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        default_model = os.getenv('OLLAMA_DEFAULT_MODEL', 'phi3.5')
        
        try:
            # Test if Ollama server is running
            health_response = requests.get(f"{base_url}/api/version", timeout=5)
            
            if health_response.status_code != 200:
                return {
                    'status': 'FAILED',
                    'error': f'Ollama server not responding: {health_response.status_code}'
                }
            
            # Get available models
            models_response = requests.get(f"{base_url}/api/tags", timeout=10)
            available_models = []
            
            if models_response.status_code == 200:
                models_data = models_response.json()
                available_models = [model['name'] for model in models_data.get('models', [])]
            
            # Test generation if models are available
            if available_models:
                test_model = default_model if default_model in available_models else available_models[0]
                
                generate_payload = {
                    "model": test_model,
                    "prompt": "Say 'Ollama API test successful' in exactly those words.",
                    "stream": False
                }
                
                generate_response = requests.post(
                    f"{base_url}/api/generate", 
                    json=generate_payload, 
                    timeout=30
                )
                
                if generate_response.status_code == 200:
                    result = generate_response.json().get('response', '').strip()
                    
                    return {
                        'status': 'SUCCESS',
                        'response': result,
                        'available_models': available_models,
                        'model_used': test_model,
                        'server_running': True
                    }
                else:
                    return {
                        'status': 'PARTIAL',
                        'error': f'Generation failed: {generate_response.status_code}',
                        'available_models': available_models,
                        'server_running': True
                    }
            else:
                return {
                    'status': 'PARTIAL',
                    'warning': 'Ollama server running but no models available',
                    'server_running': True,
                    'available_models': []
                }
                
        except requests.exceptions.ConnectionError:
            return {
                'status': 'FAILED',
                'error': 'Ollama server not running or not accessible',
                'server_running': False,
                'base_url': base_url
            }
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'base_url': base_url
            }
    
    def test_redis_connection(self) -> Dict[str, Any]:
        """Test Redis connectivity for session management"""
        print("\n📦 Testing Redis Connection...")
        
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_url = os.getenv('REDIS_URL', f'redis://{redis_host}:{redis_port}/0')
        
        try:
            import redis
            
            # Test direct connection
            r = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
            
            # Test ping
            pong = r.ping()
            
            # Test set/get
            test_key = 'api_test_' + str(int(time.time()))
            test_value = 'Redis API test successful'
            
            r.set(test_key, test_value, ex=10)  # Expire in 10 seconds
            retrieved_value = r.get(test_key)
            
            # Clean up
            r.delete(test_key)
            
            # Get server info
            info = r.info()
            
            return {
                'status': 'SUCCESS',
                'ping_response': pong,
                'set_get_test': retrieved_value == test_value,
                'redis_version': info.get('redis_version'),
                'connected_clients': info.get('connected_clients'),
                'used_memory_human': info.get('used_memory_human'),
                'connection_config': {
                    'host': redis_host,
                    'port': redis_port,
                    'url': redis_url
                }
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'connection_config': {
                    'host': redis_host,
                    'port': redis_port,
                    'url': redis_url
                }
            }
    
    def test_local_flask_api(self) -> Dict[str, Any]:
        """Test local Flask API endpoints"""
        print("\n🌐 Testing Local Flask API...")
        
        base_url = 'http://localhost:5002'  # Our current server port
        
        endpoints_to_test = [
            ('Health Check', '/health'),
            ('Root Dashboard', '/'),
            ('Agent Status', '/api/agents/status'),
            ('Voice Profiles', '/api/voice/profiles'),
            ('TTS Status', '/api/tts/status'),
            ('Session Status', '/api/session/status')
        ]
        
        results = {}
        working_endpoints = 0
        total_endpoints = len(endpoints_to_test)
        
        for name, endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                
                if response.status_code == 200:
                    working_endpoints += 1
                    results[endpoint] = {
                        'status': 'SUCCESS',
                        'status_code': response.status_code,
                        'content_type': response.headers.get('content-type', 'unknown'),
                        'response_size': len(response.content)
                    }
                else:
                    results[endpoint] = {
                        'status': 'FAILED',
                        'status_code': response.status_code,
                        'error': f'HTTP {response.status_code}'
                    }
                    
            except Exception as e:
                results[endpoint] = {
                    'status': 'FAILED',
                    'error': str(e)
                }
        
        success_rate = working_endpoints / total_endpoints
        
        return {
            'status': 'SUCCESS' if success_rate > 0.8 else 'PARTIAL' if success_rate > 0.5 else 'FAILED',
            'success_rate': success_rate,
            'working_endpoints': working_endpoints,
            'total_endpoints': total_endpoints,
            'endpoint_results': results,
            'base_url': base_url
        }
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all API tests and generate comprehensive report"""
        
        print("\n🚀 RUNNING COMPREHENSIVE API TESTS")
        print("-" * 60)
        
        # Test all APIs
        api_tests = {
            'openai': self.test_openai_api,
            'anthropic': self.test_anthropic_api,
            'google_gemini': self.test_google_gemini_api,
            'ollama': self.test_ollama_api,
            'redis': self.test_redis_connection,
            'flask_api': self.test_local_flask_api
        }
        
        test_results = {}
        successful_apis = 0
        total_apis = len(api_tests)
        
        for api_name, test_func in api_tests.items():
            try:
                result = test_func()
                test_results[api_name] = result
                
                if result['status'] == 'SUCCESS':
                    successful_apis += 1
                    print(f"   ✅ {api_name.upper()}: {result['status']}")
                elif result['status'] == 'PARTIAL':
                    print(f"   ⚠️  {api_name.upper()}: {result['status']} - {result.get('warning', 'Partial functionality')}")
                else:
                    print(f"   ❌ {api_name.upper()}: {result['status']} - {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results[api_name] = {
                    'status': 'ERROR',
                    'error': f'Test execution failed: {str(e)}'
                }
                print(f"   💥 {api_name.upper()}: ERROR - {str(e)}")
        
        # Calculate overall success metrics
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        overall_report = {
            'execution_summary': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'successful_apis': successful_apis,
                'total_apis': total_apis,
                'success_rate': successful_apis / total_apis
            },
            'api_test_results': test_results,
            'environment_config': {
                'openai_configured': bool(os.getenv('OPENAI_API_KEY')),
                'anthropic_configured': bool(os.getenv('ANTHROPIC_API_KEY')),
                'google_configured': bool(os.getenv('GOOGLE_API_KEY')),
                'ollama_url': os.getenv('OLLAMA_BASE_URL'),
                'redis_host': os.getenv('REDIS_HOST'),
                'flask_env': os.getenv('FLASK_ENV')
            }
        }
        
        # Save detailed report
        report_filename = f'api_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_filename, 'w') as f:
            json.dump(overall_report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏆 API TESTING COMPLETE")
        print("=" * 60)
        print(f"Duration: {duration}")
        print(f"APIs Tested: {total_apis}")
        print(f"Successful: {successful_apis}")
        print(f"Success Rate: {successful_apis/total_apis*100:.1f}%")
        print(f"Detailed Report: {report_filename}")
        
        if successful_apis == total_apis:
            print("🎉 ALL APIS WORKING PERFECTLY!")
        elif successful_apis >= total_apis * 0.8:
            print("✅ MOST APIS WORKING - SYSTEM OPERATIONAL")
        elif successful_apis >= total_apis * 0.5:
            print("⚠️  PARTIAL FUNCTIONALITY - SOME APIS NEED ATTENTION")
        else:
            print("❌ MULTIPLE API ISSUES - SYSTEM NEEDS REPAIR")
        
        return overall_report

def main():
    """Main execution function"""
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please ensure .env file exists with API configurations.")
        return
    
    # Initialize and run tests
    tester = APITestingSuite()
    results = tester.run_comprehensive_tests()
    
    # Print key insights
    print("\n📊 KEY INSIGHTS:")
    print("-" * 40)
    
    for api_name, result in results['api_test_results'].items():
        status = result['status']
        if status == 'SUCCESS':
            if api_name == 'openai':
                print(f"• OpenAI: {result.get('model_count', 0)} models available")
            elif api_name == 'anthropic':
                print(f"• Anthropic: Claude models accessible")
            elif api_name == 'google_gemini':
                print(f"• Google Gemini: {result.get('model_count', 0)} models available")
            elif api_name == 'ollama':
                print(f"• Ollama: {len(result.get('available_models', []))} local models")
            elif api_name == 'redis':
                print(f"• Redis: v{result.get('redis_version', 'unknown')} running")
            elif api_name == 'flask_api':
                print(f"• Flask API: {result.get('success_rate', 0)*100:.1f}% endpoints working")
    
    return results

if __name__ == "__main__":
    results = main()
