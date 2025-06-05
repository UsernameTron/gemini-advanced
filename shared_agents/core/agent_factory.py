"""
Core shared agent framework extracted from MindMeld for use in VectorDBRAG enhancement.
This provides a unified agent interface that both systems can use.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
import json
import time
import uuid
import asyncio
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Agent capabilities enumeration."""
    # Code-related capabilities
    CODE_ANALYSIS = "code_analysis"
    CODE_DEBUGGING = "code_debugging"
    CODE_REPAIR = "code_repair"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    TEST_GENERATION = "test_generation"
    
    # Content generation and processing
    TEXT_GENERATION = "text_generation"
    DATA_PROCESSING = "data_processing"
    DOCUMENTATION = "documentation"
    
    # Research and analysis
    RESEARCH = "research"
    TESTING = "testing"
    DEBUGGING = "debugging"
    
    # Strategic capabilities
    STRATEGIC_PLANNING = "strategic_planning"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"
    
    # Multimodal capabilities
    AUDIO_PROCESSING = "audio_processing"
    IMAGE_PROCESSING = "image_processing"
    SPEECH_ANALYSIS = "speech_analysis"
    VISUAL_ANALYSIS = "visual_analysis"
    
    # Memory and knowledge
    VECTOR_SEARCH = "vector_search"
    RAG_PROCESSING = "rag_processing"


@dataclass
class AgentResponse:
    """Standardized agent response format."""
    success: bool
    result: Any
    agent_type: str
    timestamp: str
    execution_time: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ValidationError(Exception):
    """Raised when agent input/output validation fails."""
    pass


class AgentExecutionError(Exception):
    """Raised when agent execution fails."""
    pass


class AgentBase(ABC):
    """
    Enhanced base agent class that provides a unified interface for both 
    MindMeld and VectorDBRAG agents.
    
    Combines the best features from both systems:
    - MindMeld's structured validation and testing framework
    - VectorDBRAG's capability system and statistics tracking
    """
    
    def __init__(
        self, 
        name: str,
        agent_type: str,
        config: Dict[str, Any],
        capabilities: Optional[List[AgentCapability]] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            name: Human-readable agent name
            agent_type: Unique agent type identifier
            config: Agent configuration dictionary
            capabilities: List of agent capabilities
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.agent_type = agent_type
        self.config = config
        self.capabilities = capabilities or []
        
        # Statistics tracking (from VectorDBRAG)
        self.created_at = time.time()
        self.total_executions = 0
        self.successful_executions = 0
        self.conversation_history = []
        
        # Configuration validation
        self.validate_config()
    
    def validate_config(self) -> None:
        """
        Validate agent configuration. Override in subclasses for specific validation.
        
        Raises:
            ValidationError: If configuration is invalid
        """
        required_fields = getattr(self, 'REQUIRED_CONFIG_FIELDS', [])
        for field in required_fields:
            if field not in self.config:
                raise ValidationError(f"Missing required config field: {field}")
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Execute the agent's primary task.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            AgentResponse with execution results
            
        Raises:
            AgentExecutionError: If execution fails
        """
        pass
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data. Override in subclasses for specific validation.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def validate_output(self, output_data: Any) -> bool:
        """
        Validate output data. Override in subclasses for specific validation.
        
        Args:
            output_data: Output data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def add_capability(self, capability: AgentCapability) -> None:
        """Add a capability to the agent."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.capabilities
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent execution statistics."""
        success_rate = (
            (self.successful_executions / self.total_executions * 100) 
            if self.total_executions > 0 else 0
        )
        return {
            "id": self.id,
            "name": self.name,
            "agent_type": self.agent_type,
            "capabilities": [cap.value for cap in self.capabilities],
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "success_rate": round(success_rate, 2),
            "uptime": time.time() - self.created_at,
            "created_at": datetime.fromtimestamp(self.created_at).isoformat()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    async def _safe_execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Safely execute the agent with error handling and statistics tracking.
        
        Args:
            input_data: Input data for execution
            
        Returns:
            AgentResponse with execution results
        """
        start_time = time.time()
        self.total_executions += 1
        
        try:
            # Validate input
            if not self.validate_input(input_data):
                raise ValidationError("Input validation failed")
            
            # Execute the agent
            result = await self.execute(input_data)
            
            # Validate output
            if not self.validate_output(result.result):
                raise ValidationError("Output validation failed")
            
            self.successful_executions += 1
            result.execution_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Agent {self.name} execution failed: {str(e)}")
            
            return AgentResponse(
                success=False,
                result=None,
                agent_type=self.agent_type,
                timestamp=self._get_timestamp(),
                execution_time=execution_time,
                error=str(e),
                metadata={"input_data": input_data}
            )


class AgentFactory:
    """
    Enhanced agent factory that provides type-safe agent creation and management.
    """
    
    _agents: Dict[str, type] = {}
    _input_types: Dict[str, str] = {}
    
    @classmethod
    def register_agent(
        cls, 
        agent_type: str, 
        agent_class: type, 
        input_type: str = "dict"
    ) -> None:
        """
        Register an agent type with the factory.
        
        Args:
            agent_type: Unique identifier for the agent type
            agent_class: Agent class to instantiate
            input_type: Expected input type (file, directory, string, dict, etc.)
        """
        if not issubclass(agent_class, AgentBase):
            raise ValueError(f"Agent class must inherit from AgentBase")
        
        cls._agents[agent_type] = agent_class
        cls._input_types[agent_type] = input_type
        logger.info(f"Registered agent type: {agent_type}")
    
    @classmethod
    def create_agent(cls, agent_type: str, config: Dict[str, Any]) -> AgentBase:
        """
        Create an agent instance.
        
        Args:
            agent_type: Type of agent to create
            config: Configuration for the agent
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If agent type is not registered
        """
        if agent_type not in cls._agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = cls._agents[agent_type]
        return agent_class(
            name=config.get('name', agent_type),
            agent_type=agent_type,
            config=config
        )
    
    @classmethod
    def get_registered_agents(cls) -> List[str]:
        """Get list of registered agent types."""
        return list(cls._agents.keys())
    
    @classmethod
    def get_input_type(cls, agent_type: str) -> Optional[str]:
        """Get expected input type for an agent."""
        return cls._input_types.get(agent_type)
    
    @classmethod
    def get_agent_info(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered agents."""
        return {
            agent_type: {
                "class": agent_class.__name__,
                "input_type": cls._input_types.get(agent_type, "unknown"),
                "capabilities": getattr(agent_class, 'DEFAULT_CAPABILITIES', [])
            }
            for agent_type, agent_class in cls._agents.items()
        }


# Export main classes
__all__ = [
    'AgentBase',
    'AgentFactory', 
    'AgentResponse',
    'AgentCapability',
    'ValidationError',
    'AgentExecutionError'
]
