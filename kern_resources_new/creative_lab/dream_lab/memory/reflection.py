"""
Memory and reflection system for the Dream Lab module.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Set up logging
logger = logging.getLogger(__name__)

class MemorySystem:
    """
    Stores and processes experiences and reflections.
    
    This class manages the memory system for the Dream Lab, storing experiences,
    generating reflections, and retrieving relevant memories.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the memory system.
        
        Args:
            config: Configuration dictionary with settings for the memory system
        """
        self.config = config
        self.memory_path = config.get("memory_path", "data/dream_lab/memories")
        
        # Create memory directory if it doesn't exist
        os.makedirs(self.memory_path, exist_ok=True)
        
        logger.info(f"Memory system initialized with path: {self.memory_path}")
    
    def store_experience(self, task: str, result: str, agent_id: str) -> str:
        """
        Store an experience in the memory system.
        
        Args:
            task: The task that was performed
            result: The result of the task
            agent_id: Identifier for the agent that performed the task
            
        Returns:
            The filename where the memory was stored
        """
        memory = {
            "task": task,
            "result": result,
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "reflections": []
        }
        
        # Generate a unique filename
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{agent_id}.json"
        file_path = os.path.join(self.memory_path, filename)
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(memory, f, indent=2)
        
        logger.info(f"Stored experience in {filename}")
        return filename
    
    def generate_reflection(self, memory_id: str, reflection_agent: Any) -> str:
        """
        Generate a reflection on a stored memory.
        
        Args:
            memory_id: The filename of the memory to reflect on
            reflection_agent: The agent to use for generating the reflection
            
        Returns:
            The generated reflection
        """
        # Load the memory
        file_path = os.path.join(self.memory_path, memory_id)
        
        try:
            with open(file_path, 'r') as f:
                memory = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading memory {memory_id}: {str(e)}")
            return f"Error loading memory: {str(e)}"
        
        # Create reflection prompt
        prompt = f"""
        Review this experience and reflect on it:
        
        Task: {memory['task']}
        Result: {memory['result']}
        
        Please reflect on:
        1. What went well in this solution?
        2. What could be improved?
        3. What new insights or patterns do you notice?
        4. How might this inform future approaches?
        """
        
        # Get reflection from agent
        try:
            if hasattr(reflection_agent, 'llm') and hasattr(reflection_agent.llm, 'generate'):
                reflection = reflection_agent.llm.generate(prompt)
            elif hasattr(reflection_agent, 'generate'):
                reflection = reflection_agent.generate(prompt)
            else:
                logger.warning("Reflection agent doesn't support generation, using placeholder")
                reflection = f"Placeholder reflection for memory {memory_id}"
        except Exception as e:
            logger.error(f"Error generating reflection: {str(e)}")
            reflection = f"Error generating reflection: {str(e)}"
        
        # Store reflection
        memory["reflections"].append({
            "content": reflection,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save updated memory
        with open(file_path, 'w') as f:
            json.dump(memory, f, indent=2)
        
        logger.info(f"Generated reflection for memory {memory_id}")
        return reflection
    
    def retrieve_relevant_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve memories relevant to a query.
        
        Args:
            query: The query to search for
            limit: Maximum number of memories to return
            
        Returns:
            A list of relevant memories
        """
        logger.info(f"Retrieving memories relevant to: {query[:50]}...")
        
        relevant_memories = []
        query_terms = query.lower().split()
        
        try:
            # Iterate through all memory files
            for filename in os.listdir(self.memory_path):
                if not filename.endswith('.json'):
                    continue
                    
                file_path = os.path.join(self.memory_path, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        memory = json.load(f)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    logger.warning(f"Skipping invalid memory file: {filename}")
                    continue
                
                # Simple relevance check
                content = memory['task'] + ' ' + memory['result']
                content = content.lower()
                
                # Calculate a simple relevance score based on term frequency
                score = sum(1 for term in query_terms if term in content)
                
                if score > 0:
                    memory['relevance_score'] = score
                    memory['filename'] = filename
                    relevant_memories.append(memory)
        except Exception as e:
            logger.error(f"Error retrieving memories: {str(e)}")
        
        # Sort by relevance score and recency
        relevant_memories.sort(key=lambda x: (x['relevance_score'], x['timestamp']), reverse=True)
        
        return relevant_memories[:limit]
    
    def get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: The filename of the memory to retrieve
            
        Returns:
            The memory dictionary, or None if not found
        """
        file_path = os.path.join(self.memory_path, memory_id)
        
        try:
            with open(file_path, 'r') as f:
                memory = json.load(f)
            return memory
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error retrieving memory {memory_id}: {str(e)}")
            return None
    
    def get_all_memories(self, limit: int = 100, sort_by: str = 'timestamp') -> List[Dict[str, Any]]:
        """
        Get all memories, optionally sorted.
        
        Args:
            limit: Maximum number of memories to return
            sort_by: Field to sort by ('timestamp' or 'agent_id')
            
        Returns:
            A list of memories
        """
        memories = []
        
        try:
            for filename in os.listdir(self.memory_path):
                if not filename.endswith('.json'):
                    continue
                    
                file_path = os.path.join(self.memory_path, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        memory = json.load(f)
                    memory['filename'] = filename
                    memories.append(memory)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    logger.warning(f"Skipping invalid memory file: {filename}")
                    continue
        except Exception as e:
            logger.error(f"Error retrieving all memories: {str(e)}")
        
        # Sort memories
        if sort_by == 'timestamp':
            memories.sort(key=lambda x: x['timestamp'], reverse=True)
        elif sort_by == 'agent_id':
            memories.sort(key=lambda x: x['agent_id'])
        
        return memories[:limit]
