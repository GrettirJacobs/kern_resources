"""
Dream-time task generation for the Dream Lab module.
"""

import random
import logging
from datetime import datetime
from typing import Dict, List, Any

# Set up logging
logger = logging.getLogger(__name__)

class DreamGenerator:
    """
    Generates exploratory tasks during system downtime.
    
    This class creates "dream-like" tasks for the AI to explore during periods
    of low activity, encouraging creative thinking and knowledge integration.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the dream generator.
        
        Args:
            config: Configuration dictionary with settings for the generator
        """
        self.config = config
        
        # Default task templates
        self.task_templates = config.get("task_templates", [
            "Imagine a new type of social service resource that doesn't exist yet. Describe it in detail.",
            "Consider a complex case where a client needs multiple types of resources. How would you approach it?",
            "Explore connections between {resource_type1} and {resource_type2} that might not be obvious.",
            "Develop a new categorization system for resources that might be more intuitive for users.",
            "Imagine you're explaining {resource_type1} resources to someone who has never used social services before. How would you do it?",
            "What are potential gaps in the current social service system for {demographic_group}?",
            "How might {resource_type1} services be improved to better serve {demographic_group}?",
            "Design an ideal workflow for connecting clients to {resource_type1} resources.",
            "What emerging trends might affect how {resource_type1} resources are delivered in the next 5 years?",
            "How could technology improve access to {resource_type1} resources for {demographic_group}?"
        ])
        
        # Resource types
        self.resource_types = config.get("resource_types", [
            "housing", "food", "healthcare", "education", "employment", 
            "legal", "mental health", "transportation", "childcare", 
            "financial assistance", "substance abuse", "senior services"
        ])
        
        # Demographic groups
        self.demographic_groups = config.get("demographic_groups", [
            "seniors", "children", "single parents", "immigrants", 
            "people with disabilities", "veterans", "low-income families",
            "rural residents", "homeless individuals", "LGBTQ+ community"
        ])
        
        logger.info(f"Dream generator initialized with {len(self.task_templates)} task templates")
    
    def generate_dream_task(self) -> Dict[str, Any]:
        """
        Generate a random exploratory task.
        
        Returns:
            A dictionary containing the task description and metadata
        """
        template = random.choice(self.task_templates)
        
        # Fill in template variables if needed
        if "{resource_type1}" in template:
            resource_type1 = random.choice(self.resource_types)
            template = template.replace("{resource_type1}", resource_type1)
            
        if "{resource_type2}" in template:
            # Ensure we pick a different resource type
            resource_type2 = random.choice([rt for rt in self.resource_types if rt != resource_type1])
            template = template.replace("{resource_type2}", resource_type2)
            
        if "{demographic_group}" in template:
            demographic_group = random.choice(self.demographic_groups)
            template = template.replace("{demographic_group}", demographic_group)
            
        # Add timestamp for tracking
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        task = {
            "task": template,
            "timestamp": timestamp,
            "type": "dream_exploration",
            "metadata": {
                "resource_types": [resource_type1, resource_type2] if "{resource_type1}" in template and "{resource_type2}" in template else 
                                 [resource_type1] if "{resource_type1}" in template else [],
                "demographic_group": demographic_group if "{demographic_group}" in template else None
            }
        }
        
        logger.info(f"Generated dream task: {task['task'][:50]}...")
        return task
    
    def generate_batch(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate a batch of dream tasks.
        
        Args:
            count: Number of tasks to generate
            
        Returns:
            A list of task dictionaries
        """
        logger.info(f"Generating batch of {count} dream tasks")
        return [self.generate_dream_task() for _ in range(count)]
    
    def generate_focused_task(self, focus_area: str) -> Dict[str, Any]:
        """
        Generate a task focused on a specific area.
        
        Args:
            focus_area: The area to focus on (e.g., "housing", "seniors")
            
        Returns:
            A task dictionary focused on the specified area
        """
        logger.info(f"Generating focused dream task for area: {focus_area}")
        
        # Check if focus area is a resource type
        if focus_area in self.resource_types:
            templates = [t for t in self.task_templates if "{resource_type1}" in t]
            if not templates:
                templates = self.task_templates
                
            template = random.choice(templates)
            template = template.replace("{resource_type1}", focus_area)
            
            # Replace other variables if needed
            if "{resource_type2}" in template:
                resource_type2 = random.choice([rt for rt in self.resource_types if rt != focus_area])
                template = template.replace("{resource_type2}", resource_type2)
                
            if "{demographic_group}" in template:
                demographic_group = random.choice(self.demographic_groups)
                template = template.replace("{demographic_group}", demographic_group)
                
        # Check if focus area is a demographic group
        elif focus_area in self.demographic_groups:
            templates = [t for t in self.task_templates if "{demographic_group}" in t]
            if not templates:
                templates = self.task_templates
                
            template = random.choice(templates)
            template = template.replace("{demographic_group}", focus_area)
            
            # Replace other variables if needed
            if "{resource_type1}" in template:
                resource_type1 = random.choice(self.resource_types)
                template = template.replace("{resource_type1}", resource_type1)
                
            if "{resource_type2}" in template:
                resource_type2 = random.choice([rt for rt in self.resource_types if rt != resource_type1])
                template = template.replace("{resource_type2}", resource_type2)
                
        # If focus area is neither, create a custom task
        else:
            template = f"Explore how {focus_area} relates to social services and resource provision. What insights can you generate?"
            
        # Add timestamp for tracking
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "task": template,
            "timestamp": timestamp,
            "type": "focused_dream_exploration",
            "focus_area": focus_area
        }
