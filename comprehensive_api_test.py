#!/usr/bin/env python3
"""
Comprehensive API Testing Suite for UnifiedAI Platform
Tests all APIs configured in .env file with detailed reporting
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
import subprocess
import sys

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class APITestSuite:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'test_summary': {},
            'detailed_results': {},
            'recommendations': []
        }
        self.success_count = 0
        self.total_tests = 0
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_openai_api(self):
        """Test OpenAI API functionality"""
        self.log("Testing OpenAI API...")
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            result = {'status': 'FAILED', 'error': 'No API key found', 'models': 0}
            self.results['detailed_results']['openai'] = result
            return result
            
        try:
            # Test with openai library
            import openai
            client = openai.OpenAI(api_key=api_key)
            
            # List models
            models = client.models.list()
            model_names = [model.id for model in models.data]
            
            # Test a simple completion
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'API test successful'"}],
                max_tokens=10
            )
            
            result = {
                'status': 'SUCCESS',
                'models_available': len(model_names),
                'test_model': 'gpt-3.5-turbo',
                'test_response': response.choices[0].message.content.strip() if response.choices[0].message.content else "No response",
                'sample_models': model_names[:5]
            }
            self.success_count += 1
            
        except Exception as e:
            result = {
                'status': 'FAILED',
                'error': str(e),
                'models': 0
            }
            
        self.total_tests += 1
        self.results['detailed_results']['openai'] = result
        return result
        
    def test_anthropic_api(self):
        """Test Anthropic Claude API"""
        self.log("Testing Anthropic API...")
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            result = {'status': 'FAILED', 'error': 'No API key found'}
            self.results['detailed_results']['anthropic'] = result
            return result
            
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            # Test a simple message
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say 'API test successful'"}]
            )
            
            result = {
                'status': 'SUCCESS',
                'test_model': 'claude-3-haiku-20240307',
                'test_response': message.content[0].text.strip() if hasattr(message.content[0], 'text') else str(message.content[0]),
                'available_models': ['claude-3-haiku-20240307', 'claude-3-sonnet-20240229', 'claude-3-opus-20240229']
            }
            self.success_count += 1
            
        except Exception as e:
            result = {
                'status': 'FAILED',
                'error': str(e)
            }
            
        self.total_tests += 1
        self.results['detailed_results']['anthropic'] = result
        return result
        
    def test_google_gemini_api(self):
        """Test Google Gemini API"""
        self.log("Testing Google Gemini API...")
        api_key = os.getenv('GOOGLE_API_KEY')
        
        if not api_key:
            result = {'status': 'FAILED', 'error': 'No API key found'}
            self.results['detailed_results']['google_gemini'] = result
            return result
            
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # List available models
            models = list(genai.list_models())
            model_names = [model.name for model in models if 'generateContent' in model.supported_generation_methods]
            
            if not model_names:
                result = {
                    'status': 'FAILED',
                    'error': 'No content generation models available',
                    'all_models': [model.name for model in models]
                }
            else:
                # Test with gemini-1.5-flash (the recommended replacement)
                test_model_name = None
                for model_name in model_names:
                    if 'gemini-1.5-flash' in model_name:
                        test_model_name = model_name
                        break
                
                if not test_model_name:
                    # Fall back to first available model
                    test_model_name = model_names[0]
                
                model = genai.GenerativeModel(test_model_name)
                response = model.generate_content("Say 'API test successful'")
                
                result = {
                    'status': 'SUCCESS',
                    'models_available': len(model_names),
                    'test_model': test_model_name,
                    'test_response': response.text.strip() if hasattr(response, 'text') else "Generated successfully",
                    'available_models': model_names[:5]
                }
                self.success_count += 1
                
        except Exception as e:
            result = {
                'status': 'FAILED',
                'error': str(e),
                'error_type': type(e).__name__
            }
            
        self.total_tests += 1
        self.results['detailed_results']['google_gemini'] = result
        return result
        
    def test_ollama_api(self):
        """Test Ollama local API"""
        self.log("Testing Ollama API...")
        
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        default_model = os.getenv('OLLAMA_DEFAULT_MODEL', 'phi3.5')
        
        try:
            # Check if Ollama is running
            health_response = requests.get(f"{base_url}/api/version", timeout=5)
            
            if health_response.status_code != 200:
                result = {
                    'status': 'FAILED',
                    'error': f'Ollama server not responding: {health_response.status_code}'
                }
            else:
                # List available models
                models_response = requests.get(f"{base_url}/api/tags", timeout=10)
                models_data = models_response.json()
                available_models = [model['name'] for model in models_data.get('models', [])]
                
                if not available_models:
                    result = {
                        'status': 'FAILED',
                        'error': 'No models available in Ollama',
                        'server_version': health_response.json()
                    }
                else:
                    # Test generation with default model or first available
                    test_model = default_model if default_model in [m.split(':')[0] for m in available_models] else available_models[0]
                    
                    generate_payload = {
                        "model": test_model,
                        "prompt": "Say 'API test successful'",
                        "stream": False
                    }
                    
                    generate_response = requests.post(
                        f"{base_url}/api/generate",
                        json=generate_payload,
                        timeout=60  # Increased timeout for generation
                    )
                    
                    if generate_response.status_code == 200:
                        response_data = generate_response.json()
                        result = {
                            'status': 'SUCCESS',
                            'models_available': len(available_models),
                            'test_model': test_model,
                            'test_response': response_data.get('response', '').strip(),
                            'available_models': available_models,
                            'server_version': health_response.json()
                        }
                        self.success_count += 1
                    else:
                        result = {
                            'status': 'FAILED',
                            'error': f'Generation failed: {generate_response.status_code}',
                            'available_models': available_models
                        }
                        
        except Exception as e:
            result = {
                'status': 'FAILED',
                'error': str(e),
                'error_type': type(e).__name__
            }
            
        self.total_tests += 1
        self.results['detailed_results']['ollama'] = result
        return result
        
    def test_redis_connection(self):
        """Test Redis connection"""
        self.log("Testing Redis connection...")
        
        try:
            import redis
            
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            
            r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            
            # Test basic operations
            r.set('test_key', 'API test successful')
            test_value = r.get('test_key')
            r.delete('test_key')
            
            # Get Redis info
            info = r.info()
            
            result = {
                'status': 'SUCCESS',
                'test_response': test_value,
                'redis_version': info.get('redis_version'),
                'connected_clients': info.get('connected_clients'),
                'host': redis_host,
                'port': redis_port
            }
            self.success_count += 1
            
        except Exception as e:
            result = {
                'status': 'FAILED',
                'error': str(e),
                'error_type': type(e).__name__
            }
            
        self.total_tests += 1
        self.results['detailed_results']['redis'] = result
        return result
        
    def test_flask_endpoints(self):
        """Test Flask application endpoints"""
        self.log("Testing Flask endpoints...")
        
        base_url = "http://localhost:5002"
        endpoints_to_test = [
            "/health",
            "/api/session/status",
            "/api/agents/status", 
            "/api/unified/vector-stores",
            "/dashboard",
            "/analytics"
        ]
        
        endpoint_results = {}
        successful_endpoints = 0
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    endpoint_results[endpoint] = {
                        'status': 'SUCCESS',
                        'status_code': response.status_code,
                        'response_size': len(response.text)
                    }
                    successful_endpoints += 1
                else:
                    endpoint_results[endpoint] = {
                        'status': 'FAILED',
                        'status_code': response.status_code,
                        'error': response.text[:200]
                    }
                    
            except Exception as e:
                endpoint_results[endpoint] = {
                    'status': 'FAILED',
                    'error': str(e),
                    'error_type': type(e).__name__
                }
        
        if successful_endpoints > 0:
            self.success_count += 1
            
        result = {
            'status': 'SUCCESS' if successful_endpoints > len(endpoints_to_test) // 2 else 'PARTIAL',
            'successful_endpoints': successful_endpoints,
            'total_endpoints': len(endpoints_to_test),
            'success_rate': f"{(successful_endpoints/len(endpoints_to_test)*100):.1f}%",
            'endpoint_details': endpoint_results
        }
        
        self.total_tests += 1
        self.results['detailed_results']['flask_endpoints'] = result
        return result
        
    def run_all_tests(self):
        """Run all API tests"""
        self.log("Starting comprehensive API testing suite...")
        start_time = time.time()
        
        # Test all APIs
        tests = [
            ("OpenAI", self.test_openai_api),
            ("Anthropic", self.test_anthropic_api),
            ("Google Gemini", self.test_google_gemini_api),
            ("Ollama", self.test_ollama_api),
            ("Redis", self.test_redis_connection),
            ("Flask Endpoints", self.test_flask_endpoints)
        ]
        
        for test_name, test_func in tests:
            self.log(f"Running {test_name} test...")
            result = test_func()
            status_color = "✅" if result['status'] == 'SUCCESS' else "❌" if result['status'] == 'FAILED' else "⚠️"
            self.log(f"{status_color} {test_name}: {result['status']}")
            
        # Calculate summary
        execution_time = time.time() - start_time
        success_rate = (self.success_count / self.total_tests * 100) if self.total_tests > 0 else 0
        
        self.results['test_summary'] = {
            'total_tests': self.total_tests,
            'successful_tests': self.success_count,
            'failed_tests': self.total_tests - self.success_count,
            'success_rate': f"{success_rate:.1f}%",
            'execution_time_seconds': round(execution_time, 2)
        }
        
        # Generate recommendations
        self._generate_recommendations()
        
        return self.results
        
    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        for api_name, result in self.results['detailed_results'].items():
            if result['status'] == 'FAILED':
                if api_name == 'google_gemini':
                    recommendations.append("Google Gemini API: Check API key validity and model availability. Consider updating to newer model names.")
                elif api_name == 'ollama':
                    recommendations.append("Ollama API: Ensure Ollama server is running locally on port 11434 and models are installed.")
                elif api_name == 'redis':
                    recommendations.append("Redis: Start Redis server locally or update connection settings.")
                elif api_name == 'flask_endpoints':
                    recommendations.append("Flask Endpoints: Ensure the Flask application is running on port 5002.")
                else:
                    recommendations.append(f"{api_name.title()} API: Verify API key and network connectivity.")
                    
        if not recommendations:
            recommendations.append("All APIs are functioning correctly! System is production-ready.")
            
        self.results['recommendations'] = recommendations
        
    def save_report(self):
        """Save detailed test report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_api_test_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        return filename
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🚀 COMPREHENSIVE API TEST RESULTS")
        print("="*60)
        
        summary = self.results['test_summary']
        print(f"📊 Total Tests: {summary['total_tests']}")
        print(f"✅ Successful: {summary['successful_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}")
        print(f"📈 Success Rate: {summary['success_rate']}")
        print(f"⏱️ Execution Time: {summary['execution_time_seconds']}s")
        
        print("\n📋 DETAILED RESULTS:")
        print("-"*40)
        
        for api_name, result in self.results['detailed_results'].items():
            status_icon = "✅" if result['status'] == 'SUCCESS' else "❌" if result['status'] == 'FAILED' else "⚠️"
            print(f"{status_icon} {api_name.upper().replace('_', ' ')}: {result['status']}")
            
            if result['status'] == 'SUCCESS':
                if 'models_available' in result:
                    print(f"   📚 Models Available: {result['models_available']}")
                if 'test_response' in result:
                    print(f"   💬 Test Response: {result['test_response']}")
            else:
                if 'error' in result:
                    print(f"   ❗ Error: {result['error']}")
                    
        print("\n💡 RECOMMENDATIONS:")
        print("-"*40)
        for i, rec in enumerate(self.results['recommendations'], 1):
            print(f"{i}. {rec}")
            
        print("\n" + "="*60)

def main():
    """Main execution function"""
    print("🔍 UnifiedAI Platform - Comprehensive API Testing Suite")
    print("Testing all APIs configured in .env file...\n")
    
    # Install required packages if not available
    required_packages = ['openai', 'anthropic', 'google-generativeai', 'redis', 'requests', 'python-dotenv']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    
    # Run tests
    test_suite = APITestSuite()
    results = test_suite.run_all_tests()
    
    # Display results
    test_suite.print_summary()
    
    # Save report
    report_file = test_suite.save_report()
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    return results

if __name__ == "__main__":
    main()
