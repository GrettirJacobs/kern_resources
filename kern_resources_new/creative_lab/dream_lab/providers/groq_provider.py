"""
GroqCloud provider for Dream Lab.

This module provides a custom LLM provider that can be used with Dream Lab to run
Llama 4 Scout Instruct through GroqCloud's API.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union

# Set up logging
logger = logging.getLogger(__name__)

class GroqProvider:
    """
    Custom LLM provider for Dream Lab that uses GroqCloud to run Llama 4 models.
    
    This provider allows Dream Lab to use Llama 4 models through GroqCloud's API,
    which offers cost-effective inference for these models.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: int = 60
    ):
        """
        Initialize the GroqCloud provider.
        
        Args:
            api_key: The API key for GroqCloud. If not provided, it will be read from the GROQ_API_KEY environment variable.
            model: The name of the model to use.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            timeout: The timeout for API requests in seconds.
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GroqCloud API key not provided and GROQ_API_KEY environment variable not set.")
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        logger.info(f"Initialized GroqProvider with model: {self.model}")
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response based on a list of chat messages.
        
        Args:
            messages: A list of message dictionaries with 'role' and 'content'.
            
        Returns:
            The generated response.
        """
        logger.info(f"Generating response with GroqCloud for {len(messages)} messages")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                response_json = response.json()
                return response_json["choices"][0]["message"]["content"]
            else:
                error_msg = f"GroqCloud API returned status code {response.status_code}: {response.text}"
                logger.error(error_msg)
                return f"Error: {error_msg}"
        except requests.RequestException as e:
            error_msg = f"Failed to communicate with GroqCloud API: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    def generate(self, prompt: str) -> str:
        """
        Generate text based on the prompt.
        
        Args:
            prompt: The prompt to generate text from.
            
        Returns:
            The generated text.
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages)
    
    def get_model_name(self) -> str:
        """Get the name of the model being used."""
        return self.model
