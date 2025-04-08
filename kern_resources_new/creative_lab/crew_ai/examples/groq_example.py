"""
Example of using GroqCloud with CrewAI.

This script demonstrates how to use the GroqCloud provider with CrewAI
to create a simple crew of agents that can help with resource discovery and analysis.
"""

import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the providers module
sys.path.append(str(Path(__file__).parent.parent))

# Import the GroqCloud provider
from providers.groq_provider import GroqCloudProvider

# Try to import CrewAI classes, but don't fail if they're not installed
try:
    from crewai import Agent, Task, Crew, Process
    CREWAI_AVAILABLE = True
except ImportError:
    logger.warning("CrewAI is not installed. Please install it with 'pip install crewai'.")
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

def create_agents(llm):
    """
    Create a list of agents for the crew.
    
    Args:
        llm: The language model to use for the agents.
        
    Returns:
        A list of Agent objects.
    """
    # Resource Researcher Agent
    researcher = Agent(
        role="Resource Researcher",
        goal="Discover and document social service resources in Kern County",
        backstory=(
            "You are an expert at finding and analyzing social service resources. "
            "You have extensive knowledge of government programs, non-profit organizations, "
            "and community services. Your mission is to help people find the resources they need."
        ),
        verbose=True,
        llm=llm
    )
    
    # Resource Analyst Agent
    analyst = Agent(
        role="Resource Analyst",
        goal="Analyze resources to determine eligibility criteria and application processes",
        backstory=(
            "You are a detail-oriented analyst with expertise in social service eligibility requirements. "
            "You can quickly identify who qualifies for different programs and what steps they need to take "
            "to apply. Your insights help connect people with the right resources efficiently."
        ),
        verbose=True,
        llm=llm
    )
    
    # Resource Recommender Agent
    recommender = Agent(
        role="Resource Recommender",
        goal="Recommend the most appropriate resources based on client needs",
        backstory=(
            "You are a compassionate advisor with a talent for matching people with the right resources. "
            "You understand that each person's situation is unique and requires personalized recommendations. "
            "Your goal is to ensure that no one falls through the cracks of the social service system."
        ),
        verbose=True,
        llm=llm
    )
    
    return [researcher, analyst, recommender]

def create_tasks(agents):
    """
    Create a list of tasks for the crew.
    
    Args:
        agents: A list of Agent objects.
        
    Returns:
        A list of Task objects.
    """
    # Resource Discovery Task
    discovery_task = Task(
        description=(
            "Identify and document 3 key resources for food assistance in Kern County. "
            "For each resource, provide the name, description, and contact information."
        ),
        expected_output="A list of 3 food assistance resources with details",
        agent=agents[0]  # Researcher
    )
    
    # Resource Analysis Task
    analysis_task = Task(
        description=(
            "Analyze the eligibility criteria and application process for each of the "
            "food assistance resources identified. Determine who qualifies and how to apply."
        ),
        expected_output="Detailed eligibility and application information for each resource",
        agent=agents[1],  # Analyst
        context=[discovery_task]  # This task depends on the discovery task
    )
    
    # Resource Recommendation Task
    recommendation_task = Task(
        description=(
            "Create a recommendation plan for a single mother with two children "
            "who needs food assistance. Based on the resources identified and analyzed, "
            "recommend the most appropriate options and explain why."
        ),
        expected_output="Personalized resource recommendations with rationale",
        agent=agents[2],  # Recommender
        context=[discovery_task, analysis_task]  # This task depends on both previous tasks
    )
    
    return [discovery_task, analysis_task, recommendation_task]

def main():
    """Main function to run the CrewAI example with GroqCloud."""
    if not CREWAI_AVAILABLE:
        logger.error("This example requires CrewAI to be installed.")
        logger.error("Please install it with: pip install crewai")
        return
    
    # Check if the API key is set
    if not os.environ.get("GROQ_API_KEY"):
        logger.error("GROQ_API_KEY environment variable not set.")
        logger.error("Please set it before running this example.")
        logger.error("Example: export GROQ_API_KEY=your_api_key_here")
        return
    
    logger.info("=" * 50)
    logger.info("GroqCloud with CrewAI Example")
    logger.info("=" * 50)
    
    # Create the GroqCloud provider
    llm = GroqCloudProvider(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0.7
    )
    
    # Create agents
    logger.info("Creating agents...")
    agents = create_agents(llm)
    
    # Create tasks
    logger.info("Creating tasks...")
    tasks = create_tasks(agents)
    
    # Create and run the crew
    logger.info("Creating crew...")
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=2,  # Increased verbosity for more detailed output
        process=Process.sequential  # Run tasks sequentially
    )
    
    logger.info("Running crew to find and analyze food assistance resources...")
    result = crew.kickoff()
    
    logger.info("=" * 50)
    logger.info("RESULT:")
    logger.info("=" * 50)
    logger.info(result)

if __name__ == "__main__":
    main()
