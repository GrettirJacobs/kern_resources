"""
Simple example of using the CrewAI integration module.

This script demonstrates how to use the CrewAI integration module
to create and run a simple crew for the Kern Resources project.
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

# Add the parent directory to the path so we can import the integration module
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from .env file
load_dotenv()

# Import the CrewAI integration
from integration import create_default_integration

def main():
    """Main function to run the simple integration example."""
    logger.info("=" * 50)
    logger.info("Simple CrewAI Integration Example")
    logger.info("=" * 50)
    
    # Create the integration
    integration = create_default_integration()
    
    # Create agents
    researcher = integration.create_agent(
        role="Resource Researcher",
        goal="Find information about mental health resources in Kern County",
        backstory="You are an expert at finding and documenting mental health resources."
    )
    
    analyst = integration.create_agent(
        role="Resource Analyst",
        goal="Analyze mental health resources for accessibility and effectiveness",
        backstory="You are skilled at evaluating mental health services and their accessibility."
    )
    
    # Create tasks
    research_task = integration.create_task(
        description="Identify 3 mental health resources in Kern County that offer services for teenagers.",
        agent=researcher,
        expected_output="A list of 3 mental health resources for teenagers with details"
    )
    
    analysis_task = integration.create_task(
        description="Analyze the accessibility and effectiveness of the identified mental health resources for teenagers.",
        agent=analyst,
        expected_output="Analysis of accessibility and effectiveness",
        context=[research_task]
    )
    
    # Create crew
    crew = integration.create_crew(
        agents=[researcher, analyst],
        process="sequential",
        verbose=2
    )
    
    # Run crew
    logger.info("Running crew...")
    result = integration.run_crew(crew, tasks=[research_task, analysis_task])
    
    logger.info("=" * 50)
    logger.info("RESULT:")
    logger.info("=" * 50)
    logger.info(result)

if __name__ == "__main__":
    main()
