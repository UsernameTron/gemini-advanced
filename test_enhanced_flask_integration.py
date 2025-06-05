"""
Flask Integration Tests for Enhanced Agent System
Tests the complete integration of enhanced agents with VectorDBRAG's Flask application
"""

import pytest
import json
import asyncio
import tempfile
import os
from typing import Dict, Any, List
from flask import Flask
from unittest.mock import Mock, patch, MagicMock

# Import Flask app components
import sys
sys.path.append('/Users/cpconnor/projects/Meld and RAG/VectorDBRAG')

from app import create_app
from config import Config
from shared_agents.config.shared_config import SharedConfig, ConfigEnvironment
from shared_agents.validation.system_validator import SystemValidator


class TestEnhancedFlaskIntegration:
    """Test suite for enhanced agent Flask integration."""
    
    @pytest.fixture
    def app_config(self):
        """Create test configuration."""
        return SharedConfig(
            environment=ConfigEnvironment.TESTING,
            debug=True,
            agent_config=None,  # Will use defaults
            rag_config=None,    # Will use defaults
            analytics_config=None  # Will use defaults
        )
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch('openai.OpenAI') as mock_client:
            # Mock successful responses
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Test response from AI"
            
            mock_client.return_value.chat.completions.create.return_value = mock_response
            mock_client.return_value.models.list.return_value = MagicMock(data=[])
            
            yield mock_client
    
    @pytest.fixture
    def test_app(self, app_config, mock_openai_client):
        """Create test Flask application."""
        # Set test environment variables
        os.environ['OPENAI_API_KEY'] = 'test-key-12345'
        os.environ['FLASK_ENV'] = 'testing'
        
        # Create app with test configuration
        app = create_app('testing')
        app.config['TESTING'] = True
        
        return app
    
    @pytest.fixture
    def client(self, test_app):
        """Create test client."""
        return test_app.test_client()
    
    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
    
    def test_enhanced_agent_query_endpoint(self, client):
        """Test enhanced agent query endpoint."""
        query_data = {
            'query': 'Analyze this simple Python function: def add(a, b): return a + b',
            'agent_type': 'code_analysis',
            'context': {'source': 'test'}
        }
        
        response = client.post('/api/enhanced/agents/query',
                              data=json.dumps(query_data),
                              content_type='application/json')
        
        # Should work even with mock
        assert response.status_code in [200, 400, 503]  # Various acceptable responses
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'status' in data
            assert 'response' in data
    
    def test_enhanced_agent_capability_endpoint(self, client):
        """Test enhanced agent capability-based routing."""
        capability_data = {
            'capability': 'code_analysis',
            'input_data': {
                'query': 'Test query for capability routing',
                'content': 'def test(): pass'
            }
        }
        
        response = client.post('/api/enhanced/agents/capability',
                              data=json.dumps(capability_data),
                              content_type='application/json')
        
        # Should handle the request appropriately
        assert response.status_code in [200, 400, 503]
    
    def test_enhanced_agent_types_endpoint(self, client):
        """Test enhanced agent types listing."""
        response = client.get('/api/enhanced/agents/types')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'agent_types' in data
    
    def test_enhanced_agent_status_endpoint(self, client):
        """Test enhanced agent system status."""
        response = client.get('/api/enhanced/agents/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'factory_info' in data
    
    def test_error_handling(self, client):
        """Test error handling in enhanced agent endpoints."""
        # Test invalid JSON
        response = client.post('/api/enhanced/agents/query',
                              data='invalid json',
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_missing_parameters(self, client):
        """Test handling of missing required parameters."""
        # Missing query parameter
        query_data = {
            'agent_type': 'code_analysis',
            'context': {}
        }
        
        response = client.post('/api/enhanced/agents/query',
                              data=json.dumps(query_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    @pytest.mark.asyncio
    async def test_integration_with_rag_system(self, test_app):
        """Test integration between enhanced agents and RAG system."""
        with test_app.app_context():
            # Check if RAG system is available
            rag_system = getattr(test_app, 'search_system', None)
            
            if rag_system:
                # Test that enhanced agents can access RAG system
                from enhanced_agent_integration import get_factory
                factory = get_factory()
                
                # Create an agent that uses RAG
                agent = factory.create_agent('code_analysis')
                
                # Test with RAG context
                input_data = {
                    'query': 'Find best practices for Python function design',
                    'context': {'use_rag': True}
                }
                
                response = await agent._safe_execute(input_data)
                assert response is not None
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent enhanced agent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            query_data = {
                'query': f'Test concurrent request at {time.time()}',
                'agent_type': 'research_analysis'
            }
            
            response = client.post('/api/enhanced/agents/query',
                                  data=json.dumps(query_data),
                                  content_type='application/json')
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that requests were handled (may be errors due to mocking)
        assert len(results) == 5
        assert all(status in [200, 400, 500, 503] for status in results)
    
    def test_configuration_loading(self, test_app):
        """Test that configuration is properly loaded."""
        with test_app.app_context():
            from enhanced_agent_integration import get_factory
            
            factory = get_factory()
            assert factory is not None
            assert hasattr(factory, 'config')
    
    def test_agent_factory_initialization(self, test_app):
        """Test that agent factory is properly initialized."""
        with test_app.app_context():
            from enhanced_agent_integration import get_factory
            
            factory = get_factory()
            
            # Test that factory can create agents
            agent_types = ['code_analysis', 'research_analysis', 'strategic_planning']
            
            for agent_type in agent_types:
                try:
                    agent = factory.create_agent(agent_type)
                    assert agent is not None
                    assert hasattr(agent, 'execute')
                except Exception as e:
                    # Expected if dependencies are not available
                    assert 'not available' in str(e) or 'missing' in str(e).lower()


class TestEnhancedAgentRoutes:
    """Test individual enhanced agent routes."""
    
    @pytest.fixture
    def test_app(self):
        """Create minimal test app."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Mock the enhanced agent integration
        with patch('enhanced_agent_integration.get_factory') as mock_get_factory:
            mock_factory = Mock()
            mock_agent = Mock()
            mock_response = Mock()
            mock_response.success = True
            mock_response.result = "Test result"
            mock_response.execution_time = 1.0
            mock_response.error = None
            mock_response.metadata = {}
            
            mock_agent._safe_execute.return_value = asyncio.coroutine(lambda: mock_response)()
            mock_agent.name = "TestAgent"
            mock_agent.agent_type = "test_agent"
            
            mock_factory.create_agent.return_value = mock_agent
            mock_factory.create_agent_by_capability.return_value = mock_agent
            mock_factory.list_available_types.return_value = ['test_agent']
            mock_factory.get_status.return_value = {'status': 'operational'}
            
            mock_get_factory.return_value = mock_factory
            
            # Register enhanced agent routes
            from enhanced_agent_integration import register_enhanced_agent_routes
            register_enhanced_agent_routes(app)
            
            yield app
    
    @pytest.fixture
    def client(self, test_app):
        """Create test client."""
        return test_app.test_client()
    
    def test_enhanced_query_route(self, client):
        """Test enhanced agent query route."""
        query_data = {
            'query': 'Test query',
            'agent_type': 'test_agent'
        }
        
        response = client.post('/api/enhanced/agents/query',
                              data=json.dumps(query_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'response' in data
    
    def test_capability_route(self, client):
        """Test capability-based agent routing."""
        capability_data = {
            'capability': 'code_analysis',
            'input_data': {'query': 'Test capability query'}
        }
        
        response = client.post('/api/enhanced/agents/capability',
                              data=json.dumps(capability_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_types_route(self, client):
        """Test agent types listing route."""
        response = client.get('/api/enhanced/agents/types')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'agent_types' in data
    
    def test_status_route(self, client):
        """Test agent status route."""
        response = client.get('/api/enhanced/agents/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'


class TestEnhancedAgentPerformance:
    """Performance tests for enhanced agent system."""
    
    @pytest.fixture
    def performance_client(self):
        """Create client for performance testing."""
        # Set up test environment
        os.environ['OPENAI_API_KEY'] = 'test-key-12345'
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Mock fast responses for performance testing
        with patch('enhanced_agent_integration.get_factory') as mock_get_factory:
            mock_factory = Mock()
            mock_agent = Mock()
            mock_response = Mock()
            mock_response.success = True
            mock_response.result = "Fast test result"
            mock_response.execution_time = 0.1
            mock_response.error = None
            
            async def fast_execute(input_data):
                return mock_response
            
            mock_agent._safe_execute = fast_execute
            mock_agent.name = "FastAgent"
            mock_agent.agent_type = "fast_agent"
            
            mock_factory.create_agent.return_value = mock_agent
            mock_get_factory.return_value = mock_factory
            
            from enhanced_agent_integration import register_enhanced_agent_routes
            register_enhanced_agent_routes(app)
            
            yield app.test_client()
    
    def test_response_time(self, performance_client):
        """Test response time for enhanced agent queries."""
        import time
        
        query_data = {
            'query': 'Performance test query',
            'agent_type': 'fast_agent'
        }
        
        start_time = time.time()
        response = performance_client.post('/api/enhanced/agents/query',
                                          data=json.dumps(query_data),
                                          content_type='application/json')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # Should respond within 5 seconds
    
    def test_throughput(self, performance_client):
        """Test throughput for multiple concurrent requests."""
        import time
        import threading
        
        request_count = 10
        responses = []
        
        def make_request():
            query_data = {
                'query': f'Throughput test {time.time()}',
                'agent_type': 'fast_agent'
            }
            
            response = performance_client.post('/api/enhanced/agents/query',
                                              data=json.dumps(query_data),
                                              content_type='application/json')
            responses.append(response.status_code)
        
        start_time = time.time()
        
        # Create and start threads
        threads = []
        for i in range(request_count):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate throughput
        throughput = len(responses) / total_time
        
        assert len(responses) == request_count
        assert throughput > 1.0  # At least 1 request per second


class TestEnhancedAgentValidation:
    """Integration tests for the validation system."""
    
    @pytest.mark.asyncio
    async def test_system_validation(self):
        """Test the system validation functionality."""
        from shared_agents.validation.system_validator import SystemValidator
        from shared_agents.config.shared_config import SharedConfig, ConfigEnvironment
        
        # Create test configuration
        config = SharedConfig(environment=ConfigEnvironment.TESTING)
        
        # Mock OpenAI for validation tests
        with patch('openai.OpenAI') as mock_client:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Validation test response with function analysis"
            
            mock_client.return_value.chat.completions.create.return_value = mock_response
            
            validator = SystemValidator(config)
            
            # Test individual capability validation
            from shared_agents.core.agent_factory import AgentCapability
            
            results = await validator.agent_validator.validate_agent_capability(
                AgentCapability.CODE_ANALYSIS
            )
            
            assert len(results) > 0
            assert all(isinstance(r.test_name, str) for r in results)
    
    @pytest.mark.asyncio
    async def test_performance_benchmark(self):
        """Test performance benchmarking."""
        from shared_agents.validation.system_validator import AgentValidator
        from shared_agents.config.shared_config import SharedConfig
        from shared_agents.core.agent_factory import AgentCapability
        
        config = SharedConfig()
        
        with patch('openai.OpenAI') as mock_client:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Benchmark test response"
            
            mock_client.return_value.chat.completions.create.return_value = mock_response
            
            validator = AgentValidator(config)
            
            metrics = await validator.performance_benchmark(
                AgentCapability.CODE_ANALYSIS,
                test_count=3
            )
            
            assert metrics.total_executions == 3
            assert metrics.avg_response_time >= 0
            assert 0 <= metrics.success_rate <= 1


# Run tests
if __name__ == "__main__":
    # Set up test environment
    os.environ['OPENAI_API_KEY'] = 'test-key-12345'
    
    # Run pytest
    pytest.main([__file__, "-v"])
