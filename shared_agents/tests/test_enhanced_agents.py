"""
Enhanced Agent Testing Framework
Comprehensive test suite for the shared agent framework and VectorDBRAG integration
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any, List

# Add paths for imports
sys.path.append('/Users/cpconnor/projects/Meld and RAG')

# Import shared framework components
try:
    from shared_agents.core.agent_factory import AgentFactory, AgentCapability
    from shared_agents.core.agent_base import AgentBase, AgentResponse
    SHARED_FRAMEWORK_AVAILABLE = True
except ImportError:
    SHARED_FRAMEWORK_AVAILABLE = False

# Import VectorDBRAG components
try:
    from VectorDBRAG.agents.enhanced.enhanced_agents import CEOAgent, CodeAnalysisAgent, TriageAgent
    from VectorDBRAG.agents.enhanced.factory import EnhancedAgentFactory
    VECTORDBRAG_AVAILABLE = True
except ImportError:
    VECTORDBRAG_AVAILABLE = False


class MockOpenAIClient:
    """Mock OpenAI client for testing"""
    
    def __init__(self):
        self.chat = MagicMock()
        self.completions = MagicMock()
        
        # Setup mock response
        mock_message = MagicMock()
        mock_message.content = "Mock response from AI agent"
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        self.chat.completions.create = AsyncMock(return_value=mock_response)


@pytest.fixture
def mock_openai_client():
    """Fixture providing a mock OpenAI client"""
    return MockOpenAIClient()


@pytest.fixture
def agent_config(mock_openai_client):
    """Fixture providing standard agent configuration"""
    return {
        "openai_client": mock_openai_client,
        "model": "gpt-4",
        "api_key": "test_key",
        "temperature": 0.7,
        "max_tokens": 1000
    }


@pytest.fixture
def enhanced_factory(agent_config):
    """Fixture providing an enhanced agent factory"""
    if not VECTORDBRAG_AVAILABLE:
        pytest.skip("VectorDBRAG enhanced agents not available")
    
    return EnhancedAgentFactory(agent_config)


class TestEnhancedCEOAgent:
    """Test suite for Enhanced CEO Agent"""
    
    @pytest.fixture
    def ceo_agent(self, agent_config):
        if not VECTORDBRAG_AVAILABLE:
            pytest.skip("VectorDBRAG enhanced agents not available")
        return CEOAgent(agent_config)
    
    @pytest.mark.asyncio
    async def test_execute_with_valid_input(self, ceo_agent):
        """Test CEO agent execution with valid strategic query"""
        result = await ceo_agent._safe_execute({
            "query": "What's our Q3 strategy?",
            "context": "Company performance data showing 15% growth"
        })
        
        assert result.success is True
        assert result.result is not None
        assert len(result.result) > 0
        assert result.agent_type == "ceo"
        assert result.execution_time >= 0
    
    @pytest.mark.asyncio
    async def test_execute_with_empty_input(self, ceo_agent):
        """Test CEO agent handles empty input gracefully"""
        result = await ceo_agent._safe_execute({})
        
        assert result.success is False
        assert result.error is not None
        assert "query" in result.error.lower() or "input" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_execute_with_invalid_input(self, ceo_agent):
        """Test CEO agent handles invalid input types"""
        result = await ceo_agent._safe_execute("invalid_input")
        
        assert result.success is False
        assert result.error is not None
    
    def test_agent_capabilities(self, ceo_agent):
        """Test CEO agent has correct capabilities"""
        assert AgentCapability.STRATEGIC_PLANNING in ceo_agent.capabilities
        assert AgentCapability.BUSINESS_ANALYSIS in ceo_agent.capabilities


class TestEnhancedCodeAnalysisAgent:
    """Test suite for Enhanced Code Analysis Agent"""
    
    @pytest.fixture
    def code_agent(self, agent_config):
        if not VECTORDBRAG_AVAILABLE:
            pytest.skip("VectorDBRAG enhanced agents not available")
        return CodeAnalysisAgent(agent_config)
    
    @pytest.mark.asyncio
    async def test_analyze_python_code(self, code_agent):
        """Test code analysis with Python code"""
        code_sample = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
        
        result = await code_agent._safe_execute({
            "code": code_sample,
            "query": "Analyze this function for performance issues"
        })
        
        assert result.success is True
        assert result.result is not None
        assert result.agent_type == "code_analysis"
    
    @pytest.mark.asyncio
    async def test_analyze_without_code(self, code_agent):
        """Test code analysis without code input"""
        result = await code_agent._safe_execute({
            "query": "Analyze code"
        })
        
        assert result.success is False
        assert "code" in result.error.lower()
    
    def test_code_agent_capabilities(self, code_agent):
        """Test code analysis agent has correct capabilities"""
        assert AgentCapability.CODE_ANALYSIS in code_agent.capabilities
        assert AgentCapability.PERFORMANCE_ANALYSIS in code_agent.capabilities


class TestEnhancedAgentFactory:
    """Test suite for Enhanced Agent Factory"""
    
    def test_factory_initialization(self, enhanced_factory):
        """Test factory initializes correctly"""
        assert enhanced_factory is not None
        assert hasattr(enhanced_factory, 'config')
    
    def test_create_agent_by_type(self, enhanced_factory):
        """Test creating agents by type"""
        agent = enhanced_factory.create_agent("ceo")
        assert agent is not None
        assert agent.agent_type == "ceo"
        
        code_agent = enhanced_factory.create_agent("code_analysis")
        assert code_agent is not None
        assert code_agent.agent_type == "code_analysis"
    
    def test_create_agent_invalid_type(self, enhanced_factory):
        """Test creating agent with invalid type"""
        with pytest.raises(ValueError):
            enhanced_factory.create_agent("nonexistent_agent")
    
    def test_get_agent_types(self, enhanced_factory):
        """Test getting available agent types"""
        agent_types = enhanced_factory.get_agent_types()
        assert isinstance(agent_types, dict)
        assert "ceo" in agent_types
        assert "code_analysis" in agent_types
    
    def test_create_agents_with_capability(self, enhanced_factory):
        """Test creating agents by capability"""
        strategic_agents = enhanced_factory.create_agents_with_capability(
            AgentCapability.STRATEGIC_PLANNING
        )
        
        assert isinstance(strategic_agents, dict)
        assert len(strategic_agents) > 0
        
        # Verify at least one agent has the capability
        for agent_type, agent in strategic_agents.items():
            assert AgentCapability.STRATEGIC_PLANNING in agent.capabilities


class TestAgentIntegration:
    """Integration tests for the enhanced agent system"""
    
    @pytest.mark.asyncio
    async def test_multiple_agent_workflow(self, enhanced_factory):
        """Test workflow using multiple agents"""
        # Step 1: Use triage agent to analyze task
        triage_agent = enhanced_factory.create_agent("triage")
        triage_result = await triage_agent._safe_execute({
            "query": "I need to analyze code performance and plan improvements"
        })
        
        assert triage_result.success is True
        
        # Step 2: Use code analysis agent
        code_agent = enhanced_factory.create_agent("code_analysis")
        code_result = await code_agent._safe_execute({
            "code": "def slow_function(n): return sum(range(n))",
            "query": "Analyze performance"
        })
        
        assert code_result.success is True
        
        # Step 3: Use CEO agent for strategic planning
        ceo_agent = enhanced_factory.create_agent("ceo")
        ceo_result = await ceo_agent._safe_execute({
            "query": "Based on performance analysis, what's our improvement strategy?",
            "context": f"Analysis results: {code_result.result[:200]}"
        })
        
        assert ceo_result.success is True
    
    @pytest.mark.asyncio
    async def test_capability_based_routing(self, enhanced_factory):
        """Test automatic agent selection based on capabilities"""
        # Request code analysis capability
        agents_with_code_capability = enhanced_factory.create_agents_with_capability(
            AgentCapability.CODE_ANALYSIS
        )
        
        assert len(agents_with_code_capability) > 0
        
        # Use the first agent with code analysis capability
        agent_type, agent = next(iter(agents_with_code_capability.items()))
        result = await agent._safe_execute({
            "code": "print('hello world')",
            "query": "Review this code"
        })
        
        assert result.success is True
        assert AgentCapability.CODE_ANALYSIS in agent.capabilities


# Performance benchmarking utilities
class PerformanceBenchmark:
    """Utility class for performance benchmarking"""
    
    @staticmethod
    async def benchmark_agent(agent, test_input: Dict[str, Any], iterations: int = 5) -> Dict[str, Any]:
        """Benchmark an agent's performance"""
        import time
        
        execution_times = []
        success_count = 0
        
        for _ in range(iterations):
            start_time = time.time()
            result = await agent._safe_execute(test_input)
            end_time = time.time()
            
            execution_times.append(end_time - start_time)
            if result.success:
                success_count += 1
        
        return {
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "success_rate": success_count / iterations,
            "total_iterations": iterations
        }


@pytest.mark.performance
class TestPerformance:
    """Performance tests for enhanced agents"""
    
    @pytest.mark.asyncio
    async def test_ceo_agent_performance(self, enhanced_factory):
        """Benchmark CEO agent performance"""
        agent = enhanced_factory.create_agent("ceo")
        test_input = {
            "query": "What's our strategic direction for the next quarter?",
            "context": "Current market conditions and company performance data"
        }
        
        benchmark = await PerformanceBenchmark.benchmark_agent(agent, test_input)
        
        # Performance assertions
        assert benchmark["success_rate"] >= 0.8  # At least 80% success rate
        assert benchmark["avg_execution_time"] <= 30.0  # Under 30 seconds average
    
    @pytest.mark.asyncio
    async def test_code_agent_performance(self, enhanced_factory):
        """Benchmark code analysis agent performance"""
        agent = enhanced_factory.create_agent("code_analysis")
        test_input = {
            "code": "def example_function(data): return [x*2 for x in data if x > 0]",
            "query": "Analyze this function"
        }
        
        benchmark = await PerformanceBenchmark.benchmark_agent(agent, test_input)
        
        # Performance assertions
        assert benchmark["success_rate"] >= 0.9  # At least 90% success rate
        assert benchmark["avg_execution_time"] <= 15.0  # Under 15 seconds average


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])
