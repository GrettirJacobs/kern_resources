"""
Example of using GroqCloud with Dream Lab.

This script demonstrates how to use the GroqCloud provider with Dream Lab
to create a dream session that explores creative ideas for social services.
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

# Add the parent directory to the path so we can import the Dream Lab modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Load environment variables from .env file
load_dotenv()

# Import Dream Lab modules
try:
    from dream_lab.agents.team import DreamTeam
    from dream_lab.exploration.dream_generator import DreamGenerator
    from dream_lab.memory.reflection import MemorySystem
    from dream_lab.training.fine_tuner import BaseLearner
    from dream_lab.orchestration.scheduler import DreamScheduler
    from dream_lab.providers.groq_provider import GroqProvider
    DREAM_LAB_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import Dream Lab modules: {e}")
    DREAM_LAB_AVAILABLE = False
    sys.exit(1)

def main():
    """Main function to run the Dream Lab example with GroqCloud."""
    logger.info("=" * 50)
    logger.info("Dream Lab with GroqCloud Example")
    logger.info("=" * 50)
    
    # Check if the API key is set
    if not os.environ.get("GROQ_API_KEY"):
        logger.error("GROQ_API_KEY environment variable not set.")
        logger.error("Please set it before running this example.")
        logger.error("Example: export GROQ_API_KEY=your_api_key_here")
        return
    
    # Create configuration
    config = {
        "memory_path": "data/dream_lab/memories",
        "training_data_path": "data/dream_lab/training",
        "dream_time": "02:00",
        "dream_duration": 30,  # 30 minutes
        "dream_task_count": 2,  # 2 tasks per session
        "resource_types": [
            "housing", "food", "healthcare", "education", "employment", 
            "legal", "mental health", "transportation", "childcare"
        ],
        "demographic_groups": [
            "seniors", "children", "single parents", "immigrants", 
            "people with disabilities", "veterans", "low-income families"
        ]
    }
    
    # Create directories if they don't exist
    os.makedirs(config["memory_path"], exist_ok=True)
    os.makedirs(config["training_data_path"], exist_ok=True)
    
    # Create GroqCloud providers
    lead_model_provider = GroqProvider(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0.7
    )
    
    base_model_provider = GroqProvider(
        model="meta-llama/llama-4-scout-8b-16e-instruct",
        temperature=0.8
    )
    
    # Create Dream Lab components
    logger.info("Creating Dream Lab components...")
    
    # Create Dream Team with GroqCloud providers
    dream_team = DreamTeam(config)
    
    # Replace the default providers with GroqCloud providers
    dream_team.lead_model.llm = lead_model_provider
    dream_team.base_model.llm = base_model_provider
    for agent in dream_team.expert_models:
        agent.llm = lead_model_provider
    
    # Create other components
    dream_generator = DreamGenerator(config)
    memory_system = MemorySystem(config)
    base_learner = BaseLearner(config, dream_team.base_model)
    
    # Create scheduler
    dream_scheduler = DreamScheduler(
        config,
        dream_team,
        dream_generator,
        memory_system,
        base_learner
    )
    
    # Run a manual dream session
    logger.info("Starting a manual dream session...")
    dream_scheduler.start_dream_session()
    
    logger.info("Dream session completed!")

if __name__ == "__main__":
    main()
