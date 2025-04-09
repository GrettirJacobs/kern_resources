"""
Environment variable management for the Kern Resources project.

This module provides secure handling of environment variables, including
API keys and other sensitive information.
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# Try to import dotenv, but don't fail if it's not installed
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    logger.warning("python-dotenv not installed. Using os.environ only.")
    DOTENV_AVAILABLE = False

class EnvManager:
    """
    Secure management of environment variables.
    
    This class provides methods for loading and accessing environment variables,
    with a focus on secure handling of API keys and other sensitive information.
    """
    
    def __init__(self, env_file: Optional[str] = None, auto_load: bool = True):
        """
        Initialize the environment manager.
        
        Args:
            env_file: Path to the .env file. If None, will look for .env in the current directory.
            auto_load: Whether to automatically load environment variables from the .env file.
        """
        self.env_file = env_file
        
        # Load environment variables if auto_load is True
        if auto_load:
            self.load_env()
    
    def load_env(self) -> bool:
        """
        Load environment variables from the .env file.
        
        Returns:
            True if environment variables were loaded successfully, False otherwise.
        """
        if not DOTENV_AVAILABLE:
            logger.warning("python-dotenv not installed. Cannot load .env file.")
            return False
        
        # If env_file is not specified, look for .env in the current directory
        if self.env_file is None:
            # Try to find .env in the current directory or parent directories
            current_dir = Path.cwd()
            env_path = current_dir / ".env"
            
            # If not found, try parent directories
            if not env_path.exists():
                for parent in current_dir.parents:
                    env_path = parent / ".env"
                    if env_path.exists():
                        break
            
            self.env_file = str(env_path) if env_path.exists() else None
        
        # Load environment variables from the .env file
        if self.env_file and Path(self.env_file).exists():
            load_dotenv(self.env_file)
            logger.info(f"Loaded environment variables from {self.env_file}")
            return True
        else:
            logger.warning(f"Environment file not found: {self.env_file}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get an environment variable.
        
        Args:
            key: The name of the environment variable.
            default: The default value to return if the environment variable is not set.
            
        Returns:
            The value of the environment variable, or the default value if not set.
        """
        return os.environ.get(key, default)
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get an API key for a specific service.
        
        Args:
            service: The name of the service (e.g., "GROQ", "OPENAI", "ANTHROPIC").
            
        Returns:
            The API key for the service, or None if not set.
        """
        key_name = f"{service.upper()}_API_KEY"
        api_key = self.get(key_name)
        
        if not api_key:
            logger.warning(f"API key for {service} not found in environment variables.")
            return None
        
        # Log a masked version of the API key for debugging
        masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
        logger.debug(f"Using {service} API key: {masked_key}")
        
        return api_key
    
    def get_model(self, service: str) -> Optional[str]:
        """
        Get the model name for a specific service.
        
        Args:
            service: The name of the service (e.g., "GROQ", "OPENAI", "ANTHROPIC").
            
        Returns:
            The model name for the service, or None if not set.
        """
        key_name = f"{service.upper()}_MODEL"
        model = self.get(key_name)
        
        if not model:
            logger.warning(f"Model for {service} not found in environment variables.")
            return None
        
        logger.debug(f"Using {service} model: {model}")
        
        return model
    
    def get_all(self) -> Dict[str, str]:
        """
        Get all environment variables.
        
        Returns:
            A dictionary of all environment variables.
        """
        return dict(os.environ)
    
    def is_api_key_set(self, service: str) -> bool:
        """
        Check if an API key is set for a specific service.
        
        Args:
            service: The name of the service (e.g., "GROQ", "OPENAI", "ANTHROPIC").
            
        Returns:
            True if the API key is set, False otherwise.
        """
        key_name = f"{service.upper()}_API_KEY"
        return key_name in os.environ and os.environ[key_name] != ""


# Create a singleton instance for easy access
env_manager = EnvManager(auto_load=True)

# Example usage
if __name__ == "__main__":
    # Set up logging for the example
    logging.basicConfig(level=logging.INFO)
    
    # Get the GroqCloud API key
    groq_api_key = env_manager.get_api_key("GROQ")
    if groq_api_key:
        print(f"GroqCloud API key found: {groq_api_key[:4]}...{groq_api_key[-4:]}")
    else:
        print("GroqCloud API key not found.")
    
    # Get the GroqCloud model
    groq_model = env_manager.get_model("GROQ")
    if groq_model:
        print(f"GroqCloud model: {groq_model}")
    else:
        print("GroqCloud model not found.")
