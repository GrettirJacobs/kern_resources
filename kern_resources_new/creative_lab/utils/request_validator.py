"""
Request validation for the Kern Resources project.

This module provides functions for validating API requests and parameters,
ensuring that inputs are properly sanitized and validated before processing.
"""

import re
import logging
import json
from typing import Dict, List, Any, Optional, Union, Callable, Type

# Set up logging
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass

class RequestValidator:
    """
    Validator for API requests and parameters.
    
    This class provides methods for validating API requests and parameters,
    ensuring that inputs are properly sanitized and validated before processing.
    """
    
    def __init__(self):
        """Initialize the request validator."""
        pass
    
    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate an API key.
        
        Args:
            api_key: The API key to validate.
            
        Returns:
            True if the API key is valid, False otherwise.
            
        Raises:
            ValidationError: If the API key is invalid.
        """
        if not api_key:
            raise ValidationError("API key is required.")
        
        # Check if the API key has a valid format
        # This is a simple check that can be enhanced for specific API key formats
        if len(api_key) < 8:
            raise ValidationError("API key is too short.")
        
        # For GroqCloud API keys, they typically start with "gsk_"
        if api_key.startswith("gsk_"):
            # Additional validation for GroqCloud API keys
            if not re.match(r"^gsk_[A-Za-z0-9]{32,}$", api_key):
                raise ValidationError("Invalid GroqCloud API key format.")
        
        # For OpenAI API keys, they typically start with "sk-"
        elif api_key.startswith("sk-"):
            # Additional validation for OpenAI API keys
            if not re.match(r"^sk-[A-Za-z0-9]{32,}$", api_key):
                raise ValidationError("Invalid OpenAI API key format.")
        
        # For Anthropic API keys, they typically start with "sk-ant-"
        elif api_key.startswith("sk-ant-"):
            # Additional validation for Anthropic API keys
            if not re.match(r"^sk-ant-[A-Za-z0-9]{32,}$", api_key):
                raise ValidationError("Invalid Anthropic API key format.")
        
        # For other API keys, just check that they're not obviously invalid
        else:
            if re.search(r"[^A-Za-z0-9_\-\.]", api_key):
                raise ValidationError("API key contains invalid characters.")
        
        return True
    
    def validate_model_name(self, model_name: str, provider: str = None) -> bool:
        """
        Validate a model name.
        
        Args:
            model_name: The model name to validate.
            provider: The provider of the model (e.g., "GROQ", "OPENAI", "ANTHROPIC").
            
        Returns:
            True if the model name is valid, False otherwise.
            
        Raises:
            ValidationError: If the model name is invalid.
        """
        if not model_name:
            raise ValidationError("Model name is required.")
        
        # Check if the model name has a valid format
        if re.search(r"[^A-Za-z0-9_\-\./]", model_name):
            raise ValidationError("Model name contains invalid characters.")
        
        # Validate model names for specific providers
        if provider:
            provider = provider.upper()
            
            if provider == "GROQ":
                # GroqCloud model names typically start with "meta-llama/"
                if not model_name.startswith("meta-llama/"):
                    logger.warning(f"Unusual GroqCloud model name: {model_name}")
            
            elif provider == "OPENAI":
                # OpenAI model names typically start with "gpt-"
                if not model_name.startswith("gpt-"):
                    logger.warning(f"Unusual OpenAI model name: {model_name}")
            
            elif provider == "ANTHROPIC":
                # Anthropic model names typically start with "claude-"
                if not model_name.startswith("claude-"):
                    logger.warning(f"Unusual Anthropic model name: {model_name}")
        
        return True
    
    def validate_temperature(self, temperature: float) -> bool:
        """
        Validate a temperature parameter.
        
        Args:
            temperature: The temperature parameter to validate.
            
        Returns:
            True if the temperature is valid, False otherwise.
            
        Raises:
            ValidationError: If the temperature is invalid.
        """
        if not isinstance(temperature, (int, float)):
            raise ValidationError("Temperature must be a number.")
        
        if temperature < 0 or temperature > 2:
            raise ValidationError("Temperature must be between 0 and 2.")
        
        return True
    
    def validate_max_tokens(self, max_tokens: int) -> bool:
        """
        Validate a max_tokens parameter.
        
        Args:
            max_tokens: The max_tokens parameter to validate.
            
        Returns:
            True if the max_tokens is valid, False otherwise.
            
        Raises:
            ValidationError: If the max_tokens is invalid.
        """
        if not isinstance(max_tokens, int):
            raise ValidationError("max_tokens must be an integer.")
        
        if max_tokens < 1:
            raise ValidationError("max_tokens must be at least 1.")
        
        if max_tokens > 32768:
            raise ValidationError("max_tokens must be at most 32768.")
        
        return True
    
    def validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        """
        Validate a messages parameter for chat completions.
        
        Args:
            messages: The messages parameter to validate.
            
        Returns:
            True if the messages are valid, False otherwise.
            
        Raises:
            ValidationError: If the messages are invalid.
        """
        if not isinstance(messages, list):
            raise ValidationError("messages must be a list.")
        
        if not messages:
            raise ValidationError("messages must not be empty.")
        
        for message in messages:
            if not isinstance(message, dict):
                raise ValidationError("Each message must be a dictionary.")
            
            if "role" not in message:
                raise ValidationError("Each message must have a 'role' field.")
            
            if "content" not in message:
                raise ValidationError("Each message must have a 'content' field.")
            
            if message["role"] not in ["system", "user", "assistant"]:
                raise ValidationError("Message role must be 'system', 'user', or 'assistant'.")
            
            if not isinstance(message["content"], str):
                raise ValidationError("Message content must be a string.")
        
        return True
    
    def validate_prompt(self, prompt: str) -> bool:
        """
        Validate a prompt parameter for completions.
        
        Args:
            prompt: The prompt parameter to validate.
            
        Returns:
            True if the prompt is valid, False otherwise.
            
        Raises:
            ValidationError: If the prompt is invalid.
        """
        if not isinstance(prompt, str):
            raise ValidationError("prompt must be a string.")
        
        if not prompt:
            raise ValidationError("prompt must not be empty.")
        
        # Check for potential injection attacks
        if "```" in prompt and ("import os" in prompt or "subprocess" in prompt):
            logger.warning("Prompt contains potentially dangerous code blocks.")
        
        return True
    
    def validate_chat_request(self, request: Dict[str, Any]) -> bool:
        """
        Validate a chat completion request.
        
        Args:
            request: The request to validate.
            
        Returns:
            True if the request is valid, False otherwise.
            
        Raises:
            ValidationError: If the request is invalid.
        """
        required_fields = ["model", "messages"]
        for field in required_fields:
            if field not in request:
                raise ValidationError(f"Request must include '{field}'.")
        
        # Validate model
        self.validate_model_name(request["model"])
        
        # Validate messages
        self.validate_messages(request["messages"])
        
        # Validate optional parameters
        if "temperature" in request:
            self.validate_temperature(request["temperature"])
        
        if "max_tokens" in request:
            self.validate_max_tokens(request["max_tokens"])
        
        return True
    
    def validate_completion_request(self, request: Dict[str, Any]) -> bool:
        """
        Validate a completion request.
        
        Args:
            request: The request to validate.
            
        Returns:
            True if the request is valid, False otherwise.
            
        Raises:
            ValidationError: If the request is invalid.
        """
        required_fields = ["model", "prompt"]
        for field in required_fields:
            if field not in request:
                raise ValidationError(f"Request must include '{field}'.")
        
        # Validate model
        self.validate_model_name(request["model"])
        
        # Validate prompt
        self.validate_prompt(request["prompt"])
        
        # Validate optional parameters
        if "temperature" in request:
            self.validate_temperature(request["temperature"])
        
        if "max_tokens" in request:
            self.validate_max_tokens(request["max_tokens"])
        
        return True
    
    def sanitize_input(self, input_str: str) -> str:
        """
        Sanitize an input string.
        
        Args:
            input_str: The input string to sanitize.
            
        Returns:
            The sanitized input string.
        """
        if not isinstance(input_str, str):
            return str(input_str)
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r"[^\w\s\.,;:!?'\"\-\(\)\[\]\{\}]", "", input_str)
        
        return sanitized


# Create a singleton instance for easy access
request_validator = RequestValidator()

# Example usage
if __name__ == "__main__":
    # Set up logging for the example
    logging.basicConfig(level=logging.INFO)
    
    # Test API key validation
    try:
        api_key = "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"
        request_validator.validate_api_key(api_key)
        logger.info("API key validation passed.")
    except ValidationError as e:
        logger.error(f"API key validation failed: {e}")
    
    # Test model name validation
    try:
        model_name = "meta-llama/llama-4-scout-17b-16e-instruct"
        request_validator.validate_model_name(model_name, "GROQ")
        logger.info("Model name validation passed.")
    except ValidationError as e:
        logger.error(f"Model name validation failed: {e}")
    
    # Test chat request validation
    try:
        request = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, world!"}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        request_validator.validate_chat_request(request)
        logger.info("Chat request validation passed.")
    except ValidationError as e:
        logger.error(f"Chat request validation failed: {e}")
