"""
Example of using Llama 4 Scout Instruct with CrewAI.

This script demonstrates how to use the Llama 4 Scout Instruct model with CrewAI
to create a simple crew of agents that can help with resource discovery and analysis.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the ollama_provider module
sys.path.append(str(Path(__file__).parent))

# Try to import CrewAI classes, but don't fail if they're not installed
try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tasks.task_output import TaskOutput
    CREWAI_AVAILABLE = True
except ImportError:
    print("CrewAI is not installed. Please install it with 'pip install crewai'.")
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
    class TaskOutput:
        pass

# Import the OllamaProvider
from ollama_provider import OllamaProvider

def create_agents(llm) -> list:
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

def create_tasks(agents) -> list:
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
    """Main function to run the CrewAI example."""
    if not CREWAI_AVAILABLE:
        print("This example requires CrewAI to be installed.")
        print("Please install it with: pip install crewai")
        return
    
    print("=" * 50)
    print("Llama 4 Scout Instruct with CrewAI Example")
    print("=" * 50)
    
    # Find the model_info.json file
    script_dir = Path(__file__).parent.parent
    model_info_path = script_dir / "models" / "model_info.json"
    
    # Create the Ollama provider
    if model_info_path.exists():
        llm = OllamaProvider(model_info_path=str(model_info_path))
        print(f"Using model: {llm.get_model_name()}")
    else:
        print("Model info not found. Using default configuration.")
        llm = OllamaProvider()
    
    # Create agents
    print("\nCreating agents...")
    agents = create_agents(llm)
    
    # Create tasks
    print("Creating tasks...")
    tasks = create_tasks(agents)
    
    # Create and run the crew
    print("Creating crew...")
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=2,  # Increased verbosity for more detailed output
        process=Process.sequential  # Run tasks sequentially
    )
    
    print("\nRunning crew to find and analyze food assistance resources...")
    result = crew.kickoff()
    
    print("\n" + "=" * 50)
    print("RESULT:")
    print("=" * 50)
    print(result)

if __name__ == "__main__":
    main()
