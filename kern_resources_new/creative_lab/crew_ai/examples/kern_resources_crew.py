"""
Kern Resources CrewAI Example with GroqCloud.

This script demonstrates how to use the GroqCloud provider with CrewAI
to create a crew of agents for the Kern Resources project. The crew
includes agents for resource discovery, analysis, and recommendation.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the providers module
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from .env file
load_dotenv()

# Import the GroqCloud provider
from providers.groq_provider import GroqCloudProvider

# Try to import CrewAI classes, but don't fail if they're not installed
try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tasks.task_output import TaskOutput
    CREWAI_AVAILABLE = True
except ImportError:
    logger.error("CrewAI is not installed. Please install it with 'pip install crewai'.")
    sys.exit(1)

class KernResourcesCrew:
    """
    A crew of agents for the Kern Resources project.
    
    This class creates and manages a crew of agents for resource discovery,
    analysis, and recommendation using the GroqCloud provider.
    """
    
    def __init__(self, api_key=None, model="meta-llama/llama-4-scout-17b-16e-instruct"):
        """
        Initialize the Kern Resources crew.
        
        Args:
            api_key: The API key for GroqCloud. If not provided, it will be read from the GROQ_API_KEY environment variable.
            model: The name of the model to use.
        """
        # Check if the API key is set
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GroqCloud API key not provided and GROQ_API_KEY environment variable not set.")
        
        self.model = model
        logger.info(f"Initializing Kern Resources crew with model: {self.model}")
        
        # Create the GroqCloud provider
        self.llm = GroqCloudProvider(
            api_key=self.api_key,
            model=self.model,
            temperature=0.7
        )
        
        # Create agents
        self.agents = self._create_agents()
        
        # Create the crew
        self.crew = Crew(
            agents=self.agents,
            verbose=2,  # Increased verbosity for more detailed output
            process=Process.sequential  # Run tasks sequentially
        )
    
    def _create_agents(self):
        """Create the agents for the crew."""
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
            llm=self.llm
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
            llm=self.llm
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
            llm=self.llm
        )
        
        return [researcher, analyst, recommender]
    
    def create_tasks(self, resource_type, client_description):
        """
        Create tasks for the crew based on the resource type and client description.
        
        Args:
            resource_type: The type of resource to search for (e.g., "housing", "food", "healthcare").
            client_description: A description of the client's situation and needs.
            
        Returns:
            A list of Task objects.
        """
        # Resource Discovery Task
        discovery_task = Task(
            description=(
                f"Identify and document 3 key resources for {resource_type} assistance in Kern County. "
                f"For each resource, provide the name, description, contact information, and location. "
                f"Focus on resources that would be relevant for a client with the following description: {client_description}"
            ),
            expected_output=f"A list of 3 {resource_type} assistance resources with details",
            agent=self.agents[0]  # Researcher
        )
        
        # Resource Analysis Task
        analysis_task = Task(
            description=(
                f"Analyze the eligibility criteria and application process for each of the "
                f"{resource_type} assistance resources identified. Determine who qualifies and how to apply. "
                f"Pay special attention to requirements that might be relevant for a client with the following description: {client_description}"
            ),
            expected_output=f"Detailed eligibility and application information for each {resource_type} resource",
            agent=self.agents[1],  # Analyst
            context=[discovery_task]  # This task depends on the discovery task
        )
        
        # Resource Recommendation Task
        recommendation_task = Task(
            description=(
                f"Create a personalized recommendation plan for a client with the following description: {client_description} "
                f"Based on the {resource_type} resources identified and analyzed, recommend the most appropriate options. "
                f"Explain why each recommendation is suitable for this client's specific situation. "
                f"Also provide step-by-step guidance on how the client should proceed to access these resources."
            ),
            expected_output="Personalized resource recommendations with rationale and action steps",
            agent=self.agents[2],  # Recommender
            context=[discovery_task, analysis_task]  # This task depends on both previous tasks
        )
        
        return [discovery_task, analysis_task, recommendation_task]
    
    def run(self, resource_type, client_description):
        """
        Run the crew to find and recommend resources.
        
        Args:
            resource_type: The type of resource to search for (e.g., "housing", "food", "healthcare").
            client_description: A description of the client's situation and needs.
            
        Returns:
            The result of the crew's work.
        """
        logger.info(f"Running Kern Resources crew for {resource_type} resources")
        logger.info(f"Client description: {client_description}")
        
        # Create tasks
        tasks = self.create_tasks(resource_type, client_description)
        
        # Run the crew
        result = self.crew.kickoff(tasks=tasks)
        
        return result


def main():
    """Main function to run the Kern Resources crew example."""
    logger.info("=" * 50)
    logger.info("Kern Resources CrewAI Example with GroqCloud")
    logger.info("=" * 50)
    
    # Resource type and client description
    resource_type = "housing"
    client_description = (
        "A single mother with two children (ages 5 and 8) who recently lost her job "
        "due to company downsizing. She has been living in a month-to-month rental "
        "but can no longer afford the rent. She has some savings but they are running low. "
        "She receives child support inconsistently and is looking for both immediate "
        "housing assistance and longer-term affordable housing options."
    )
    
    try:
        # Create and run the crew
        kern_crew = KernResourcesCrew()
        result = kern_crew.run(resource_type, client_description)
        
        logger.info("=" * 50)
        logger.info("RESULT:")
        logger.info("=" * 50)
        logger.info(result)
        
    except Exception as e:
        logger.error(f"Error running Kern Resources crew: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
