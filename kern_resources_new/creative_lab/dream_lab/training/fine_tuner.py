"""
Fine-tuning components for the Dream Lab module.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Set up logging
logger = logging.getLogger(__name__)

class BaseLearner:
    """
    Manages the continuous learning of the base model.
    
    This class collects training examples from team interactions and
    prepares datasets for fine-tuning the base model.
    """
    
    def __init__(self, config: Dict[str, Any], base_model: Any):
        """
        Initialize the base learner.
        
        Args:
            config: Configuration dictionary with settings for the learner
            base_model: The base model agent that will be fine-tuned
        """
        self.config = config
        self.base_model = base_model
        self.training_data_path = config.get("training_data_path", "data/dream_lab/training")
        
        # Create training data directory if it doesn't exist
        os.makedirs(self.training_data_path, exist_ok=True)
        
        logger.info(f"Base learner initialized with path: {self.training_data_path}")
    
    def collect_training_example(self, task: str, expert_solution: str, 
                                base_solution: Optional[str] = None, 
                                quality_score: float = 0.0) -> str:
        """
        Collect a training example from team interactions.
        
        Args:
            task: The task that was performed
            expert_solution: The solution provided by an expert model
            base_solution: The solution provided by the base model (optional)
            quality_score: A score indicating the quality of the expert solution
            
        Returns:
            The filename where the example was stored
        """
        example = {
            "task": task,
            "expert_solution": expert_solution,
            "base_solution": base_solution,
            "quality_score": quality_score,
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate a unique filename
        filename = f"training_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        file_path = os.path.join(self.training_data_path, filename)
        
        # Save to training data
        with open(file_path, 'w') as f:
            json.dump(example, f, indent=2)
        
        logger.info(f"Collected training example in {filename}")
        return filename
    
    def prepare_training_dataset(self, format_type: str = "instruction") -> str:
        """
        Prepare a dataset for fine-tuning from collected examples.
        
        Args:
            format_type: The format to use for the dataset ("instruction", "completion", or "comparison")
            
        Returns:
            The path to the prepared dataset
        """
        logger.info(f"Preparing training dataset in {format_type} format")
        
        examples = []
        
        try:
            # Iterate through all example files
            for filename in os.listdir(self.training_data_path):
                if not filename.endswith('.json') or filename.startswith('dataset_'):
                    continue
                    
                file_path = os.path.join(self.training_data_path, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        example = json.load(f)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    logger.warning(f"Skipping invalid example file: {filename}")
                    continue
                
                # Format based on the specified type
                if format_type == "instruction":
                    formatted_example = {
                        "instruction": example["task"],
                        "input": "",
                        "output": example["expert_solution"]
                    }
                elif format_type == "completion":
                    formatted_example = {
                        "prompt": f"Task: {example['task']}\n\nSolution:",
                        "completion": example["expert_solution"]
                    }
                elif format_type == "comparison":
                    if example.get("base_solution"):
                        formatted_example = {
                            "prompt": example["task"],
                            "chosen": example["expert_solution"],
                            "rejected": example["base_solution"]
                        }
                    else:
                        # Skip examples without base solutions for comparison format
                        continue
                else:
                    logger.error(f"Unknown format type: {format_type}")
                    continue
                
                examples.append(formatted_example)
        except Exception as e:
            logger.error(f"Error preparing dataset: {str(e)}")
        
        if not examples:
            logger.warning("No valid examples found for dataset")
            return ""
        
        # Save formatted dataset
        dataset_path = os.path.join(
            self.training_data_path, 
            f"dataset_{format_type}_{datetime.now().strftime('%Y%m%d')}.json"
        )
        
        with open(dataset_path, 'w') as f:
            json.dump(examples, f, indent=2)
        
        logger.info(f"Prepared dataset with {len(examples)} examples at {dataset_path}")
        return dataset_path
    
    def schedule_fine_tuning(self) -> bool:
        """
        Schedule a fine-tuning job when enough data is collected.
        
        Returns:
            True if fine-tuning was scheduled, False otherwise
        """
        # Check if we have enough examples
        example_count = len([
            f for f in os.listdir(self.training_data_path) 
            if f.endswith('.json') and not f.startswith('dataset_')
        ])
        
        min_examples = self.config.get("min_examples_for_training", 100)
        
        if example_count >= min_examples:
            logger.info(f"Scheduling fine-tuning with {example_count} examples")
            
            # Prepare datasets in different formats
            instruction_dataset = self.prepare_training_dataset("instruction")
            comparison_dataset = self.prepare_training_dataset("comparison")
            
            # In a real implementation, this would launch a fine-tuning job
            # For now, we'll just log that it would happen
            logger.info(f"Would fine-tune base model with instruction dataset: {instruction_dataset}")
            if comparison_dataset:
                logger.info(f"Would also use comparison dataset: {comparison_dataset}")
            
            return True
        else:
            logger.info(f"Not enough examples for fine-tuning yet. Have {example_count}, need {min_examples}")
            return False
    
    def get_training_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collected training data.
        
        Returns:
            A dictionary with statistics about the training data
        """
        stats = {
            "total_examples": 0,
            "examples_with_base_solution": 0,
            "average_quality_score": 0.0,
            "examples_by_date": {},
            "latest_example_timestamp": None
        }
        
        try:
            quality_scores = []
            
            for filename in os.listdir(self.training_data_path):
                if not filename.endswith('.json') or filename.startswith('dataset_'):
                    continue
                    
                file_path = os.path.join(self.training_data_path, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        example = json.load(f)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
                
                stats["total_examples"] += 1
                
                if example.get("base_solution"):
                    stats["examples_with_base_solution"] += 1
                
                if "quality_score" in example:
                    quality_scores.append(example["quality_score"])
                
                # Track examples by date
                date = example.get("timestamp", "").split("T")[0]
                if date:
                    stats["examples_by_date"][date] = stats["examples_by_date"].get(date, 0) + 1
                
                # Track latest example timestamp
                if example.get("timestamp"):
                    if not stats["latest_example_timestamp"] or example["timestamp"] > stats["latest_example_timestamp"]:
                        stats["latest_example_timestamp"] = example["timestamp"]
            
            # Calculate average quality score
            if quality_scores:
                stats["average_quality_score"] = sum(quality_scores) / len(quality_scores)
        except Exception as e:
            logger.error(f"Error getting training stats: {str(e)}")
        
        return stats
