# File: core/base_agents.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import asyncio
import json
from datetime import datetime
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    """Standardized response format for all agents"""
    success: bool
    data: Any = None
    error_message: Optional[str] = None
    execution_time: float = 0
    metadata: Dict[str, Any] = None

class AgentBase(ABC):
    """
    Base class for all our specialized agents.
    Every agent knows how to execute its specific task and return standardized results.
    """
    
    def __init__(self, agent_config: Dict[str, Any] = None):
        self.config = agent_config or {}
        self.agent_id = f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Execute the agent's core functionality"""
        pass
        
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate that the agent has the input it needs"""
        return input_data is not None

class AgentManager:
    """
    Central coordinator for all our agents.
    This manager knows which agents are available and can create them on demand.
    """
    
    def __init__(self):
        self.registered_agents = {}
        self.agent_instances = {}
        
    def register_agent(self, agent_type: str, agent_class):
        """Register a new agent type that can be created later"""
        self.registered_agents[agent_type] = agent_class
        logger.info(f"Registered agent type: {agent_type}")
        
    def create_agent(self, agent_type: str, config: Dict[str, Any] = None) -> AgentBase:
        """Create a new agent instance of the specified type"""
        if agent_type not in self.registered_agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
            
        agent_class = self.registered_agents[agent_type]
        agent_instance = agent_class(config)
        
        self.agent_instances[agent_instance.agent_id] = agent_instance
        logger.info(f"Created agent: {agent_instance.agent_id}")
        
        return agent_instance
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all registered and active agents"""
        return {
            'registered_types': list(self.registered_agents.keys()),
            'active_instances': len(self.agent_instances),
            'instance_details': {
                agent_id: type(agent).__name__ 
                for agent_id, agent in self.agent_instances.items()
            }
        }

# File: core/workflow_base.py

class WorkflowStep:
    """
    Represents a single step in our brand analysis pipeline.
    Each step knows what agent to use and how to prepare its input.
    """
    
    def __init__(self, step_name: str, agent_type: str, input_transformer=None):
        self.step_name = step_name
        self.agent_type = agent_type
        self.input_transformer = input_transformer or (lambda x: x)
        
    def prepare_input(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Transform previous results into input for this step's agent"""
        return self.input_transformer(workflow_results)

class BrandDeconstructionWorkflow:
    """
    Orchestrates the complete brand analysis pipeline.
    This is the main conductor that coordinates all our specialized agents.
    """
    
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.steps = []
        self.results_history = []
        
    def add_step(self, step: WorkflowStep):
        """Add a new step to our analysis pipeline"""
        self.steps.append(step)
        logger.info(f"Added workflow step: {step.step_name}")
        
    async def execute_workflow(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete brand deconstruction pipeline.
        This is where the magic happens - each step builds on the previous one.
        """
        results = {'initial_input': initial_input}
        start_time = datetime.now()
        
        logger.info(f"Starting brand deconstruction workflow with {len(self.steps)} steps")
        
        try:
            for i, step in enumerate(self.steps):
                step_start = datetime.now()
                logger.info(f"Executing step {i+1}/{len(self.steps)}: {step.step_name}")
                
                # Create agent for this step
                agent = self.agent_manager.create_agent(step.agent_type)
                
                # Prepare input using previous results
                step_input = step.prepare_input(results)
                
                # Execute the agent
                step_result = await agent.execute(step_input)
                
                # Store results
                results[step.step_name] = step_result
                
                step_duration = (datetime.now() - step_start).total_seconds()
                logger.info(f"Step {step.step_name} completed in {step_duration:.2f} seconds")
                
                # If any step fails, we stop the pipeline
                if not step_result.success:
                    logger.error(f"Step {step.step_name} failed: {step_result.error_message}")
                    break
                    
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            results['workflow_error'] = str(e)
            
        total_duration = (datetime.now() - start_time).total_seconds()
        results['execution_metadata'] = {
            'total_duration': total_duration,
            'steps_completed': len([r for r in results.values() if isinstance(r, AgentResponse) and r.success]),
            'execution_timestamp': start_time.isoformat()
        }
        
        self.results_history.append(results)
        return results
