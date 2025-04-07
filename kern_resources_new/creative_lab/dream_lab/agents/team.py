"""
Multi-agent team setup for the Dream Lab module.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Try to import CrewAI components
try:
    from crewai import Agent, Crew, Task
    CREWAI_AVAILABLE = True
except ImportError:
    logger.warning("CrewAI not available. Using placeholder classes.")
    CREWAI_AVAILABLE = False
    
    # Create placeholder classes if CrewAI is not installed
    class Agent:
        def __init__(self, role="", goal="", backstory="", llm=None):
            self.role = role
            self.goal = goal
            self.backstory = backstory
            self.llm = llm
            
    class Crew:
        def __init__(self, agents=None):
            self.agents = agents or []
            
        def kickoff(self, tasks=None):
            return "CrewAI not available. This is a placeholder response."
            
    class Task:
        def __init__(self, description="", agent=None):
            self.description = description
            self.agent = agent

# Try to import OllamaProvider
try:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from creative_lab.llama4_exp.integration.ollama_provider import OllamaProvider
    OLLAMA_PROVIDER_AVAILABLE = True
except ImportError:
    logger.warning("OllamaProvider not available. Using placeholder class.")
    OLLAMA_PROVIDER_AVAILABLE = False
    
    # Create placeholder class if OllamaProvider is not installed
    class OllamaProvider:
        def __init__(self, model="", remote=False):
            self.model = model
            self.remote = remote
            
        def generate(self, prompt):
            return f"OllamaProvider not available. This is a placeholder response for prompt: {prompt[:50]}..."


class DreamTeam:
    """
    Manages a team of AI agents for collaborative problem-solving and learning.
    
    This class creates and coordinates a team consisting of:
    - A lead instruction-following model
    - Specialized expert models
    - A base model that learns over time
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the dream team.
        
        Args:
            config: Configuration dictionary with settings for the team
        """
        self.config = config
        self.lead_model = self._create_lead_model()
        self.expert_models = self._create_expert_models()
        self.base_model = self._create_base_model()
        self.crew = self._create_crew()
        
        logger.info(f"Dream team initialized with {len(self.expert_models)} expert models")
    
    def _create_lead_model(self) -> Agent:
        """Create the lead instruction-following model."""
        model_name = self.config.get("lead_model", "llama4-scout-instruct")
        remote = self.config.get("remote_lead_model", True)
        
        llm = OllamaProvider(model=model_name, remote=remote)
        
        return Agent(
            role="Lead Coordinator",
            goal="Coordinate the team to solve complex problems",
            backstory="You are an expert at breaking down problems and coordinating specialists",
            llm=llm
        )
    
    def _create_expert_models(self) -> List[Agent]:
        """Create specialized expert models."""
        experts = []
        
        # Resource expert
        experts.append(Agent(
            role="Resource Specialist",
            goal="Find and analyze social service resources",
            backstory="You are an expert at identifying and categorizing resources",
            llm=OllamaProvider(
                model=self.config.get("expert_model", "llama4-scout-instruct"), 
                remote=self.config.get("remote_expert_models", True)
            )
        ))
        
        # Search expert
        experts.append(Agent(
            role="Search Specialist",
            goal="Find relevant information using search techniques",
            backstory="You are an expert at searching and retrieving information",
            llm=OllamaProvider(
                model=self.config.get("expert_model", "llama4-scout-instruct"), 
                remote=self.config.get("remote_expert_models", True)
            )
        ))
        
        # Recommendation expert
        experts.append(Agent(
            role="Recommendation Specialist",
            goal="Recommend resources based on user needs",
            backstory="You are an expert at matching resources to user requirements",
            llm=OllamaProvider(
                model=self.config.get("expert_model", "llama4-scout-instruct"), 
                remote=self.config.get("remote_expert_models", True)
            )
        ))
        
        return experts
    
    def _create_base_model(self) -> Agent:
        """Create the base model that will learn over time."""
        return Agent(
            role="Learning Assistant",
            goal="Assist the team while learning from experiences",
            backstory="You are a flexible learner that improves over time",
            llm=OllamaProvider(
                model=self.config.get("base_model", "llama3"), 
                remote=self.config.get("remote_base_model", False)
            )
        )
    
    def _create_crew(self) -> Crew:
        """Create the CrewAI crew with all agents."""
        all_agents = [self.lead_model] + self.expert_models + [self.base_model]
        return Crew(agents=all_agents)
    
    def solve_task(self, task_description: str) -> str:
        """
        Use the crew to solve a user-provided task.
        
        Args:
            task_description: Description of the task to solve
            
        Returns:
            The solution to the task
        """
        logger.info(f"Solving task: {task_description[:50]}...")
        
        task = Task(description=task_description, agent=self.lead_model)
        
        try:
            result = self.crew.kickoff(tasks=[task])
            logger.info("Task completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error solving task: {str(e)}")
            return f"Error solving task: {str(e)}"
    
    def get_base_solution(self, task_description: str) -> str:
        """
        Get a solution from just the base model.
        
        Args:
            task_description: Description of the task to solve
            
        Returns:
            The base model's solution to the task
        """
        logger.info(f"Getting base model solution for: {task_description[:50]}...")
        
        try:
            if hasattr(self.base_model.llm, 'generate'):
                return self.base_model.llm.generate(task_description)
            else:
                return "Base model does not support direct generation"
        except Exception as e:
            logger.error(f"Error getting base solution: {str(e)}")
            return f"Error getting base solution: {str(e)}"
    
    def get_expert_solution(self, task_description: str, expert_index: int = 0) -> str:
        """
        Get a solution from a specific expert model.
        
        Args:
            task_description: Description of the task to solve
            expert_index: Index of the expert to use
            
        Returns:
            The expert model's solution to the task
        """
        if expert_index >= len(self.expert_models):
            logger.error(f"Expert index {expert_index} out of range")
            return f"Error: Expert index {expert_index} out of range"
        
        expert = self.expert_models[expert_index]
        logger.info(f"Getting solution from expert '{expert.role}' for: {task_description[:50]}...")
        
        try:
            if hasattr(expert.llm, 'generate'):
                return expert.llm.generate(task_description)
            else:
                return "Expert model does not support direct generation"
        except Exception as e:
            logger.error(f"Error getting expert solution: {str(e)}")
            return f"Error getting expert solution: {str(e)}"
