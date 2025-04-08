"""
Integration module for CrewAI with GroqCloud.

This module provides functions to integrate CrewAI with GroqCloud
for use in the Kern Resources project.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Import the GroqCloud provider
try:
    from providers.groq_provider import GroqCloudProvider
    GROQ_PROVIDER_AVAILABLE = True
except ImportError:
    logger.warning("GroqCloudProvider not available.")
    GROQ_PROVIDER_AVAILABLE = False

# Try to import CrewAI classes, but don't fail if they're not installed
try:
    from crewai import Agent, Task, Crew, Process
    from crewai.llm import BaseLLM
    CREWAI_AVAILABLE = True
except ImportError:
    logger.warning("CrewAI not available. Please install it with 'pip install crewai'.")
    CREWAI_AVAILABLE = False
    
    # Create placeholder classes for type hints
    class Agent:
        pass
    class Task:
        pass
    class Crew:
        pass
    class Process:
        pass
    class BaseLLM:
        pass

class CrewAIIntegration:
    """
    Integration class for CrewAI with GroqCloud.
    
    This class provides methods to create and manage CrewAI agents and crews
    using the GroqCloud provider for the Kern Resources project.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the CrewAI integration.
        
        Args:
            config: Configuration dictionary with settings for the integration.
        """
        self.config = config or {}
        
        # Check if CrewAI is available
        if not CREWAI_AVAILABLE:
            logger.error("CrewAI is not available. Please install it with 'pip install crewai'.")
            return
        
        # Check if GroqCloud provider is available
        if not GROQ_PROVIDER_AVAILABLE:
            logger.error("GroqCloudProvider is not available.")
            return
        
        # Initialize the GroqCloud provider
        self.llm = self._create_llm()
        
        logger.info("CrewAI integration initialized")
    
    def _create_llm(self) -> Optional[BaseLLM]:
        """Create the LLM provider based on configuration."""
        # Get API key from config or environment
        api_key = self.config.get("api_key") or os.environ.get("GROQ_API_KEY")
        if not api_key:
            logger.error("GroqCloud API key not provided and GROQ_API_KEY environment variable not set.")
            return None
        
        # Get model from config or use default
        model = self.config.get("model", "meta-llama/llama-4-scout-17b-16e-instruct")
        
        # Get other parameters from config or use defaults
        temperature = self.config.get("temperature", 0.7)
        max_tokens = self.config.get("max_tokens", 4096)
        
        # Create the provider
        try:
            provider = GroqCloudProvider(
                api_key=api_key,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            logger.info(f"Created GroqCloudProvider with model: {model}")
            return provider
        except Exception as e:
            logger.error(f"Failed to create GroqCloudProvider: {e}")
            return None
    
    def create_agent(self, role: str, goal: str, backstory: str, verbose: bool = True) -> Optional[Agent]:
        """
        Create a CrewAI agent with the GroqCloud provider.
        
        Args:
            role: The role of the agent.
            goal: The goal of the agent.
            backstory: The backstory of the agent.
            verbose: Whether to enable verbose output.
            
        Returns:
            A CrewAI Agent object, or None if creation fails.
        """
        if not CREWAI_AVAILABLE:
            logger.error("CrewAI is not available.")
            return None
        
        if not self.llm:
            logger.error("LLM provider not initialized.")
            return None
        
        try:
            agent = Agent(
                role=role,
                goal=goal,
                backstory=backstory,
                verbose=verbose,
                llm=self.llm
            )
            logger.info(f"Created agent with role: {role}")
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            return None
    
    def create_task(self, description: str, agent: Agent, expected_output: str = None, 
                   context: List[Task] = None) -> Optional[Task]:
        """
        Create a CrewAI task.
        
        Args:
            description: The description of the task.
            agent: The agent to assign the task to.
            expected_output: The expected output of the task.
            context: A list of tasks that provide context for this task.
            
        Returns:
            A CrewAI Task object, or None if creation fails.
        """
        if not CREWAI_AVAILABLE:
            logger.error("CrewAI is not available.")
            return None
        
        try:
            task = Task(
                description=description,
                agent=agent,
                expected_output=expected_output,
                context=context
            )
            logger.info(f"Created task: {description[:50]}...")
            return task
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return None
    
    def create_crew(self, agents: List[Agent], process: str = "sequential", 
                   verbose: int = 2) -> Optional[Crew]:
        """
        Create a CrewAI crew.
        
        Args:
            agents: A list of agents to include in the crew.
            process: The process to use for task execution ("sequential" or "hierarchical").
            verbose: The verbosity level (0-2).
            
        Returns:
            A CrewAI Crew object, or None if creation fails.
        """
        if not CREWAI_AVAILABLE:
            logger.error("CrewAI is not available.")
            return None
        
        try:
            # Convert process string to Process enum
            process_enum = Process.sequential
            if process.lower() == "hierarchical":
                process_enum = Process.hierarchical
            
            crew = Crew(
                agents=agents,
                process=process_enum,
                verbose=verbose
            )
            logger.info(f"Created crew with {len(agents)} agents")
            return crew
        except Exception as e:
            logger.error(f"Failed to create crew: {e}")
            return None
    
    def run_crew(self, crew: Crew, tasks: List[Task]) -> Optional[str]:
        """
        Run a CrewAI crew with the specified tasks.
        
        Args:
            crew: The crew to run.
            tasks: The tasks to assign to the crew.
            
        Returns:
            The result of the crew's work, or None if execution fails.
        """
        if not CREWAI_AVAILABLE:
            logger.error("CrewAI is not available.")
            return None
        
        try:
            logger.info(f"Running crew with {len(tasks)} tasks")
            result = crew.kickoff(tasks=tasks)
            logger.info("Crew execution completed")
            return result
        except Exception as e:
            logger.error(f"Failed to run crew: {e}")
            return None


# Example usage
def create_default_integration() -> CrewAIIntegration:
    """Create a default CrewAI integration with GroqCloud."""
    config = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "temperature": 0.7,
        "max_tokens": 4096
    }
    return CrewAIIntegration(config)
